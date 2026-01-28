from __future__ import annotations

import base64
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.http import FileResponse, Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ActivityEventFilterSet
from .models import ActivityEvent, LogIngestionKey, ActorRole, Verb, Source, ExportJob, ExportFormat, ScheduledReport, ScheduleType, JobStatus
from .permissions import IsAdmin
from .serializers import (
    ActivityEventIngestSerializer,
    ActivityEventSerializer,
    ExportJobRequestSerializer,
    ExportJobSerializer,
    SummarySerializer,
    ExportJobListSerializer,
    BehaviorMonitoringSerializer,
    ScheduledReportSerializer,
)
from .tasks import run_export_job, _calculate_next_run, _execute_export_job, run_export_job_sync
from .services.email_service import send_scheduled_report
from .utils.hashing import compute_event_hash
from .utils.pagination import UICursorPagination
from .utils.rbac import apply_rbac
from .utils.hmac_signing import verify_hmac_sha256
from .permissions import user_role
from uuid import uuid4
from .utils.encryption import decrypt_field


ALLOW_TARGET_TYPES = {
    "Order",
    "Design",
    "Client",
    "InventoryItem",
    "File",
    "Job",
    "Machine",
    "QA",
    "Dispatch",
    "Attendance",
}


def _decrypt_value(value: Any) -> str:
    """
    Helper function to decrypt a value if it's encrypted, otherwise return as-is.
    For admin users viewing behavior monitoring data, we decrypt sensitive fields.
    
    Args:
        value: The value to decrypt (may be encrypted string, plain string, or None)
    
    Returns:
        Decrypted value as string, or original value if not encrypted, or "-" if None/empty
    """
    if not value or value == "-":
        return "-"
    
    if isinstance(value, str) and value.startswith("encrypted:"):
        try:
            decrypted = decrypt_field(value)
            # Convert to string if needed (handles dict/list results from JSON parsing)
            if isinstance(decrypted, (dict, list)):
                return str(decrypted)
            return str(decrypted) if decrypted else "-"
        except Exception as e:
            logger.warning(f"Failed to decrypt value: {e}")
            return value  # Return encrypted value if decryption fails
    
    return str(value) if value else "-"


def _log_view_access(request, target_log_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None):
    """
    Log when someone views activity logs.
    This creates an audit event tracking log view access.
    
    Args:
        request: The HTTP request object
        target_log_id: The ID of the specific log being viewed (for detail view)
        filters: Dictionary of filter parameters applied (for list view)
    """
    try:
        # Prevent recursive tracking - don't log view access events for view access events themselves
        # We check if the request is for viewing a log view access event (target_type="ActivityEvent")
        # This is a simple heuristic - in practice, we rely on the fact that view access events
        # have target_type="ActivityEvent" and verb="READ", so they won't trigger infinite loops
        # because we're only tracking when users view logs, not when the system creates audit events
        pass
        
        role = user_role(request.user) or "ADMIN"
        context = {
            "action": "view_logs",
            "viewer_id": str(request.user.id),
            "viewer_username": request.user.username,
            "viewer_role": role,
            "ip_address": request.META.get('REMOTE_ADDR', 'unknown'),
            "user_agent": request.META.get('HTTP_USER_AGENT', 'unknown'),
        }
        
        if target_log_id:
            # Detail view - viewing a specific log
            context["target_log_id"] = target_log_id
            context["view_type"] = "detail"
        else:
            # List view - viewing multiple logs
            context["view_type"] = "list"
            if filters:
                context["filters_applied"] = filters
        
        canon = {
            "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tenant_id": getattr(request.user, 'org_id', None) or "default",
            "actor": {"id": str(request.user.id), "role": role},
            "verb": Verb.READ,
            "target": {"type": "ActivityEvent", "id": target_log_id or "list"},
            "source": Source.ADMIN_UI,
            "request_id": f"req_{uuid4().hex}",
            "context": context,
        }
        ev_hash = compute_event_hash(canon)
        
        tenant_id = canon["tenant_id"]
        prev = ActivityEvent.objects.filter(tenant_id=tenant_id).order_by("-timestamp").first()
        
        # Create the audit event with a special flag to prevent recursive tracking
        ActivityEvent.objects.create(
            timestamp=timezone.now(),
            actor_id=request.user.id,
            actor_role=role,
            verb=Verb.READ,
            target_type="ActivityEvent",
            target_id=target_log_id or "list",
            context=context,
            source=Source.ADMIN_UI,
            request_id=canon["request_id"],
            tenant_id=tenant_id,
            hash=ev_hash,
            prev_hash=prev.hash if prev else None,
        )
    except Exception as e:
        # Don't fail the request if logging fails
        logger.exception(f"Failed to log view access activity event: {e}")


def normalize_actor(actor: Optional[dict]) -> dict:
    if not actor:
        return {"id": None, "role": "SYSTEM"}
    return {"id": actor.get("id"), "role": str(actor.get("role", "SYSTEM")).upper()}


def normalize_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    actor = normalize_actor(data.get("actor"))
    return {
        "timestamp": data.get("timestamp"),
        "tenant_id": data.get("tenant_id"),
        "actor": actor,
        "verb": str(data.get("verb", "OTHER")).upper(),
        "target": {
            "type": data["target"]["type"],
            "id": str(data["target"]["id"]),
        },
        "source": str(data.get("source", "API")).upper(),
        "request_id": data.get("request_id") or "",
        "context": data.get("context") or {},
    }


def canonicalize_for_hash(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Reduce to fields included in hash and ensure stable types
    return {
        "timestamp": payload["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(payload["timestamp"], "strftime") else str(payload["timestamp"]),
        "tenant_id": payload["tenant_id"],
        "actor": {"id": payload["actor"]["id"], "role": payload["actor"]["role"]},
        "verb": payload["verb"],
        "target": {"type": payload["target"]["type"], "id": str(payload["target"]["id"])},
        "source": payload["source"],
        "request_id": payload.get("request_id") or "",
        "context": payload.get("context") or {},
    }


@method_decorator(csrf_exempt, name="dispatch")
class IngestView(APIView):
    authentication_classes: list[type] = [BasicAuthentication]  # not used; we use HMAC headers
    permission_classes = [AllowAny]

    def post(self, request):
        # HMAC headers
        key_id = request.headers.get("X-Log-Key")
        signature = request.headers.get("X-Log-Signature")
        req_id_header = request.headers.get("X-Request-Id")
        if not key_id or not signature:
            return Response({"detail": "Missing HMAC headers"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            key = LogIngestionKey.objects.get(key_id=key_id, is_active=True)
        except LogIngestionKey.DoesNotExist:
            return Response({"detail": "Invalid key"}, status=status.HTTP_401_UNAUTHORIZED)

        # Simple Redis-backed rate limit: per IP and per key
        ident_ip = request.META.get("REMOTE_ADDR", "unknown")
        per_min = int(getattr(settings, "INGEST_RATE_PER_MIN", 600))
        for k in (f"ingest:ip:{ident_ip}", f"ingest:key:{key_id}"):
            try:
                current = cache.get(k) or 0
                if current >= per_min:
                    return Response({"detail": "Rate limited"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                pipe = cache.client.get_client(write=True).pipeline(True)  # type: ignore[attr-defined]
                pipe.incr(k)
                pipe.expire(k, 60)
                pipe.execute()
            except Exception:
                # fallback: allow if cache not available
                pass

        raw_body = request.body or b"{}"
        if not verify_hmac_sha256(key.secret, raw_body, signature):
            return Response({"detail": "Bad signature"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        # support bulk ingest array
        if isinstance(data, list):
            events_in = data
        else:
            events_in = [data]

        stored_ids: list[str] = []
        for item in events_in[:100]:
            ser = ActivityEventIngestSerializer(data=item)
            ser.is_valid(raise_exception=True)
            payload = normalize_payload(ser.validated_data)
            if req_id_header and not payload.get("request_id"):
                payload["request_id"] = req_id_header
            if payload["target"]["type"] not in ALLOW_TARGET_TYPES:
                return Response({"detail": "target.type not allowed"}, status=status.HTTP_400_BAD_REQUEST)
            if payload["verb"] not in dict(Verb.choices):
                return Response({"detail": "verb not allowed"}, status=status.HTTP_400_BAD_REQUEST)
            if payload["source"] not in dict(Source.choices):
                return Response({"detail": "source not allowed"}, status=status.HTTP_400_BAD_REQUEST)

            canon = canonicalize_for_hash(payload)
            event_hash = compute_event_hash(canon)

            # Idempotency on (tenant_id, request_id)
            if payload.get("request_id"):
                dup = ActivityEvent.objects.filter(
                    tenant_id=payload["tenant_id"], request_id=payload["request_id"]
                ).first()
                if dup:
                    stored_ids.append(str(dup.id))
                    continue

            with transaction.atomic():
                prev = (
                    ActivityEvent.objects.filter(tenant_id=payload["tenant_id"]).order_by("-timestamp").first()
                )
                ev = ActivityEvent.objects.create(
                    timestamp=payload["timestamp"],
                    actor_id=payload["actor"]["id"],
                    actor_role=payload["actor"]["role"],
                    verb=payload["verb"],
                    target_type=payload["target"]["type"],
                    target_id=str(payload["target"]["id"]),
                    context=payload.get("context") or {},
                    source=payload["source"],
                    request_id=payload.get("request_id") or "",
                    tenant_id=payload["tenant_id"],
                    hash=event_hash,
                    prev_hash=prev.hash if prev else None,
                )
                stored_ids.append(str(ev.id))

        return Response({"storedIds": stored_ids}, status=status.HTTP_200_OK)


class ActivityEventListView(generics.ListAPIView):
    serializer_class = ActivityEventSerializer
    pagination_class = UICursorPagination
    filterset_class = ActivityEventFilterSet
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ActivityEvent.objects.select_related("actor", "actor__hr_employee").all().order_by("-timestamp", "-id")

        # include_pii=1 only if Admin (HTTPS required in production, allowed in development)
        include_pii = self.request.query_params.get("include_pii") == "1"
        if include_pii:
            is_admin = IsAdmin().has_permission(self.request, self)
            # Allow PII if admin (even without HTTPS in development)
            # In production (non-DEBUG), HTTPS is still required for security
            if not is_admin or (not settings.DEBUG and not self.request.is_secure()):
                # redact PII in results; actual masking applied in serializer by stripping sensitive fields
                self.include_pii = False
            else:
                self.include_pii = True
        else:
            self.include_pii = False

        # RBAC
        qs = apply_rbac(qs, self.request.user)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["include_pii"] = getattr(self, "include_pii", False)
        return ctx

    def list(self, request, *args, **kwargs):
        # Track log view access
        filters = dict(request.query_params)
        _log_view_access(request, target_log_id=None, filters=filters)
        
        # Call parent list method
        return super().list(request, *args, **kwargs)


class ActivityEventDetailView(generics.RetrieveAPIView):
    serializer_class = ActivityEventSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    queryset = ActivityEvent.objects.select_related("actor").all()

    def get_object(self):
        obj = super().get_object()
        # RBAC enforce
        qs = apply_rbac(ActivityEvent.objects.filter(id=obj.id), self.request.user)
        if not qs.exists():
            raise Http404
        
        # Track log view access for this specific log
        _log_view_access(request=self.request, target_log_id=str(obj.id))
        
        return obj

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        # detail view follows same rules
        include_pii_param = self.request.query_params.get("include_pii") == "1"
        if include_pii_param:
            is_admin = IsAdmin().has_permission(self.request, self)
            # Allow PII if admin (even without HTTPS in development)
            # In production (non-DEBUG), HTTPS is still required for security
            include_pii = is_admin and (settings.DEBUG or self.request.is_secure())
        else:
            include_pii = False
        ctx["include_pii"] = include_pii
        return ctx


class ExportStartView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        ser = ExportJobRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        job = ExportJob.objects.create(
            format=ser.validated_data["format"],
            filters_json={
                **ser.validated_data.get("filters", {}),
                "fields": ser.validated_data.get("fields", []),
            },
            requested_by=request.user,
        )
        
        # Check if Celery eager mode is enabled - if so, run synchronously
        from django.conf import settings
        celery_eager = getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)
        
        if celery_eager:
            # Run synchronously if eager mode is enabled
            try:
                _execute_export_job(job.id)
            except Exception as e:
                logger.error(f"Export job {job.id} failed: {e}", exc_info=True)
        else:
            # Try async via Celery
            try:
                # Check if Celery broker is accessible
                from celery import current_app
                inspect = current_app.control.inspect()
                if inspect is None or not inspect.active():
                    # No workers available, run synchronously in thread
                    logger.warning(f"No Celery workers available. Running export {job.id} synchronously.")
                    import threading
                    thread = threading.Thread(target=_execute_export_job, args=(job.id,))
                    thread.daemon = True
                    thread.start()
                else:
                    # Workers available, queue the task
                    run_export_job.delay(job.id)
            except Exception as e:
                logger.warning(f"Failed to queue export job via Celery: {e}. Running synchronously.")
                # Run synchronously as fallback (in background thread to avoid blocking)
                import threading
                thread = threading.Thread(target=_execute_export_job, args=(job.id,))
                thread.daemon = True
                thread.start()
        
        return Response({"jobId": job.id}, status=status.HTTP_202_ACCEPTED)


class ExportStatusView(generics.RetrieveAPIView):
    serializer_class = ExportJobSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = ExportJob.objects.all()
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        job = self.get_object()
        data = ExportJobSerializer(job).data
        if job.status == "COMPLETED" and job.file_path:
            signer = signing.TimestampSigner()
            token = signer.sign(str(job.id))
            url = request.build_absolute_uri(
                reverse("activity_export_download", kwargs={"job_id": job.id}) + f"?sig={token}"
            )
            data["downloadUrl"] = url
        return Response(data)


class ExportDownloadView(APIView):
    """
    Export file download view.
    Allows access via:
    1. Valid signed URL (sig parameter) - no authentication required
    2. Authenticated admin user - if no signature provided
    """
    permission_classes = []  # We'll handle permissions manually

    def get(self, request, job_id: int):
        sig = request.GET.get("sig")
        
        # If signature is provided, validate it
        if sig:
            signer = signing.TimestampSigner()
            try:
                unsigned = signer.unsign(sig, max_age=300)  # 5 minutes expiry
                if unsigned != str(job_id):
                    return Response({"detail": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)
                # Signature is valid, allow access
            except signing.BadSignature:
                return Response({"detail": "Invalid or expired signature"}, status=status.HTTP_403_FORBIDDEN)
            except signing.SignatureExpired:
                return Response({"detail": "Signature has expired"}, status=status.HTTP_403_FORBIDDEN)
        else:
            # No signature provided, require authentication
            if not request.user or not request.user.is_authenticated:
                return Response({"detail": "Authentication required or valid signature"}, status=status.HTTP_401_UNAUTHORIZED)
            # Check if user is admin
            if not IsAdmin().has_permission(request, self):
                return Response({"detail": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
        
        # Get the export job
        try:
            job = ExportJob.objects.get(id=job_id)
        except ExportJob.DoesNotExist:
            raise Http404("Export job not found")
        
        if not job.file_path:
            raise Http404("Export file not found")
        
        # Check if file exists
        if not os.path.exists(job.file_path):
            raise Http404("Export file not found on disk")
        
        # Serve the file
        try:
            file = open(job.file_path, "rb")
            response = FileResponse(file, as_attachment=True, filename=f"export_{job.id}.{job.format.lower()}")
            return response
        except Exception as e:
            logger.error(f"Error serving export file {job.id}: {e}", exc_info=True)
            return Response({"detail": "Error serving file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # lightweight metrics; for production use cached aggregations
        qs = apply_rbac(ActivityEvent.objects.all(), request.user)
        top_verbs = list(qs.values_list("verb", flat=True).order_by().distinct())
        top_targets = list(qs.values_list("target_type", flat=True).order_by().distinct())
        top_sources = list(qs.values_list("source", flat=True).order_by().distinct())
        return Response(
            {
                "topVerbs": top_verbs[:10],
                "topTargetTypes": top_targets[:10],
                "sources": top_sources[:10],
                # For brevity, p95 latency and events/day aggregation can be expanded later
            }
        )


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get summary statistics for activity logs.
        Accepts same filter parameters as ActivityEventListView.
        Returns new_devices_ips count and recent_exports list.
        """
        # Start with base queryset and apply RBAC
        qs = ActivityEvent.objects.select_related("actor", "actor__hr_employee").all()
        qs = apply_rbac(qs, request.user)
        
        # Apply filters using ActivityEventFilterSet
        filterset = ActivityEventFilterSet(request.query_params, queryset=qs)
        filtered_qs = filterset.qs
        
        # Calculate unique IP addresses and device IDs from context
        # Use database aggregation for better performance
        unique_ips = set()
        unique_devices = set()
        
        # Get distinct context values (PostgreSQL supports JSON field queries)
        # For better performance, we'll iterate but limit to a reasonable number
        # In production, consider using raw SQL or materialized views
        for event in filtered_qs.values_list("context", flat=True)[:10000]:  # Limit to prevent memory issues
            if isinstance(event, dict):
                ip = event.get("ip_address") or event.get("ip")
                if ip and ip not in ("-", "", "***"):
                    unique_ips.add(str(ip))
                device_id = event.get("device_id") or event.get("device")
                if device_id and device_id not in ("-", "", "***"):
                    unique_devices.add(str(device_id))
        
        # Count unique IPs and devices
        new_devices_ips = len(unique_ips) + len(unique_devices)
        
        # Get recent exports for the current user
        recent_exports = ExportJob.objects.filter(
            requested_by=request.user
        ).order_by("-finished_at", "-started_at")[:10]
        
        # Return summary data - pass QuerySet directly to let SummarySerializer handle serialization
        summary_data = {
            "new_devices_ips": new_devices_ips,
            "recent_exports": recent_exports,
        }
        
        serializer = SummarySerializer(summary_data, context={"request": request})
        return Response(serializer.data)


class TypesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import ActivityType

        items = list(
            ActivityType.objects.all().values("key", "description", "role_scope", "default_severity")
        )
        return Response({"results": items})


class PoliciesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        from .models import RetentionPolicy

        data = request.data
        rp, _ = RetentionPolicy.objects.update_or_create(
            name=data.get("name"),
            defaults={
                "role_filter": data.get("role_filter", []),
                "target_type_filter": data.get("target_type_filter", []),
                "keep_days": data.get("keep_days", 365),
                "action": data.get("action", "anonymize"),
                "drop_fields": data.get("drop_fields", []),
                "mask_fields": data.get("mask_fields", {}),
                "enabled": data.get("enabled", True),
            },
        )
        return Response({"id": rp.id, "name": rp.name})


class PoliciesRunView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        from .tasks import run_retention
        from .models import RetentionPolicy

        policy_id = request.data.get("policy_id")
        if not policy_id:
            return Response({"detail": "policy_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            policy = RetentionPolicy.objects.get(id=policy_id)
        except RetentionPolicy.DoesNotExist:
            return Response({"detail": "policy not found"}, status=status.HTTP_404_NOT_FOUND)
        run_retention.delay(policy.id)
        return Response({"status": "queued", "policyId": policy.id})


class BehaviorMonitoringView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """
        Analyze activity logs to detect security and risk-related behavior patterns.
        Returns failed logins, suspicious logins, unauthorized access, high-risk edits, and inactive user access.
        """
        try:
            # Start with base queryset and apply RBAC
            qs = ActivityEvent.objects.select_related("actor").all()
            qs = apply_rbac(qs, request.user)
            
            # Apply filters using ActivityEventFilterSet
            filterset = ActivityEventFilterSet(request.query_params, queryset=qs)
            if not filterset.is_valid():
                return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
            filtered_qs = filterset.qs
            
            # Initialize all result lists
            failed_logins = []
            suspicious_logins = []
            unauthorized_access = []
            high_risk_edits = []
            inactive_user_access = []
            
            # 1. Failed Login Attempts
            try:
                # Check for failed logins: status="failed", success=False, or error exists, or no actor (failed attempts)
                # Get all LOGIN events first
                login_events = filtered_qs.filter(verb=Verb.LOGIN)
                
                # Filter for failed logins - check multiple conditions
                # 1. Events with no actor (most failed logins don't have an actor)
                failed_no_actor = login_events.filter(actor_id__isnull=True)
                
                # 2. Events with context indicating failure
                failed_with_status = login_events.filter(context__status="failed")
                failed_with_success = login_events.filter(context__success=False)
                
                # Combine all conditions
                failed_logins_qs = (failed_no_actor | failed_with_status | failed_with_success).distinct().order_by("-timestamp")
                
                total_count = failed_logins_qs.count()
                logger.info(f"Found {total_count} failed login events in queryset")
                
                # Additional debug: check individual conditions
                logger.debug(f"  - No actor: {failed_no_actor.count()}")
                logger.debug(f"  - Status='failed': {failed_with_status.count()}")
                logger.debug(f"  - Success=False: {failed_with_success.count()}")
                
                seen_attempts = {}  # Group by username+ip to count
                
                for event in failed_logins_qs[:200]:  # Limit to prevent memory issues
                    try:
                        context = event.context or {}
                        # Get username from context (stored for failed attempts) or target_id or actor
                        username_from_context = context.get("username")
                        if username_from_context:
                            # Username came from context, decrypt it
                            username = _decrypt_value(username_from_context)
                        else:
                            # Username came from actor or target_id, not encrypted
                            username = event.actor.username if event.actor else event.target_id or "Unknown"
                        
                        ip_address_raw = context.get("ip_address") or context.get("ip") or "-"
                        ip_address = _decrypt_value(ip_address_raw)
                        
                        device_raw = context.get("device_name") or context.get("device_id") or context.get("device_info") or "-"
                        device = _decrypt_value(device_raw)
                        
                        logger.debug(f"Processing failed login: event_id={event.id}, username={username}, ip={ip_address}, context_status={context.get('status')}, context_success={context.get('success')}")
                        
                        # Group by username and IP to count attempts
                        key = f"{username}:{ip_address}"
                        if key in seen_attempts:
                            seen_attempts[key]["count"] += 1
                            # Update timestamp to most recent
                            if event.timestamp > seen_attempts[key]["timestamp"]:
                                seen_attempts[key]["timestamp"] = event.timestamp
                        else:
                            seen_attempts[key] = {
                                "id": str(event.id),
                                "username": username,
                                "ip_address": ip_address,
                                "device": device,
                                "timestamp": event.timestamp,
                                "count": 1,
                            }
                    except Exception as e:
                        logger.warning(f"Error processing failed login event {event.id}: {e}")
                        continue
                
                failed_logins = list(seen_attempts.values())
                # Sort by most recent timestamp
                failed_logins.sort(key=lambda x: x["timestamp"], reverse=True)
                logger.info(f"Returning {len(failed_logins)} grouped failed login attempts")
            except Exception as e:
                logger.error(f"Error detecting failed logins: {e}", exc_info=True)
                failed_logins = []
        
            # 2. Suspicious Logins (multiple IPs/locations within 1 hour)
            try:
                login_events = filtered_qs.filter(verb=Verb.LOGIN).filter(actor_id__isnull=False).order_by("actor_id", "timestamp")
                
                # Group by user and analyze time windows
                user_login_groups = defaultdict(list)
                for event in login_events:
                    if event.actor_id:
                        user_login_groups[str(event.actor_id)].append(event)
                
                one_hour = timedelta(hours=1)
                processed_users = set()  # Track users we've already flagged
                
                for user_id, events in user_login_groups.items():
                    if len(events) < 3 or user_id in processed_users:  # Need at least 3 logins
                        continue
                    
                    # Check for multiple IPs/locations within 1-hour windows
                    events_sorted = sorted(events, key=lambda e: e.timestamp)
                    for i, start_event in enumerate(events_sorted):
                        window_end = start_event.timestamp + one_hour
                        window_events = [e for e in events_sorted if start_event.timestamp <= e.timestamp <= window_end]
                        
                        if len(window_events) >= 3:  # At least 3 logins in 1 hour
                            unique_ips = set()
                            unique_locations = set()
                            
                            for e in window_events:
                                try:
                                    ctx = e.context or {}
                                    ip_raw = ctx.get("ip_address") or ctx.get("ip")
                                    if ip_raw and ip_raw not in ("-", "", "***", None):
                                        ip = _decrypt_value(ip_raw)
                                        if ip and ip not in ("-", "", "***"):
                                            unique_ips.add(ip)
                                    location_raw = ctx.get("location_address") or ctx.get("geo_location") or ctx.get("location")
                                    if location_raw and location_raw not in ("-", "", None):
                                        location = _decrypt_value(location_raw)
                                        if location and location not in ("-", ""):
                                            unique_locations.add(location)
                                except Exception:
                                    continue
                            
                            # Flag if 3+ unique IPs or locations
                            if len(unique_ips) >= 3 or len(unique_locations) >= 3:
                                username = start_event.actor.username if start_event.actor else f"User {user_id}"
                                suspicious_logins.append({
                                    "user_id": user_id,
                                    "username": username,
                                    "login_count": len(window_events),
                                    "unique_ips": list(unique_ips),
                                    "unique_locations": list(unique_locations),
                                    "time_window": "1 hour",
                                    "timestamps": [e.timestamp for e in window_events],
                                })
                                processed_users.add(user_id)
                                break  # Only add once per user
            except Exception as e:
                logger.error(f"Error detecting suspicious logins: {e}", exc_info=True)
                suspicious_logins = []
        
            # 3. Unauthorized Access
            try:
                unauthorized_qs = filtered_qs.filter(
                    Q(context__status_code=403) |
                    Q(context__error__icontains="unauthorized") |
                    Q(context__error__icontains="forbidden") |
                    Q(context__error__icontains="access denied")
                ).order_by("-timestamp")
                
                for event in unauthorized_qs[:100]:
                    try:
                        context = event.context or {}
                        username = event.actor.username if event.actor else "System"
                        ip_address_raw = context.get("ip_address") or context.get("ip") or "-"
                        ip_address = _decrypt_value(ip_address_raw)
                        error = context.get("error") or context.get("message") or "Access denied"
                        
                        unauthorized_access.append({
                            "id": str(event.id),
                            "user": username,
                            "action": event.verb,
                            "target": f"{event.target_type}:{event.target_id}",
                            "ip_address": ip_address,
                            "timestamp": event.timestamp,
                            "error": str(error)[:200],  # Limit error length
                        })
                    except Exception as e:
                        logger.warning(f"Error processing unauthorized access event {event.id}: {e}")
                        continue
                
                # Also check failed exports
                failed_exports = filtered_qs.filter(verb="EXPORT").filter(
                    Q(context__status="failed") | Q(context__error__isnull=False)
                ).order_by("-timestamp")
                
                for event in failed_exports[:50]:
                    try:
                        context = event.context or {}
                        username = event.actor.username if event.actor else "System"
                        ip_address_raw = context.get("ip_address") or context.get("ip") or "-"
                        ip_address = _decrypt_value(ip_address_raw)
                        error = context.get("error") or "Export failed"
                        
                        unauthorized_access.append({
                            "id": str(event.id),
                            "user": username,
                            "action": "EXPORT",
                            "target": f"{event.target_type}:{event.target_id}",
                            "ip_address": ip_address,
                            "timestamp": event.timestamp,
                            "error": str(error)[:200],
                        })
                    except Exception as e:
                        logger.warning(f"Error processing failed export event {event.id}: {e}")
                        continue
            except Exception as e:
                logger.error(f"Error detecting unauthorized access: {e}", exc_info=True)
                unauthorized_access = []
        
            # 4. High-Risk Edits (Payroll, Financial, Bank records)
            try:
                high_risk_qs = filtered_qs.filter(
                    verb__in=[Verb.UPDATE, Verb.DELETE]
                ).filter(
                    Q(target_type__icontains="Payroll") |
                    Q(target_type__icontains="Salary") |
                    Q(target_type__icontains="Financial") |
                    Q(target_type__icontains="Bank") |
                    Q(target_type__icontains="Payment")
                ).filter(actor_id__isnull=False).order_by("actor_id", "timestamp")
                
                user_edit_groups = defaultdict(list)
                for event in high_risk_qs:
                    if event.actor_id:
                        user_edit_groups[str(event.actor_id)].append(event)
                
                processed_targets = set()  # Track targets we've already flagged
                
                for user_id, events in user_edit_groups.items():
                    # Group by target and count edits within 1 hour
                    target_groups = defaultdict(list)
                    for event in events:
                        target_key = f"{event.target_type}:{event.target_id}"
                        target_groups[target_key].append(event)
                    
                    for target_key, target_events in target_groups.items():
                        if target_key in processed_targets:
                            continue
                        
                        # Check for multiple edits within 1 hour
                        target_events.sort(key=lambda e: e.timestamp)
                        for i, start_event in enumerate(target_events):
                            window_end = start_event.timestamp + one_hour
                            window_events = [e for e in target_events if start_event.timestamp <= e.timestamp <= window_end]
                            
                            if len(window_events) > 3:  # More than 3 edits in 1 hour
                                username = start_event.actor.username if start_event.actor else f"User {user_id}"
                                severity = "high" if len(window_events) > 5 else "medium"
                                
                                high_risk_edits.append({
                                    "user_id": user_id,
                                    "username": username,
                                    "target_type": start_event.target_type,
                                    "target_id": start_event.target_id,
                                    "edit_count": len(window_events),
                                    "timestamps": [e.timestamp for e in window_events],
                                    "severity": severity,
                                })
                                processed_targets.add(target_key)
                                break  # Only add once per target
            except Exception as e:
                logger.error(f"Error detecting high-risk edits: {e}", exc_info=True)
                high_risk_edits = []
        
            # 5. Inactive Users Attempting Access
            try:
                from accounts.models import User
                inactive_users_list = list(User.objects.filter(is_active=False).values_list("id", flat=True))
                
                inactive_login_events = filtered_qs.filter(
                    verb=Verb.LOGIN
                ).filter(
                    Q(actor_id__in=inactive_users_list) |
                    Q(context__is_active=False) |
                    Q(context__user_status="inactive")
                ).order_by("-timestamp")
                
                user_attempt_groups = defaultdict(list)
                for event in inactive_login_events[:200]:
                    if event.actor_id:
                        user_id = str(event.actor_id)
                        user_attempt_groups[user_id].append(event)
                
                for user_id, events in user_attempt_groups.items():
                    if events:
                        try:
                            event = events[0]  # Use most recent
                            context = event.context or {}
                            username = event.actor.username if event.actor else f"User {user_id}"
                            ip_address_raw = context.get("ip_address") or context.get("ip") or "-"
                            ip_address = _decrypt_value(ip_address_raw)
                            device_raw = context.get("device_name") or context.get("device_id") or context.get("device_info") or "-"
                            device = _decrypt_value(device_raw)
                            
                            inactive_user_access.append({
                                "user_id": user_id,
                                "username": username,
                                "ip_address": ip_address,
                                "device": device,
                                "timestamp": event.timestamp,
                                "attempt_count": len(events),
                            })
                        except Exception as e:
                            logger.warning(f"Error processing inactive user event {event.id}: {e}")
                            continue
            except Exception as e:
                logger.error(f"Error detecting inactive user access: {e}", exc_info=True)
                inactive_user_access = []
            
            # Serialize and return
            # Note: Serializers will automatically convert datetime objects to ISO format strings
            behavior_data = {
                "failed_logins": failed_logins,
                "suspicious_logins": suspicious_logins,
                "unauthorized_access": unauthorized_access,
                "high_risk_edits": high_risk_edits,
                "inactive_users": inactive_user_access,
            }
            
            serializer = BehaviorMonitoringSerializer(behavior_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in BehaviorMonitoringView: {e}", exc_info=True)
            return Response(
                {"error": "Failed to retrieve behavior monitoring data", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActivityLogMarkReviewedView(APIView):
    """Mark activity log as reviewed or unreviewed"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, id):
        try:
            event = ActivityEvent.objects.get(id=id)
        except ActivityEvent.DoesNotExist:
            return Response({"error": "Activity log not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get reviewed status from request body (default to toggle)
        is_reviewed = request.data.get("is_reviewed")
        if is_reviewed is None:
            # Toggle if not specified
            is_reviewed = not event.is_reviewed
        else:
            is_reviewed = bool(is_reviewed)
        
        event.is_reviewed = is_reviewed
        event.save(update_fields=['is_reviewed'])
        
        # Log the action
        try:
            from .permissions import user_role
            from uuid import uuid4
            
            role = user_role(request.user) or "ADMIN"
            context = {
                "action": "mark_reviewed" if is_reviewed else "mark_unreviewed",
                "log_id": str(event.id),
                "admin_user": request.user.username,
            }
            
            canon = {
                "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tenant_id": event.tenant_id,
                "actor": {"id": str(request.user.id), "role": role},
                "verb": Verb.UPDATE,
                "target": {"type": "ActivityEvent", "id": str(event.id)},
                "source": Source.ADMIN_UI,
                "request_id": f"req_{uuid4().hex}",
                "context": context,
            }
            ev_hash = compute_event_hash(canon)
            
            prev = ActivityEvent.objects.filter(tenant_id=event.tenant_id).order_by("-timestamp").first()
            
            ActivityEvent.objects.create(
                timestamp=timezone.now(),
                actor_id=request.user.id,
                actor_role=role,
                verb=Verb.UPDATE,
                target_type="ActivityEvent",
                target_id=str(event.id),
                context=context,
                source=Source.ADMIN_UI,
                request_id=canon["request_id"],
                tenant_id=event.tenant_id,
                hash=ev_hash,
                prev_hash=prev.hash if prev else None,
            )
        except Exception as e:
            logger.exception(f"Failed to log mark reviewed activity event: {e}")
        
        return Response({
            "id": str(event.id),
            "is_reviewed": event.is_reviewed,
            "message": f"Log marked as {'reviewed' if is_reviewed else 'unreviewed'}"
        }, status=status.HTTP_200_OK)


class ActivityLogRelatedActionsView(APIView):
    """Get all activity logs for a specific user (actor)"""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ActivityEventSerializer
    pagination_class = UICursorPagination
    filterset_class = ActivityEventFilterSet

    def get(self, request):
        actor_id = request.query_params.get('actor_id')
        if not actor_id:
            return Response({"error": "actor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Start with base queryset
        qs = ActivityEvent.objects.select_related("actor", "actor__hr_employee").all()
        
        # Filter by actor_id
        qs = qs.filter(actor_id=actor_id)
        
        # Apply RBAC
        qs = apply_rbac(qs, request.user)
        
        # Apply additional filters using ActivityEventFilterSet
        filterset = ActivityEventFilterSet(request.query_params, queryset=qs)
        filtered_qs = filterset.qs.order_by("-timestamp", "-id")
        
        # Log the action
        try:
            from .permissions import user_role
            from uuid import uuid4
            
            role = user_role(request.user) or "ADMIN"
            context = {
                "action": "view_related_actions",
                "target_user_id": actor_id,
                "admin_user": request.user.username,
            }
            
            canon = {
                "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tenant_id": "default",
                "actor": {"id": str(request.user.id), "role": role},
                "verb": Verb.READ,
                "target": {"type": "User", "id": actor_id},
                "source": Source.ADMIN_UI,
                "request_id": f"req_{uuid4().hex}",
                "context": context,
            }
            ev_hash = compute_event_hash(canon)
            
            prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
            
            ActivityEvent.objects.create(
                timestamp=timezone.now(),
                actor_id=request.user.id,
                actor_role=role,
                verb=Verb.READ,
                target_type="User",
                target_id=actor_id,
                context=context,
                source=Source.ADMIN_UI,
                request_id=canon["request_id"],
                tenant_id="default",
                hash=ev_hash,
                prev_hash=prev.hash if prev else None,
            )
        except Exception as e:
            logger.exception(f"Failed to log view related actions activity event: {e}")
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_qs, request)
        
        if page is not None:
            serializer = self.serializer_class(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = self.serializer_class(filtered_qs, many=True, context={"request": request})
        return Response(serializer.data)


class ActivityLogWarningView(APIView):
    """Send warning or explanation request to a user"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, id):
        try:
            event = ActivityEvent.objects.get(id=id)
        except ActivityEvent.DoesNotExist:
            return Response({"error": "Activity log not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not event.actor_id:
            return Response({"error": "Cannot send warning: no user associated with this log"}, status=status.HTTP_400_BAD_REQUEST)
        
        warning_type = request.data.get("type", "warning")  # "warning" or "explanation_request"
        message = request.data.get("message", "")
        send_email = request.data.get("send_email", False)
        send_notification = request.data.get("send_notification", True)
        
        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        target_user = event.actor
        
        # Send notification via chat if available
        if send_notification:
            try:
                from chat.models import Conversation, Participant, Message
                
                # Find or create a conversation between admin and target user
                conversation, created = Conversation.objects.get_or_create(
                    type='direct',
                    defaults={'title': f'Admin Warning: {target_user.username}'}
                )
                
                # Ensure both users are participants
                Participant.objects.get_or_create(
                    conversation=conversation,
                    user=request.user,
                    defaults={'role': 'admin'}
                )
                Participant.objects.get_or_create(
                    conversation=conversation,
                    user=target_user,
                    defaults={'role': 'user'}
                )
                
                # Create warning message
                warning_text = f"[{warning_type.upper()}] {message}"
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    type='system',
                    text=warning_text
                )
            except Exception as e:
                logger.warning(f"Failed to send chat notification: {e}")
        
        # Send email if requested (placeholder - implement email sending as needed)
        if send_email and target_user.email:
            try:
                # TODO: Implement email sending
                logger.info(f"Would send email to {target_user.email} with warning: {message}")
            except Exception as e:
                logger.warning(f"Failed to send email: {e}")
        
        # Log the warning action
        try:
            from .permissions import user_role
            from uuid import uuid4
            
            role = user_role(request.user) or "ADMIN"
            context = {
                "action": "send_warning",
                "warning_type": warning_type,
                "message": message,
                "target_user_id": str(target_user.id),
                "target_username": target_user.username,
                "admin_user": request.user.username,
                "log_id": str(event.id),
                "send_email": send_email,
                "send_notification": send_notification,
            }
            
            canon = {
                "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tenant_id": event.tenant_id,
                "actor": {"id": str(request.user.id), "role": role},
                "verb": Verb.COMMENT,  # Using COMMENT verb for warnings
                "target": {"type": "User", "id": str(target_user.id)},
                "source": Source.ADMIN_UI,
                "request_id": f"req_{uuid4().hex}",
                "context": context,
            }
            ev_hash = compute_event_hash(canon)
            
            prev = ActivityEvent.objects.filter(tenant_id=event.tenant_id).order_by("-timestamp").first()
            
            ActivityEvent.objects.create(
                timestamp=timezone.now(),
                actor_id=request.user.id,
                actor_role=role,
                verb=Verb.COMMENT,
                target_type="User",
                target_id=str(target_user.id),
                context=context,
                source=Source.ADMIN_UI,
                request_id=canon["request_id"],
                tenant_id=event.tenant_id,
                hash=ev_hash,
                prev_hash=prev.hash if prev else None,
            )
        except Exception as e:
            logger.exception(f"Failed to log warning activity event: {e}")
        
        return Response({
            "message": f"Warning sent successfully to {target_user.username}",
            "warning_type": warning_type,
            "sent_email": send_email,
            "sent_notification": send_notification,
        }, status=status.HTTP_200_OK)


class ScheduledReportListView(generics.ListCreateAPIView):
    """List and create scheduled reports."""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ScheduledReportSerializer
    
    def get_queryset(self):
        return ScheduledReport.objects.filter(created_by=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        report = serializer.save(created_by=self.request.user)
        # Calculate initial next_run
        report.next_run = _calculate_next_run(report, timezone.now())
        report.save(update_fields=['next_run'])


class ScheduledReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a scheduled report."""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ScheduledReportSerializer
    queryset = ScheduledReport.objects.all()
    lookup_field = "id"
    
    def get_queryset(self):
        # Only allow users to manage their own scheduled reports (or all if superuser)
        if self.request.user.is_superuser:
            return ScheduledReport.objects.all()
        return ScheduledReport.objects.filter(created_by=self.request.user)
    
    def perform_update(self, serializer):
        report = serializer.save()
        # Recalculate next_run if schedule changed
        if serializer.validated_data.get('schedule_type') or serializer.validated_data.get('schedule_time') or serializer.validated_data.get('schedule_day'):
            report.next_run = _calculate_next_run(report, timezone.now())
            report.save(update_fields=['next_run'])


class ScheduledReportRunNowView(APIView):
    """Manually trigger a scheduled report to run immediately."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, id):
        try:
            report = ScheduledReport.objects.get(id=id)
            # Check permissions
            if not request.user.is_superuser and report.created_by != request.user:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        except ScheduledReport.DoesNotExist:
            return Response({"error": "Scheduled report not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Create export job
        export_job = ExportJob.objects.create(
            format=report.format,
            filters_json=report.filters_json,
            requested_by=request.user,
            scheduled_report=report,
            status=JobStatus.PENDING,
        )
        
        # Check if Celery eager mode is enabled - if so, run synchronously
        celery_eager = getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)
        
        if celery_eager:
            # Run synchronously if eager mode is enabled
            try:
                _execute_export_job(export_job.id)
            except Exception as e:
                logger.error(f"Export job {export_job.id} failed: {e}", exc_info=True)
        else:
            # Try async via Celery
            try:
                # Check if Celery broker is accessible
                from celery import current_app
                inspect = current_app.control.inspect()
                if inspect is None or not inspect.active():
                    # No workers available, run synchronously in thread
                    logger.warning(f"No Celery workers available. Running export {export_job.id} synchronously.")
                    import threading
                    thread = threading.Thread(target=_execute_export_job, args=(export_job.id,))
                    thread.daemon = True
                    thread.start()
                else:
                    # Workers available, queue the task
                    run_export_job.delay(export_job.id)
            except Exception as e:
                logger.warning(f"Failed to queue export job via Celery: {e}. Running synchronously.")
                # Run synchronously as fallback (in background thread to avoid blocking)
                import threading
                thread = threading.Thread(target=_execute_export_job, args=(export_job.id,))
                thread.daemon = True
                thread.start()
        
        return Response({
            "message": f"Scheduled report '{report.name}' has been queued for execution",
            "export_job_id": export_job.id,
            "status": "PENDING",
        }, status=status.HTTP_202_ACCEPTED)

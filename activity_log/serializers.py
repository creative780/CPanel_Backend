from __future__ import annotations

from typing import Any

from datetime import timezone as dt_timezone
from rest_framework import serializers

from .models import ActivityEvent, ExportJob, ExportFormat, ScheduledReport, ScheduleType


class ActorField(serializers.Serializer):
    id = serializers.CharField(allow_blank=True, required=False)
    role = serializers.CharField()


class TargetField(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.CharField()


class ContextField(serializers.DictField):
    child = serializers.JSONField(required=False)


class ActivityEventIngestSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField(default_timezone=dt_timezone.utc)
    tenant_id = serializers.CharField()
    actor = ActorField(required=False, allow_null=True)
    verb = serializers.CharField()
    target = TargetField()
    source = serializers.CharField()
    request_id = serializers.CharField(required=False, allow_blank=True)
    context = ContextField(required=False)


class ActivityEventSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    class Meta:
        model = ActivityEvent
        fields = (
            "id",
            "timestamp",
            "actor",
            "verb",
            "target",
            "context",
            "source",
            "hash",
            "is_reviewed",
        )

    def get_actor(self, obj: ActivityEvent) -> dict[str, Any]:
        name = None
        department = None
        branch = None
        
        if obj.actor_id and getattr(obj, "actor", None):
            # prefer username; fall back to first/last
            username = getattr(obj.actor, "username", None)
            full = " ".join(filter(None, [getattr(obj.actor, "first_name", None), getattr(obj.actor, "last_name", None)])).strip()
            name = username or (full if full else None)
            
            # Try to get department and branch from HREmployee
            # The relationship should be prefetched via select_related in the view
            try:
                hr_employee = getattr(obj.actor, "hr_employee", None)
                if hr_employee:
                    department = getattr(hr_employee, "role", None)
                    branch = getattr(hr_employee, "branch", None)
            except Exception:
                # If HREmployee doesn't exist or error, continue without it
                pass
        
        if not name and not obj.actor_id:
            name = "System"
        
        result = {
            "id": str(obj.actor_id) if obj.actor_id else None,
            "role": obj.actor_role,
            "name": name,
        }
        
        # Add is_active status if actor exists and is loaded
        # The queryset should use select_related("actor") to ensure actor is loaded
        if obj.actor_id:
            actor = getattr(obj, "actor", None)
            if actor:
                result["is_active"] = actor.is_active
            else:
                # Actor not loaded - this shouldn't happen if select_related is used
                # But handle gracefully by setting to None
                result["is_active"] = None
        else:
            result["is_active"] = None
        
        # Add department and branch if available
        if department:
            result["department"] = department
        if branch:
            result["branch"] = branch
        
        return result

    def get_target(self, obj: ActivityEvent) -> dict[str, Any]:
        return {
            "type": obj.target_type,
            "id": obj.target_id,
        }

    def to_representation(self, instance: ActivityEvent):
        data = super().to_representation(instance)
        # Get decrypted context
        ctx = instance.get_decrypted_context()
        include_pii = self.context.get("include_pii", False)
        if not include_pii:
            # mask common PII fields in context
            for fld in ("ip", "user_agent", "filename", "ip_address", "device_id", "device_name"):
                if fld in ctx:
                    ctx[fld] = "***"
        data["context"] = ctx
        return data


class ExportJobRequestSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=[ExportFormat.CSV, ExportFormat.NDJSON, ExportFormat.PDF, ExportFormat.XML])
    filters = serializers.DictField(required=False, default=dict)
    fields = serializers.ListField(child=serializers.CharField(), required=False)


class ExportJobSerializer(serializers.ModelSerializer):
    scheduled_report = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ExportJob
        fields = (
            "id",
            "format",
            "status",
            "file_path",
            "started_at",
            "finished_at",
            "error",
            "scheduled_report",
        )


class ExportJobListSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportJob
        fields = (
            "id",
            "format",
            "status",
            "finished_at",
            "download_url",
        )
    
    def get_download_url(self, obj):
        # Handle both model instances and dictionaries (from already-serialized data)
        if isinstance(obj, dict):
            status = obj.get("status")
            file_path = obj.get("file_path")
            obj_id = obj.get("id")
        else:
            status = obj.status
            file_path = obj.file_path
            obj_id = obj.id
        
        if status == "COMPLETED" and file_path:
            request = self.context.get("request")
            if request:
                from django.core import signing
                from django.urls import reverse
                signer = signing.TimestampSigner()
                token = signer.sign(str(obj_id))
                return request.build_absolute_uri(
                    reverse("activity_export_download", kwargs={"job_id": obj_id}) + f"?sig={token}"
                )
        return None


class SummarySerializer(serializers.Serializer):
    new_devices_ips = serializers.IntegerField()
    recent_exports = ExportJobListSerializer(many=True)


class FailedLoginAttemptSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    ip_address = serializers.CharField()
    device = serializers.CharField()
    timestamp = serializers.DateTimeField()
    count = serializers.IntegerField()


class SuspiciousLoginSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    username = serializers.CharField()
    login_count = serializers.IntegerField()
    unique_ips = serializers.ListField(child=serializers.CharField())
    unique_locations = serializers.ListField(child=serializers.CharField())
    time_window = serializers.CharField()
    timestamps = serializers.ListField(child=serializers.DateTimeField())


class UnauthorizedAccessSerializer(serializers.Serializer):
    id = serializers.CharField()
    user = serializers.CharField()
    action = serializers.CharField()
    target = serializers.CharField()
    ip_address = serializers.CharField()
    timestamp = serializers.DateTimeField()
    error = serializers.CharField()


class HighRiskEditSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    username = serializers.CharField()
    target_type = serializers.CharField()
    target_id = serializers.CharField()
    edit_count = serializers.IntegerField()
    timestamps = serializers.ListField(child=serializers.DateTimeField())
    severity = serializers.ChoiceField(choices=["medium", "high"])


class InactiveUserAccessSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    username = serializers.CharField()
    ip_address = serializers.CharField()
    device = serializers.CharField()
    timestamp = serializers.DateTimeField()
    attempt_count = serializers.IntegerField()


class BehaviorMonitoringSerializer(serializers.Serializer):
    failed_logins = FailedLoginAttemptSerializer(many=True, required=False, allow_empty=True)
    suspicious_logins = SuspiciousLoginSerializer(many=True, required=False, allow_empty=True)
    unauthorized_access = UnauthorizedAccessSerializer(many=True, required=False, allow_empty=True)
    high_risk_edits = HighRiskEditSerializer(many=True, required=False, allow_empty=True)
    inactive_users = InactiveUserAccessSerializer(many=True, required=False, allow_empty=True)


class ScheduledReportSerializer(serializers.ModelSerializer):
    schedule_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M:%S'])
    
    class Meta:
        model = ScheduledReport
        fields = (
            "id",
            "name",
            "schedule_type",
            "schedule_time",
            "schedule_day",
            "recipients",
            "format",
            "filters_json",
            "is_active",
            "last_run",
            "next_run",
            "created_at",
            "updated_at",
            "created_by",
        )
        read_only_fields = ("id", "created_at", "updated_at", "last_run", "next_run", "created_by")
    
    def validate(self, data):
        """Validate schedule_day is set for weekly reports."""
        schedule_type = data.get('schedule_type', getattr(self.instance, 'schedule_type', None))
        schedule_day = data.get('schedule_day', getattr(self.instance, 'schedule_day', None))
        
        if schedule_type == ScheduleType.WEEKLY and schedule_day is None:
            raise serializers.ValidationError({
                'schedule_day': 'schedule_day is required for weekly reports (0=Monday, 6=Sunday)'
            })
        
        if schedule_type == ScheduleType.DAILY and schedule_day is not None:
            # Clear schedule_day for daily reports
            data['schedule_day'] = None
        
        # Validate recipients
        recipients = data.get('recipients', getattr(self.instance, 'recipients', []))
        if not recipients:
            raise serializers.ValidationError({
                'recipients': 'At least one recipient email address is required'
            })
        
        # Validate email addresses
        import re
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for email in recipients:
            if not email_regex.match(email):
                raise serializers.ValidationError({
                    'recipients': f'Invalid email address: {email}'
                })
        
        return data

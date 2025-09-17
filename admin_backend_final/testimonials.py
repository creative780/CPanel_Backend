# views/testimonial_views.py

import json
from uuid import uuid4

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Testimonial, Image
from .permissions import FrontendOnlyPermission
from .utilities import save_image  # expects (file_or_base64, alt_text, tags, linked_table, linked_page, linked_id)


# --------------------------
# Helpers
# --------------------------

def _as_bool(val, default=False):
    if val is None or val == "":
        return default
    s = str(val).strip().lower()
    if s in ("true", "1", "yes", "on"):
        return True
    if s in ("false", "0", "no", "off"):
        return False
    return default

def _clamp_rating(n):
    try:
        n = int(round(float(n)))
    except Exception:
        return 5
    return max(1, min(5, n))

def _parse_body(request):
    """Return (data, files) for JSON or form/multipart."""
    if request.content_type and "application/json" in (request.content_type or ""):
        try:
            if isinstance(request.data, dict):
                return request.data, {}
            body = request.body.decode("utf-8") if request.body else "{}"
            return json.loads(body or "{}"), {}
        except Exception:
            return {}, {}
    return request.POST, request.FILES

def _normalize_id(val):
    v = (str(val or "")).strip()
    return v or None
# --------------------------
# Helpers (updated signature only)
# --------------------------

def _serialize_testimonial(t: Testimonial, request=None):
    """
    Return a dict for the testimonial. If an Image file exists, prefer its URL.
    Otherwise fall back to image_url. Build absolute URL when request is available.
    """
    avatar = ""
    try:
        if t.image and getattr(t.image, "image_file", None):
            avatar = t.image.image_file.url or ""
    except Exception:
        avatar = ""

    if not avatar:
        avatar = t.image_url or ""

    # If we have a relative URL and a request, make it absolute
    if request and isinstance(avatar, str) and avatar.startswith("/"):
        try:
            avatar = request.build_absolute_uri(avatar)
        except Exception:
            pass

    return {
        "id": t.testimonial_id,
        "testimonial_id": t.testimonial_id,
        "name": t.name,
        "role": t.role or "",
        "content": t.content or "",
        "image": avatar,                       # resolved, absolute when possible
        "rating": int(t.rating or 5),
        "status": t.status.title() if t.status else "Draft",
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        # raw fields if needed
        "image_id": getattr(t.image, "image_id", None) if t.image_id else None,
        "image_url": t.image_url or "",
        "order": t.order,
    }


# --------------------------
# 1) SHOW (list)
# GET /api/show-testimonials[?all=1]
# --------------------------
class ShowTestimonialsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        include_all = _as_bool(request.query_params.get("all"), default=False)

        qs = Testimonial.objects.all().order_by("order", "-updated_at", "-created_at")
        if not include_all:
            qs = qs.filter(status="published")

        # pass request so image URLs become absolute
        data = [_serialize_testimonial(t, request) for t in qs]
        return Response(data, status=status.HTTP_200_OK)
    
# --------------------------
# 2) SAVE (create)
# POST /api/save-testimonials
# Accepts JSON or multipart/form with fields:
#  - id|testimonial_id? (if provided and exists, will update-in-place)
#  - name (required), role?, content?, rating?, status? (draft|published)
#  - image_id? (existing Image PK), or image / avatar / image_file (base64 or file)
#  - image_url? (external fallback)
# --------------------------
class SaveTestimonialsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data, files = _parse_body(request)

        # core fields
        tid = _normalize_id(data.get("id") or data.get("testimonial_id"))
        name = (data.get("name") or "").strip()
        role = (data.get("role") or "").strip()
        content = (data.get("content") or "").strip()
        rating = _clamp_rating(data.get("rating") or 5)
        status_in = (data.get("status") or "").strip().lower()
        status_norm = "published" if status_in == "published" else "draft"

        if not name:
            return Response({"error": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

        created = False
        if tid:
            obj, created = Testimonial.objects.get_or_create(
                testimonial_id=tid,
                defaults={
                    "name": name,
                    "role": role,
                    "content": content,
                    "rating": rating,
                    "status": status_norm,
                },
            )
            if not created:
                obj.name = name or obj.name
                obj.role = role if role != "" else obj.role
                obj.content = content if content != "" else obj.content
                obj.rating = rating
                obj.status = status_norm or obj.status
        else:
            obj = Testimonial(
                testimonial_id=f"t-{uuid4().hex[:12]}",
                name=name,
                role=role,
                content=content,
                rating=rating,
                status=status_norm,
            )
            created = True

        # Image resolution order: image_id > image/avatar/image_file (upload/base64) > image_url
        image_id = _normalize_id(data.get("image_id"))
        image_payload = (
            files.get("image") or files.get("avatar") or files.get("image_file")
            or data.get("image") or data.get("avatar")
        )
        image_url_fallback = (data.get("image_url") or "").strip()

        # NEW: if client sent a normal http(s) URL inside "image", treat it as image_url
        if isinstance(image_payload, str) and image_payload.strip().lower().startswith(("http://", "https://")):
            image_url_fallback = image_payload.strip()
            image_payload = None

        if image_id:
            try:
                img = Image.objects.get(image_id=image_id)
                obj.image = img
            except Image.DoesNotExist:
                pass
        elif image_payload:
            saved_img = save_image(
                file_or_base64=image_payload,
                alt_text=f"{name} avatar",
                tags="testimonial,avatar",
                linked_table="testimonial",
                linked_page="TestimonialManagement",
                linked_id=obj.testimonial_id,
            )
            if saved_img:
                obj.image = saved_img

        if image_url_fallback:
            obj.image_url = image_url_fallback

        # Optional audit/order fields
        cb = (data.get("created_by") or "").strip()
        cbt = (data.get("created_by_type") or "").strip().lower()
        if cb:
            obj.created_by = cb
        if cbt in ("admin", "user"):
            obj.created_by_type = cbt

        try:
            if "order" in data and str(data.get("order")).strip() != "":
                obj.order = max(0, int(data.get("order")))
        except Exception:
            pass

        obj.updated_at = timezone.now()
        if created:
            obj.created_at = timezone.now()
        obj.save()

        # return with absolute image URL when possible
        return Response(
            _serialize_testimonial(obj, request),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

# --------------------------
# 3) EDIT (update / delete)
# PUT/POST /api/edit-testimonials   (body includes id|testimonial_id)
# DELETE   /api/edit-testimonials?id=<id>
# --------------------------
class EditTestimonialsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def put(self, request):
        return self._save_or_update(request)

    def post(self, request):
        return self._save_or_update(request)

    @transaction.atomic
    def delete(self, request):
        tid = _normalize_id(request.query_params.get("id") or request.query_params.get("testimonial_id"))
        if not tid:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = Testimonial.objects.get(testimonial_id=tid)
        except Testimonial.DoesNotExist:
            return Response({"error": "Testimonial not found"}, status=status.HTTP_404_NOT_FOUND)

        obj.delete()
        return Response({"success": True, "deleted": tid}, status=status.HTTP_200_OK)

    @transaction.atomic
    def _save_or_update(self, request):
        data, files = _parse_body(request)
        tid = _normalize_id(data.get("id") or data.get("testimonial_id"))
        if not tid:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = Testimonial.objects.get(testimonial_id=tid)
        except Testimonial.DoesNotExist:
            return Response({"error": "Testimonial not found"}, status=status.HTTP_404_NOT_FOUND)

        # Patchable fields
        if "name" in data:
            v = (data.get("name") or "").strip()
            if v:
                obj.name = v

        if "role" in data:
            obj.role = (data.get("role") or "").strip()

        if "content" in data or "message" in data:
            obj.content = (data.get("content") or data.get("message") or "").strip() or obj.content

        if "rating" in data:
            obj.rating = _clamp_rating(data.get("rating"))

        if "status" in data:
            st = (data.get("status") or "").strip().lower()
            if st in ("draft", "published"):
                obj.status = st

        if "order" in data:
            try:
                obj.order = max(0, int(data.get("order")))
            except Exception:
                pass

        # Image update
        image_id = _normalize_id(data.get("image_id"))
        image_payload = (
            files.get("image") or files.get("avatar") or files.get("image_file")
            or data.get("image") or data.get("avatar")
        )
        image_url_fallback = (data.get("image_url") or "").strip()

        # NEW: accept plain URL inside "image" as image_url
        if isinstance(image_payload, str) and image_payload.strip().lower().startswith(("http://", "https://")):
            image_url_fallback = image_payload.strip()
            image_payload = None

        if image_id:
            try:
                img = Image.objects.get(image_id=image_id)
                obj.image = img
            except Image.DoesNotExist:
                pass

        elif image_payload:
            saved_img = save_image(
                file_or_base64=image_payload,
                alt_text=f"{obj.name} avatar",
                tags="testimonial,avatar",
                linked_table="testimonial",
                linked_page="TestimonialManagement",
                linked_id=obj.testimonial_id,
            )
            if saved_img:
                obj.image = saved_img

        if "image_url" in data or image_url_fallback:
            obj.image_url = image_url_fallback

        obj.updated_at = timezone.now()
        obj.save()

        # include absolute image URL
        return Response({"success": True, **_serialize_testimonial(obj, request)}, status=status.HTTP_200_OK)
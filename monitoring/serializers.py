from rest_framework import serializers
from django.db import models
from .models import (
    Employee, EmployeeActivity, EmployeeAsset, EmployeeSummary,
    Device, DeviceToken, Heartbeat, Session, Org, DeviceUserBind,
    Recording, RecordingSegment
)


class EmployeeAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAsset
        fields = ['kind', 'path', 'created_at']


class EmployeeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSummary
        fields = ['date', 'keystrokes', 'clicks', 'active_minutes', 'idle_minutes', 'productivity']


class EmployeeSerializer(serializers.ModelSerializer):
    screenshots = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    activityTimeline = serializers.SerializerMethodField()
    dailySummary = serializers.SerializerMethodField()
    lastScreenshot = serializers.SerializerMethodField()
    keystrokeCount = serializers.SerializerMethodField()
    mouseClicks = serializers.SerializerMethodField()
    activeTime = serializers.SerializerMethodField()
    idleTime = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'email', 'department', 'status', 'productivity',
            'screenshots', 'videos', 'activityTimeline', 'dailySummary',
            'lastScreenshot', 'keystrokeCount', 'mouseClicks', 'activeTime', 'idleTime', 'activities',
        ]

    def get_screenshots(self, obj):
        return [a.path for a in obj.assets.filter(kind='screenshot', deleted_at__isnull=True).order_by('-created_at')[:20]]

    def get_videos(self, obj):
        return [a.path for a in obj.assets.filter(kind='video', deleted_at__isnull=True).order_by('-created_at')[:5]]

    def get_activityTimeline(self, obj):
        # Simple 24-bucket timeline from last 24h
        buckets = [0] * 24
        qs = obj.activities.order_by('-when')[:1000]
        for a in qs:
            hour = a.when.hour
            buckets[hour] = buckets[hour] + a.delta_k + a.delta_c
        return buckets

    def get_dailySummary(self, obj):
        return EmployeeSummarySerializer(obj.summaries.order_by('-date')[:7], many=True).data

    def get_lastScreenshot(self, obj):
        if obj.last_screenshot_at:
            from django.utils import timezone
            now = timezone.now()
            diff = now - obj.last_screenshot_at
            if diff.total_seconds() < 60:
                return "Just now"
            elif diff.total_seconds() < 3600:
                return f"{int(diff.total_seconds() / 60)} min ago"
            else:
                return f"{int(diff.total_seconds() / 3600)} hour ago"
        return "Never"

    def get_keystrokeCount(self, obj):
        return obj.activities.aggregate(total=models.Sum('delta_k'))['total'] or 0

    def get_mouseClicks(self, obj):
        return obj.activities.aggregate(total=models.Sum('delta_c'))['total'] or 0

    def get_activeTime(self, obj):
        # Calculate from activities
        total_minutes = obj.activities.count() * 2  # Assume 2 minutes per activity
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"

    def get_idleTime(self, obj):
        # Simple calculation based on status
        if obj.status == 'offline':
            return "8h 0m"
        elif obj.status == 'idle':
            return "1h 30m"
        else:
            return "0h 15m"

    def get_activities(self, obj):
        activities = obj.activities.order_by('-when')[:10]
        return [
            {
                'time': a.when.strftime('%H:%M'),
                'action': a.action or 'Activity',
                'application': a.application or 'System'
            }
            for a in activities
        ]


class TrackSerializer(serializers.Serializer):
    employeeIds = serializers.ListField(child=serializers.IntegerField())
    delta = serializers.DictField(child=serializers.IntegerField(), allow_empty=True)
    action = serializers.CharField(allow_blank=True, required=False)
    application = serializers.CharField(allow_blank=True, required=False)
    when = serializers.DateTimeField()


class ScreenshotUploadSerializer(serializers.Serializer):
    employeeIds = serializers.ListField(child=serializers.IntegerField())
    when = serializers.DateTimeField()
    imageDataUrl = serializers.CharField()


class ScreenshotDeleteSerializer(serializers.Serializer):
    employeeId = serializers.IntegerField()
    file = serializers.CharField()


# New monitoring system serializers
class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Org
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    # Note: Device model no longer has 'user' field - use 'current_user' instead
    user_email = serializers.CharField(source='current_user.email', read_only=True, allow_null=True)
    user_name = serializers.SerializerMethodField()
    org_name = serializers.CharField(source='org.name', read_only=True, allow_null=True)
    latest_thumb = serializers.SerializerMethodField()
    current_user_email = serializers.CharField(source='current_user.email', read_only=True, allow_null=True)

    class Meta:
        model = Device
        fields = '__all__'

    def get_user_name(self, obj):
        return f"{obj.current_user.first_name} {obj.current_user.last_name}".strip() if obj.current_user else None
    
    def get_latest_thumb(self, obj):
        last = obj.recordings.order_by('-start_time').first()
        return last.thumb_key if last and last.thumb_key else None


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = '__all__'


class DeviceUserBindSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceUserBind
        fields = '__all__'


class HeartbeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heartbeat
        fields = '__all__'


# ScreenshotSerializer removed - Screenshot model no longer exists
# Use RecordingSerializer instead


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class RecordingSerializer(serializers.ModelSerializer):
    """Serializer for Recording model"""
    device_name = serializers.CharField(source='device.hostname', read_only=True)
    user_name = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Recording
        fields = [
            'id', 'device', 'device_id', 'device_name', 'user_name',
            'blob_key', 'thumb_key', 'start_time', 'end_time', 'duration_seconds',
            'is_idle_period', 'idle_start_offset', 'user_id_snapshot',
            'user_name_snapshot', 'user_role_snapshot', 'created_at',
            'video_url', 'thumbnail_url'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        """Get user name from current_user or snapshot"""
        if obj.device.current_user:
            return f"{obj.device.current_user.first_name} {obj.device.current_user.last_name}".strip() or obj.device.current_user.email
        return obj.user_name_snapshot or "Unknown User"
    
    def get_video_url(self, obj):
        """Generate video URL"""
        return f"/api/monitoring/files/{obj.blob_key}" if obj.blob_key else None
    
    def get_thumbnail_url(self, obj):
        """Generate thumbnail URL"""
        return f"/api/monitoring/files/{obj.thumb_key}" if obj.thumb_key else None


class RecordingSegmentSerializer(serializers.ModelSerializer):
    """Serializer for RecordingSegment model"""
    class Meta:
        model = RecordingSegment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class RecordingIngestSerializer(serializers.Serializer):
    """Serializer for recording upload validation"""
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    duration_seconds = serializers.FloatField(required=True)
    is_idle_period = serializers.BooleanField(default=False, required=False)
    idle_start_offset = serializers.FloatField(allow_null=True, required=False)


class FrameEncodingSerializer(serializers.Serializer):
    """Serializer for frame encoding request validation"""
    frames = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Array of base64-encoded JPEG strings"
    )
    metadata = serializers.DictField(
        required=True,
        help_text="Segment metadata containing segment_start, segment_end, segment_index, segment_id, date, duration_seconds"
    )
    
    def validate_metadata(self, value):
        """Validate that metadata contains required keys"""
        required_keys = ['segment_start', 'segment_end', 'segment_index', 'segment_id', 'date', 'duration_seconds']
        missing_keys = [key for key in required_keys if key not in value]
        if missing_keys:
            raise serializers.ValidationError(f"Missing required metadata keys: {', '.join(missing_keys)}")
        return value
    
    def validate_frames(self, value):
        """Validate that frames array is not empty"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("Frames array cannot be empty")
        return value


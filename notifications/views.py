from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from accounts.permissions import user_has_any_role
from .models import Notification
from .serializers import NotificationListSerializer, NotificationDetailSerializer, NotificationUpdateSerializer
from .permissions import CanViewNotification, get_notification_queryset


class NotificationListView(APIView):
    """List notifications for the authenticated user"""
    permission_classes = [IsAuthenticated, CanViewNotification]
    
    def get(self, request):
        """Get notifications, optionally filtered by read status"""
        is_read_filter = request.query_params.get('is_read')
        
        # Use helper function to get appropriate queryset (includes admin notifications)
        queryset = get_notification_queryset(request.user)
        
        # Filter by read status if provided
        if is_read_filter is not None:
            is_read_value = is_read_filter.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_read=is_read_value)
        
        notifications = queryset.order_by('-created_at')[:50]  # Limit to 50 most recent
        
        # Use serializer for consistent output
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data)


class UnreadCountView(APIView):
    """Get unread notification count for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get count of unread notifications"""
        # Use helper function to get appropriate queryset
        queryset = get_notification_queryset(request.user)
        count = queryset.filter(is_read=False).count()
        
        return Response({'count': count})


class MarkReadView(APIView):
    """Mark a notification as read or unread"""
    permission_classes = [IsAuthenticated, CanViewNotification]
    
    def patch(self, request, notification_id):
        """Mark a specific notification as read or unread"""
        try:
            notification = Notification.objects.get(id=notification_id)
            
            # Check permission using CanViewNotification
            if not CanViewNotification().has_object_permission(request, self, notification):
                return Response(
                    {'detail': 'You do not have permission to access this notification'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get is_read value from request (default to True if not provided for backward compatibility)
            is_read_value = request.data.get('is_read', True)
            if isinstance(is_read_value, str):
                is_read_value = is_read_value.lower() in ('true', '1', 'yes')
            
            # Use serializer for update
            serializer = NotificationUpdateSerializer(notification, data={'is_read': is_read_value}, partial=True)
            if serializer.is_valid():
                serializer.save()
                status_text = 'read' if is_read_value else 'unread'
                return Response({'detail': f'Notification marked as {status_text}'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Notification.DoesNotExist:
            return Response(
                {'detail': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications with role-based filtering.
    
    Employees see only their own notifications.
    Admins see their own notifications plus all request notifications
    (leave_requested, design_submitted).
    """
    permission_classes = [IsAuthenticated, CanViewNotification]
    serializer_class = NotificationListSerializer
    
    def get_queryset(self):
        """
        Filter notifications based on user role.
        
        - Employees: only their own notifications
        - Admins: their own notifications + all request notifications
        """
        return get_notification_queryset(self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return NotificationDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationUpdateSerializer
        return NotificationListSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """Get notification detail - checks permissions"""
        instance = self.get_object()
        # Permission check is handled by CanViewNotification.has_object_permission
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """Update notification (e.g., mark as read/unread) - checks permissions"""
        instance = self.get_object()
        # Permission check is handled by CanViewNotification.has_object_permission
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

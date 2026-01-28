from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationListView, UnreadCountView, MarkReadView

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Put direct paths BEFORE router to avoid conflicts
    # Order matters: more specific paths first
    path('notifications/unread-count/', UnreadCountView.as_view(), name='notifications-unread-count'),
    path('notifications/<int:notification_id>/mark-read/', MarkReadView.as_view(), name='notifications-mark-read'),
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    # Router URLs - ViewSet handles:
    # - GET /api/notifications/ (list)
    # - GET /api/notifications/{id}/ (retrieve/detail)
    # - PATCH /api/notifications/{id}/ (partial_update)
    # - PUT /api/notifications/{id}/ (update)
    path('', include(router.urls)),
]

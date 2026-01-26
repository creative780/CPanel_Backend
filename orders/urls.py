from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrdersViewSet, SendDeliveryCodeView, RiderPhotoUploadView,
    OrdersListView, OrderDetailView, QuotationView, LeaderboardView,
    ChannelAnalyticsView, TagAnalyticsView, ProductImageServeView  # Legacy views
)
from .views_workflow import (
    RequestDesignApprovalView, DesignApprovalsListView, ApproveDesignView, SendToDesignerView, SendToProductionView,
    AssignMachinesView, UploadOrderFileView, OrderFilesListView,
    OrderFileDownloadView, DeleteOrderFileView, UpdateOrderFileView, PendingApprovalsView, 
    MachineQueueView, UpdateMachineAssignmentStatusView, SendToAdminView,
    OrderStatusTrackingView, UploadQuotationPDFView
)
from .views_production import (
    ProductionOrdersView, ProductionOrderDetailView
)
from .views_design_files import (
    DesignFileUploadView, DesignFileDownloadView, DesignFileListView, DesignFileDeleteView, DesignFileUrlView
)

# Create router for ViewSet
router = DefaultRouter()
router.register(r'orders', OrdersViewSet, basename='orders')

urlpatterns = [
    # Analytics endpoints - MUST come before router to avoid catch-all matching
    path('orders/leaderboard/', LeaderboardView.as_view(), name='orders-leaderboard'),
    path('orders/channel_analytics/', ChannelAnalyticsView.as_view(), name='orders-channel-analytics'),
    path('orders/tag_analytics/', TagAnalyticsView.as_view(), name='orders-tag-analytics'),
    
    # Main API routes using ViewSet (router comes after specific paths)
    path('', include(router.urls)),
    
    # Quotation endpoints
    path('orders/<int:order_id>/quotation/', QuotationView.as_view(), name='order-quotation'),
    path('upload-quotation-pdf/', UploadQuotationPDFView.as_view(), name='upload-quotation-pdf'),
    
    # Delivery endpoints - matches frontend contracts
    path('send-delivery-code', SendDeliveryCodeView.as_view(), name='send-delivery-code'),
    path('delivery/rider-photo', RiderPhotoUploadView.as_view(), name='rider-photo-upload'),
    
    # Workflow endpoints - Design Approval
    path('orders/<int:order_id>/request-approval/', RequestDesignApprovalView.as_view(), name='request-design-approval'),
    path('orders/<int:order_id>/design-approvals/', DesignApprovalsListView.as_view(), name='order-design-approvals'),
    path('approvals/<int:approval_id>/decision/', ApproveDesignView.as_view(), name='approve-design'),
    path('approvals/pending/', PendingApprovalsView.as_view(), name='pending-approvals'),
    
    # Workflow endpoints - Designer
    path('orders/<int:order_id>/send-to-designer/', SendToDesignerView.as_view(), name='send-to-designer'),
    
    # Workflow endpoints - Production
    path('orders/<int:order_id>/send-to-production/', SendToProductionView.as_view(), name='send-to-production'),
    path('orders/<int:order_id>/assign-machines/', AssignMachinesView.as_view(), name='assign-machines'),
    path('orders/<int:order_id>/send-to-admin/', SendToAdminView.as_view(), name='send-to-admin'),
    path('machine-assignments/<int:assignment_id>/status/', UpdateMachineAssignmentStatusView.as_view(), name='update-machine-status'),
    path('production/machine-queue/', MachineQueueView.as_view(), name='machine-queue'),
    
    # File management endpoints
    path('orders/<int:order_id>/files/upload/', UploadOrderFileView.as_view(), name='upload-order-file'),
    path('orders/<int:order_id>/files/', OrderFilesListView.as_view(), name='order-files-list'),
    path('orders/<int:order_id>/files/<int:file_id>/download/', OrderFileDownloadView.as_view(), name='download-order-file'),
    path('orders/<int:order_id>/files/<int:file_id>/', UpdateOrderFileView.as_view(), name='update-order-file'),
    path('orders/<int:order_id>/files/<int:file_id>/delete/', DeleteOrderFileView.as_view(), name='rename-order-file'),
    
    # Product image serving endpoint
    path('orders/<int:order_id>/items/<int:item_id>/product-image/', ProductImageServeView.as_view(), name='serve-product-image'),
    
    # Design File Management (SECURE)
    path('orders/<int:order_id>/design-files/upload/', DesignFileUploadView.as_view(), name='upload-design-files'),
    path('orders/<int:order_id>/design-files/', DesignFileListView.as_view(), name='list-design-files'),
    path('orders/<int:order_id>/design-files/<int:file_id>/url/', DesignFileUrlView.as_view(), name='get-design-file-url'),
    path('orders/<int:order_id>/design-files/<int:file_id>/download/', DesignFileDownloadView.as_view(), name='download-design-file'),
    path('orders/<int:order_id>/design-files/<int:file_id>/delete/', DesignFileDeleteView.as_view(), name='delete-design-file'),
    
    # Status tracking endpoints
    path('orders/<int:order_id>/status-tracking/', OrderStatusTrackingView.as_view(), name='order-status-tracking'),
    
    # Production-specific endpoints
    path('production/orders/', ProductionOrdersView.as_view(), name='production-orders'),
    path('production/orders/<int:order_id>/', ProductionOrderDetailView.as_view(), name='production-order-detail'),
    
    # Legacy routes for backward compatibility
    path('orders/', OrdersListView.as_view(), name='orders-list-legacy'),
    path('orders/<uuid:id>/', OrderDetailView.as_view(), name='orders-detail-legacy'),
]

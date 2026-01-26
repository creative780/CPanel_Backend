from django.urls import path
from .views import (
    InventoryItemsView, InventoryItemDetailView, InventoryAdjustView,
    MachinesView, MachineDetailView
)

urlpatterns = [
    path('inventory/items', InventoryItemsView.as_view(), name='inventory-items'),
    path('inventory/items/<str:sku>/', InventoryItemDetailView.as_view(), name='inventory-item-detail'),
    path('inventory/adjust', InventoryAdjustView.as_view(), name='inventory-adjust'),
    path('inventory/machines/', MachinesView.as_view(), name='machines'),
    path('inventory/machines/<int:id>/', MachineDetailView.as_view(), name='machine-detail'),
]

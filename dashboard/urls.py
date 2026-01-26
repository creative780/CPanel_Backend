from django.urls import path
from .views import (
    dashboard_kpis, dashboard_recent_activity, salesperson_metrics,
    production_wip_count, production_turnaround_time, production_machine_utilization,
    production_reprint_rate, production_queue, production_jobs_by_stage,
    production_material_usage, production_delivery_handoff, monthly_financial_data,
    monthly_orders_data, lead_source_performance, sales_funnel, win_loss_by_segment,
    designer_kpis, designer_time_spent, designer_order_status,
    dashboard_sales_statistics, dashboard_low_stock_alerts,
    dashboard_attendance_today, dashboard_top_products_week
)

urlpatterns = [
    path('dashboard/kpis/', dashboard_kpis, name='dashboard-kpis'),
    path('dashboard/recent-activity/', dashboard_recent_activity, name='dashboard-recent-activity'),
    path('dashboard/salesperson-metrics/', salesperson_metrics, name='salesperson-metrics'),
    path('dashboard/monthly-financial/', monthly_financial_data, name='dashboard-monthly-financial'),
    path('dashboard/monthly-orders/', monthly_orders_data, name='dashboard-monthly-orders'),
    path('dashboard/lead-source-performance/', lead_source_performance, name='lead-source-performance'),
    path('dashboard/sales-funnel/', sales_funnel, name='sales-funnel'),
    path('dashboard/win-loss-by-segment/', win_loss_by_segment, name='win-loss-by-segment'),
    
    # Production dashboard endpoints
    path('dashboard/production/wip-count/', production_wip_count, name='production-wip-count'),
    path('dashboard/production/turnaround-time/', production_turnaround_time, name='production-turnaround'),
    path('dashboard/production/machine-utilization/', production_machine_utilization, name='production-machine-util'),
    path('dashboard/production/reprint-rate/', production_reprint_rate, name='production-reprint-rate'),
    path('dashboard/production/queue/', production_queue, name='production-queue'),
    path('dashboard/production/jobs-by-stage/', production_jobs_by_stage, name='production-jobs-by-stage'),
    path('dashboard/production/material-usage/', production_material_usage, name='production-material-usage'),
    path('dashboard/production/delivery-handoff/', production_delivery_handoff, name='production-delivery-handoff'),
    
    # Designer dashboard endpoints
    path('dashboard/designer/kpis/', designer_kpis, name='designer-kpis'),
    path('dashboard/designer/time-spent/', designer_time_spent, name='designer-time-spent'),
    path('dashboard/designer/order-status/', designer_order_status, name='designer-order-status'),
    
    # Dashboard card endpoints
    path('dashboard/sales-statistics/', dashboard_sales_statistics, name='dashboard-sales-statistics'),
    path('dashboard/low-stock-alerts/', dashboard_low_stock_alerts, name='dashboard-low-stock-alerts'),
    path('dashboard/attendance-today/', dashboard_attendance_today, name='dashboard-attendance-today'),
    path('dashboard/top-products-week/', dashboard_top_products_week, name='dashboard-top-products-week'),
]

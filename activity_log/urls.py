from django.urls import path

from .views import (
    IngestView,
    ActivityEventListView,
    ActivityEventDetailView,
    ExportStartView,
    ExportStatusView,
    ExportDownloadView,
    MetricsView,
    TypesView,
    PoliciesView,
    PoliciesRunView,
    SummaryView,
    BehaviorMonitoringView,
    ActivityLogMarkReviewedView,
    ActivityLogRelatedActionsView,
    ActivityLogWarningView,
    ScheduledReportListView,
    ScheduledReportDetailView,
    ScheduledReportRunNowView,
)


urlpatterns = [
    path("activity-logs/ingest", IngestView.as_view(), name="activity_ingest"),
    path("activity-logs/", ActivityEventListView.as_view(), name="activity_list"),
    path("activity-logs/<uuid:id>", ActivityEventDetailView.as_view(), name="activity_detail"),
    path("activity-logs/<uuid:id>/mark-reviewed", ActivityLogMarkReviewedView.as_view(), name="activity_mark_reviewed"),
    path("activity-logs/related-actions", ActivityLogRelatedActionsView.as_view(), name="activity_related_actions"),
    path("activity-logs/<uuid:id>/send-warning", ActivityLogWarningView.as_view(), name="activity_send_warning"),
    path("activity-logs/export", ExportStartView.as_view(), name="activity_export_start"),
    path("activity-logs/exports/<int:id>", ExportStatusView.as_view(), name="activity_export_status"),
    path("activity-logs/exports/<int:job_id>/download", ExportDownloadView.as_view(), name="activity_export_download"),
    path("activity-logs/metrics", MetricsView.as_view(), name="activity_metrics"),
    path("activity-logs/summary", SummaryView.as_view(), name="activity_summary"),
    path("activity-logs/behavior-monitoring", BehaviorMonitoringView.as_view(), name="behavior_monitoring"),
    path("activity-logs/types", TypesView.as_view(), name="activity_types"),
    path("activity-logs/policies/retention", PoliciesView.as_view(), name="activity_policies"),
    path("activity-logs/policies/run", PoliciesRunView.as_view(), name="activity_policies_run"),
    path("activity-logs/scheduled-reports/", ScheduledReportListView.as_view(), name="scheduled_reports_list"),
    path("activity-logs/scheduled-reports/<int:id>/", ScheduledReportDetailView.as_view(), name="scheduled_report_detail"),
    path("activity-logs/scheduled-reports/<int:id>/run-now/", ScheduledReportRunNowView.as_view(), name="scheduled_report_run_now"),
]

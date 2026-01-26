from __future__ import annotations

from django.db.models import Q
from django_filters import rest_framework as filters

from .models import ActivityEvent


class ActivityEventFilterSet(filters.FilterSet):
    q = filters.CharFilter(method="filter_q")
    actor_id = filters.CharFilter(method="filter_actor_id")
    actor_role = filters.CharFilter(field_name="actor_role")
    verb = filters.CharFilter(field_name="verb")
    target_type = filters.CharFilter(field_name="target_type")
    target_id = filters.CharFilter(field_name="target_id")
    source = filters.CharFilter(field_name="source")
    severity = filters.CharFilter(method="filter_severity")
    department = filters.CharFilter(method="filter_department")
    tags = filters.CharFilter(method="filter_tags")
    since = filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="gte")
    until = filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="lte")
    tenant_id = filters.CharFilter(field_name="tenant_id")

    class Meta:
        model = ActivityEvent
        fields = []

    def filter_q(self, queryset, name, value):
        # lightweight search across common fields
        return queryset.filter(
            Q(target_id__icontains=value)
            | Q(context__filename__icontains=value)
            | Q(context__comment__icontains=value)
            | Q(context__tags__icontains=value)
        )

    def filter_severity(self, queryset, name, value):
        return queryset.filter(**{"context__severity": value})

    def filter_tags(self, queryset, name, value):
        # value can be comma-separated
        tags = [v.strip() for v in value.split(",") if v.strip()]
        for t in tags:
            queryset = queryset.filter(context__tags__contains=[t])
        return queryset
    
    def filter_department(self, queryset, name, value):
        """Filter by department (maps to actor_role). Supports comma-separated values."""
        if ',' in value:
            # Multiple departments
            departments = [v.strip() for v in value.split(",") if v.strip()]
            return queryset.filter(actor_role__in=departments)
        else:
            return queryset.filter(actor_role=value.strip())
    
    def filter_actor_id(self, queryset, name, value):
        """Filter by actor_id. Supports comma-separated values."""
        if ',' in value:
            # Multiple actor IDs
            actor_ids = [v.strip() for v in value.split(",") if v.strip()]
            return queryset.filter(actor_id__in=actor_ids)
        else:
            return queryset.filter(actor_id=value.strip())


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from django.db.models import Count, Sum, Q
from django.db.models.functions import Extract
from django.utils import timezone
from datetime import timedelta, datetime, time
from calendar import month_abbr
from drf_spectacular.utils import extend_schema
from accounts.permissions import RolePermission
from clients.models import Lead, Client
from orders.models import Order, Quotation, ProductMachineAssignment, DesignApproval, DesignStage, DeliveryStage, OrderItem
from inventory.models import InventoryMovement, InventoryItem
from monitoring.models import Employee
from attendance.models import Attendance


@extend_schema(
    operation_id='dashboard_kpis',
    summary='Get dashboard KPIs',
    description='Returns key performance indicators for the dashboard',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def dashboard_kpis(request):
    """Get dashboard KPIs"""
    # Get date ranges
    now = timezone.now()
    today = now.date()
    this_month = now.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Leads KPIs
    total_leads = Lead.objects.count()
    new_leads_today = Lead.objects.filter(created_at__date=today).count()
    won_leads_this_month = Lead.objects.filter(
        stage='won',
        created_at__gte=this_month
    ).count()
    won_leads_last_month = Lead.objects.filter(
        stage='won',
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    
    # Orders KPIs
    total_orders = Order.objects.count()
    orders_this_month = Order.objects.filter(created_at__gte=this_month).count()
    orders_last_month = Order.objects.filter(
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    
    # Revenue KPIs (from won leads)
    revenue_this_month = Lead.objects.filter(
        stage='won',
        created_at__gte=this_month
    ).aggregate(total=Sum('value'))['total'] or 0
    
    revenue_last_month = Lead.objects.filter(
        stage='won',
        created_at__gte=last_month,
        created_at__lt=this_month
    ).aggregate(total=Sum('value'))['total'] or 0
    
    # Calculate growth rates
    lead_growth = 0
    if won_leads_last_month > 0:
        lead_growth = ((won_leads_this_month - won_leads_last_month) / won_leads_last_month) * 100
    
    order_growth = 0
    if orders_last_month > 0:
        order_growth = ((orders_this_month - orders_last_month) / orders_last_month) * 100
    
    revenue_growth = 0
    if revenue_last_month > 0:
        revenue_growth = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
    
    return Response({
        'leads': {
            'total': total_leads,
            'new_today': new_leads_today,
            'won_this_month': won_leads_this_month,
            'growth_rate': round(lead_growth, 1)
        },
        'orders': {
            'total': total_orders,
            'this_month': orders_this_month,
            'growth_rate': round(order_growth, 1)
        },
        'revenue': {
            'this_month': float(revenue_this_month),
            'growth_rate': round(revenue_growth, 1)
        },
        'employees': {
            'total': Employee.objects.count(),
            'active': Employee.objects.filter(status='active').count()
        }
    })


@extend_schema(
    operation_id='dashboard_recent_activity',
    summary='Get recent activity',
    description='Returns recent activity for the dashboard',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def dashboard_recent_activity(request):
    """Get recent activity"""
    # Recent leads
    recent_leads = Lead.objects.select_related('org', 'contact', 'owner').order_by('-created_at')[:5]
    leads_data = []
    for lead in recent_leads:
        leads_data.append({
            'id': lead.id,
            'title': lead.title or f"Lead for {lead.org.name if lead.org else 'Unknown'}",
            'stage': lead.stage,
            'value': float(lead.value),
            'created_at': lead.created_at,
            'owner': lead.owner.username if lead.owner else None,
            'org_name': lead.org.name if lead.org else None
        })
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]
    orders_data = []
    for order in recent_orders:
        orders_data.append({
            'id': order.id,
            'title': order.order_code,
            'stage': order.stage,
            'status': order.status,
            'created_at': order.created_at,
            'client_name': getattr(order, 'client_name', None)
        })
    
    # Recent clients
    recent_clients = Client.objects.select_related('org', 'account_owner').order_by('-created_at')[:5]
    clients_data = []
    for client in recent_clients:
        clients_data.append({
            'id': client.id,
            'name': client.org.name,
            'status': client.status,
            'created_at': client.created_at,
            'account_owner': client.account_owner.username if client.account_owner else None
        })
    
    return Response({
        'leads': leads_data,
        'orders': orders_data,
        'clients': clients_data
    })


@extend_schema(
    operation_id='lead_source_performance',
    summary='Get lead source performance',
    description='Returns lead counts grouped by source with MQL, SQL, and Won breakdowns',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def lead_source_performance(request):
    """Get lead source performance data"""
    # Define the sources we want to track
    sources = ['Google Ads', 'Organic', 'Referrals', 'Social', 'Email']
    
    # Get all leads
    all_leads = Lead.objects.all()
    
    # Initialize result structure
    result = {}
    
    for source in sources:
        # Filter leads by source (case-insensitive match)
        source_leads = all_leads.filter(source__iexact=source)
        
        # MQL (Marketing Qualified Leads): All leads from this source
        mql_count = source_leads.count()
        
        # SQL (Sales Qualified Leads): Leads in proposal, negotiation, or won stages
        sql_count = source_leads.filter(
            stage__in=['proposal', 'negotiation', 'won']
        ).count()
        
        # Won: Leads that closed successfully
        won_count = source_leads.filter(stage='won').count()
        
        result[source] = {
            'mql': mql_count,
            'sql': sql_count,
            'won': won_count
        }
    
    # Also include any other sources that exist in the data
    # Build Q objects for case-insensitive exclusion
    exclude_q = Q()
    for source in sources:
        exclude_q |= Q(source__iexact=source)
    other_sources = all_leads.exclude(exclude_q).exclude(source='').values_list('source', flat=True).distinct()
    
    for source in other_sources:
        if source:  # Skip empty sources
            source_leads = all_leads.filter(source__iexact=source)
            result[source] = {
                'mql': source_leads.count(),
                'sql': source_leads.filter(stage__in=['proposal', 'negotiation', 'won']).count(),
                'won': source_leads.filter(stage='won').count()
            }
    
    return Response(result)


@extend_schema(
    operation_id='sales_funnel',
    summary='Get sales funnel data',
    description='Returns lead counts grouped by sales stage',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def sales_funnel(request):
    """Get sales funnel data by stage"""
    # Map backend stages to frontend labels
    stage_mapping = {
        'new': 'Prospects',
        'contacted': 'Qualified',
        'proposal': 'Proposal',
        'negotiation': 'Negotiation',
        'won': 'Won'
    }
    
    # Count leads by stage
    result = {}
    for stage_key, stage_label in stage_mapping.items():
        count = Lead.objects.filter(stage=stage_key).count()
        result[stage_label] = count
    
    return Response(result)


@extend_schema(
    operation_id='win_loss_by_segment',
    summary='Get Win/Loss by Segment',
    description='Returns win and loss counts grouped by segment (SMB and Enterprise)',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def win_loss_by_segment(request):
    """Get win/loss counts by segment"""
    # Query leads grouped by segment and stage
    # Only count leads that have a segment assigned and are in 'won' or 'lost' stage
    smb_win = Lead.objects.filter(segment='smb', stage='won').count()
    smb_loss = Lead.objects.filter(segment='smb', stage='lost').count()
    enterprise_win = Lead.objects.filter(segment='enterprise', stage='won').count()
    enterprise_loss = Lead.objects.filter(segment='enterprise', stage='lost').count()
    
    return Response({
        'smb_win': smb_win,
        'smb_loss': smb_loss,
        'enterprise_win': enterprise_win,
        'enterprise_loss': enterprise_loss
    })


@extend_schema(
    operation_id='salesperson_metrics',
    summary='Get salesperson metrics',
    description='Returns financial metrics for the current salesperson including total revenue, pending payments, total orders, and delivered orders',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def salesperson_metrics(request):
    """Get salesperson-specific financial metrics"""
    username = request.user.username
    
    # Base queryset: orders assigned to this salesperson
    orders = Order.objects.filter(assigned_sales_person=username)
    
    # Total Revenue: Sum of grand_total from quotations for completed/delivered orders
    completed_orders = orders.filter(
        Q(status__in=['completed', 'delivered']) | Q(delivered_at__isnull=False)
    )
    total_revenue = Quotation.objects.filter(
        order__in=completed_orders
    ).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Pending Payments: Sum of grand_total from quotations for incomplete orders
    incomplete_orders = orders.exclude(
        Q(status__in=['completed', 'delivered']) | Q(delivered_at__isnull=False)
    )
    pending_payments = Quotation.objects.filter(
        order__in=incomplete_orders
    ).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Total Orders: Count of all orders assigned to this salesperson
    total_orders = orders.count()
    
    # Delivered Orders: Count of delivered orders
    delivered_orders = orders.filter(
        Q(status='delivered') | Q(delivered_at__isnull=False)
    ).count()
    
    return Response({
        'total_revenue': float(total_revenue),
        'pending_payments': float(pending_payments),
        'total_orders': total_orders,
        'delivered_orders': delivered_orders
    })


# ========== Production Dashboard Endpoints ==========

@extend_schema(
    operation_id='production_wip_count',
    summary='Get Production WIP Count',
    description='Returns current work in progress count and change vs yesterday',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_wip_count(request):
    """Get current WIP count and change vs yesterday"""
    # Filter for production orders - count ALL current WIP orders
    production_filter = Q(status__in=['sent_to_production', 'getting_ready']) | Q(stage__in=['production', 'printing'])
    
    # Current WIP count (all orders currently in production)
    current_count = Order.objects.filter(production_filter).count()
    
    # Get yesterday's count by checking orders that were in production yesterday
    # We'll use a snapshot approach: count orders that entered production before today
    # and haven't been delivered yet
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    
    # Orders that were in production at end of yesterday (entered before today, still in production)
    yesterday_wip = Order.objects.filter(
        production_filter,
        created_at__lt=today_start  # Entered production before today
    ).exclude(
        status__in=['delivered', 'sent_for_delivery']  # Exclude completed orders
    ).count()
    
    # Alternative: Count orders that were updated yesterday and are still in production
    # This is more accurate for tracking day-over-day changes
    yesterday_updated = Order.objects.filter(
        production_filter,
        updated_at__date=yesterday_start.date()
    ).count()
    
    # Use the more conservative approach: current count vs orders that were active yesterday
    # For change calculation, compare with orders that were in WIP at end of yesterday
    change = current_count - yesterday_wip
    change_direction = 'up' if change >= 0 else 'down'
    
    return Response({
        'current': current_count,
        'change': abs(change),
        'change_direction': change_direction
    })


@extend_schema(
    operation_id='production_turnaround_time',
    summary='Get Production Turnaround Time',
    description='Returns average turnaround time for last 7 days',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_turnaround_time(request):
    """Get average turnaround time for last 7 days"""
    last_7_days = timezone.now() - timedelta(days=7)
    
    completed_orders = Order.objects.filter(
        delivered_at__gte=last_7_days,
        delivered_at__isnull=False,
        created_at__isnull=False
    ).defer('client')  # Exclude client field to avoid client_id column error
    
    turnaround_times = []
    for order in completed_orders:
        if order.delivered_at and order.created_at:
            # Ensure both are timezone-aware
            delivered = order.delivered_at
            created = order.created_at
            
            # Make sure delivered_at is after created_at (logical validation)
            if delivered > created:
                delta = delivered - created
                days = delta.total_seconds() / 86400
                # Double-check: only add positive values (with small tolerance for rounding)
                if days > 0.01:  # Allow small positive values, filter out near-zero
                    turnaround_times.append(days)
    
    # Calculate average, ensuring it's never negative
    if turnaround_times:
        avg_turnaround = sum(turnaround_times) / len(turnaround_times)
        # Safety check: ensure result is never negative (absolute safety)
        avg_turnaround = max(0.0, float(avg_turnaround))
    else:
        avg_turnaround = 0.0
    
    # Final safety check before returning
    avg_turnaround = max(0.0, round(avg_turnaround, 1))
    
    return Response({
        'average_days': avg_turnaround,
        'period': 'last_7_days'
    })


@extend_schema(
    operation_id='production_machine_utilization',
    summary='Get Machine Utilization',
    description='Returns machine utilization percentages for today',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_machine_utilization(request):
    """Get machine utilization percentages for today"""
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    now = timezone.now()
    
    # Get all assignments that are active today (started today or in progress)
    assignments = ProductMachineAssignment.objects.filter(
        Q(started_at__gte=today_start) |  # Started today
        Q(status='in_progress', started_at__isnull=False)  # Currently in progress (started before today)
    )
    
    # Group by machine
    machine_stats = {}
    for assignment in assignments:
        machine_id = assignment.machine_id
        if machine_id not in machine_stats:
            machine_stats[machine_id] = {
                'name': assignment.machine_name,
                'active_minutes': 0,
                'peak_utilization': 0
            }
        
        # Calculate actual time used
        if assignment.completed_at and assignment.started_at:
            # Completed assignment - use actual completion time
            if assignment.completed_at.date() == today:
                # Only count time within today
                start_time = max(assignment.started_at, today_start)
                actual_minutes = (assignment.completed_at - start_time).total_seconds() / 60
            else:
                # Completed before today, count full estimated time if it was today's work
                if assignment.started_at.date() == today:
                    actual_minutes = (now - assignment.started_at).total_seconds() / 60
                else:
                    actual_minutes = 0  # Not today's work
        elif assignment.started_at:
            # In progress - use elapsed time today only
            if assignment.started_at.date() == today:
                elapsed = (now - assignment.started_at).total_seconds() / 60
                # Add remaining estimated time
                remaining = max(0, assignment.estimated_time_minutes - elapsed)
                actual_minutes = elapsed + remaining
            else:
                # Started before today, only count today's portion
                elapsed_today = (now - today_start).total_seconds() / 60
                # Estimate remaining time based on original estimate
                if assignment.estimated_time_minutes:
                    # Assume it should complete soon, use remaining estimate
                    remaining = max(0, assignment.estimated_time_minutes - elapsed_today)
                    actual_minutes = elapsed_today + remaining
                else:
                    actual_minutes = elapsed_today
        else:
            # Not started yet - don't count in utilization (queued items)
            actual_minutes = 0
        
        machine_stats[machine_id]['active_minutes'] += actual_minutes
    
    # Calculate utilization (assuming 8-hour workday = 480 minutes)
    available_minutes = 480
    result = []
    peak_utilization = 0
    
    for machine_id, stats in machine_stats.items():
        utilization = (stats['active_minutes'] / available_minutes) * 100
        peak_utilization = max(peak_utilization, utilization)
        result.append({
            'machine_id': machine_id,
            'machine_name': stats['name'],
            'utilization_percent': round(utilization, 1)
        })
    
    # Overall average
    overall_avg = sum(r['utilization_percent'] for r in result) / len(result) if result else 0
    
    return Response({
        'overall_utilization': round(overall_avg, 1),
        'peak_today': round(peak_utilization, 1),
        'machines': result
    })


@extend_schema(
    operation_id='production_reprint_rate',
    summary='Get Reprint Rate',
    description='Returns reprint rate with week-over-week change',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_reprint_rate(request):
    """Get reprint rate with WoW change"""
    now = timezone.now()
    # Get start of this week (Monday)
    days_since_monday = now.weekday()
    this_week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    last_week_start = this_week_start - timedelta(days=7)
    
    # This week
    this_week_orders = Order.objects.filter(created_at__gte=this_week_start)
    this_week_total = this_week_orders.count()
    this_week_reprints = this_week_orders.filter(is_reprint=True).count()
    this_week_rate = (this_week_reprints / this_week_total * 100) if this_week_total > 0 else 0
    
    # Last week
    last_week_orders = Order.objects.filter(
        created_at__gte=last_week_start,
        created_at__lt=this_week_start
    )
    last_week_total = last_week_orders.count()
    last_week_reprints = last_week_orders.filter(is_reprint=True).count()
    last_week_rate = (last_week_reprints / last_week_total * 100) if last_week_total > 0 else 0
    
    change = this_week_rate - last_week_rate
    change_direction = 'down' if change < 0 else 'up'
    
    return Response({
        'current_rate': round(this_week_rate, 1),
        'change': round(abs(change), 1),
        'change_direction': change_direction
    })


@extend_schema(
    operation_id='production_queue',
    summary='Get Production Queue',
    description='Returns production queue table data with ETA and stage information',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_queue(request):
    """Get production queue table data"""
    assignments = ProductMachineAssignment.objects.filter(
        status__in=['queued', 'in_progress']
    ).select_related('order').defer('order__client').order_by(
        'status',  # In progress first, then queued
        'started_at',  # Then by start time
        'id'  # Finally by ID for consistency
    )
    
    queue_items = []
    now = timezone.now()
    
    for assignment in assignments:
        # Calculate ETA
        if assignment.started_at:
            # Already started - ETA is start time + estimated time
            eta = assignment.started_at + timedelta(minutes=assignment.estimated_time_minutes)
        else:
            # Not started yet - ETA is current time + estimated time
            eta = now + timedelta(minutes=assignment.estimated_time_minutes)
        
        # Format ETA
        eta_date = eta.date()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        
        if eta_date == today:
            eta_str = f"Today {eta.strftime('%H:%M')}"
        elif eta_date == tomorrow:
            eta_str = f"Tomorrow {eta.strftime('%H:%M')}"
        else:
            eta_str = eta.strftime('%Y-%m-%d %H:%M')
        
        # Map status to stage name - try to get actual stage from order if available
        stage_mapping = {
            'queued': 'Queued',
            'in_progress': 'Printing',
            'completed': 'Completed',
            'on_hold': 'On Hold'
        }
        stage = stage_mapping.get(assignment.status, assignment.status.replace('_', ' ').title())
        
        # Try to get more specific stage from order
        order = assignment.order
        if order.stage == 'printing':
            if assignment.status == 'in_progress':
                stage = 'Printing'
            elif assignment.status == 'queued':
                stage = 'Queued'
        
        queue_items.append({
            'order_code': assignment.order.order_code,
            'job': assignment.product_name,
            'machine': assignment.machine_name,
            'eta': eta_str,
            'stage': stage
        })
    
    return Response(queue_items)


@extend_schema(
    operation_id='production_jobs_by_stage',
    summary='Get Jobs by Stage',
    description='Returns job counts grouped by production stage',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_jobs_by_stage(request):
    """Get job counts by production stage"""
    # Initialize stage counts
    stage_counts = {
        'Printing': 0,
        'Cutting': 0,
        'Lamination': 0,
        'Mounting': 0,
        'QA': 0
    }
    
    # Get active assignments
    assignments = ProductMachineAssignment.objects.filter(
        status__in=['queued', 'in_progress']
    ).select_related('order').defer('order__client')  # Exclude client field to avoid client_id column error
    
    # Map machine types to production stages
    # This is a simplified mapping - can be enhanced based on actual machine types
    machine_stage_mapping = {
        'printer': 'Printing',
        'cutter': 'Cutting',
        'laminator': 'Lamination',
        'mounting': 'Mounting',
        'qa': 'QA',
    }
    
    for assignment in assignments:
        # Try to determine stage from machine name/type
        machine_name_lower = assignment.machine_name.lower()
        stage_found = False
        
        # Check machine name for keywords
        if any(keyword in machine_name_lower for keyword in ['printer', 'print', 'latex', 'epson', 'mimaki', 'hp']):
            stage_counts['Printing'] += 1
            stage_found = True
        elif any(keyword in machine_name_lower for keyword in ['cutter', 'cut', 'summa']):
            stage_counts['Cutting'] += 1
            stage_found = True
        elif any(keyword in machine_name_lower for keyword in ['lamination', 'laminate', 'laminator']):
            stage_counts['Lamination'] += 1
            stage_found = True
        elif any(keyword in machine_name_lower for keyword in ['mount', 'mounting']):
            stage_counts['Mounting'] += 1
            stage_found = True
        elif any(keyword in machine_name_lower for keyword in ['qa', 'quality', 'inspection']):
            stage_counts['QA'] += 1
            stage_found = True
        
        # If no specific stage found, use status-based mapping
        if not stage_found:
            if assignment.status == 'in_progress':
                stage_counts['Printing'] += 1
            else:  # queued
                stage_counts['Printing'] += 1
    
    return Response(stage_counts)


@extend_schema(
    operation_id='production_material_usage',
    summary='Get Material Usage',
    description='Returns material consumption for last 7 days',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_material_usage(request):
    """Get material usage for last 7 days"""
    last_7_days = timezone.now() - timedelta(days=7)
    
    # Get all production-relevant materials (raw materials, consumables, supplies)
    # This ensures we show all relevant materials, even if they haven't been used recently
    production_materials = InventoryItem.objects.filter(
        category__in=['raw_materials', 'consumables', 'supplies']
    ).order_by('name')
    
    # Get consumption movements (negative deltas) in the last 7 days
    movements = InventoryMovement.objects.filter(
        created_at__gte=last_7_days,
        delta__lt=0
    )
    
    # Create a dictionary to track usage by SKU
    usage_by_sku = {}
    for movement in movements:
        if movement.sku not in usage_by_sku:
            usage_by_sku[movement.sku] = 0
        usage_by_sku[movement.sku] += abs(movement.delta)
    
    # Build result list with all production materials
    result = []
    processed_skus = set()  # Track which SKUs we've already processed
    
    for item in production_materials:
        used = usage_by_sku.get(item.sku, 0)
        result.append({
            'material': item.name,
            'used': used,
            'reorder_threshold': item.minimum_stock
        })
        processed_skus.add(item.sku)
    
    # Also include any materials from movements that don't have InventoryItem records
    # (for backward compatibility)
    for sku, used_qty in usage_by_sku.items():
        if sku not in processed_skus:
            # This SKU doesn't have an InventoryItem, add it with SKU as name
            result.append({
                'material': sku,
                'used': used_qty,
                'reorder_threshold': 0
            })
            processed_skus.add(sku)
    
    # Sort by usage (descending) to show most used materials first
    result.sort(key=lambda x: x['used'], reverse=True)
    
    return Response(result)


@extend_schema(
    operation_id='production_delivery_handoff',
    summary='Get Delivery Handoff',
    description='Returns orders ready for delivery',
    tags=['Dashboard', 'Production']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def production_delivery_handoff(request):
    """Get orders ready for delivery"""
    ready_orders = Order.objects.filter(
        status='sent_for_delivery'
    ).prefetch_related('items').order_by('-updated_at')[:10]
    
    result = []
    for order in ready_orders:
        # Get package info from order items
        items = order.items.all()
        package_info = f"{items.count()} item(s)"
        if items.exists():
            item_names = [item.name for item in items[:3]]
            if len(items) > 3:
                item_names.append(f"+{len(items) - 3} more")
            package_info = ", ".join(item_names)
        
        delivery_code = order.delivery_code or f"#DLV-{order.id:06d}"
        
        result.append({
            'order_code': order.order_code,
            'title': order.client_name,
            'package_info': package_info,
            'delivery_code': delivery_code
        })
    
    return Response(result)


@extend_schema(
    operation_id='monthly_financial_data',
    summary='Get Monthly Financial Data',
    description='Returns monthly income and expenses data for the current year',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def monthly_financial_data(request):
    """Get monthly income and expenses data for the current year"""
    now = timezone.now()
    current_year = now.year
    previous_year = current_year - 1
    
    # Get start and end of current year
    year_start = timezone.make_aware(datetime(current_year, 1, 1))
    year_end = timezone.make_aware(datetime(current_year + 1, 1, 1))
    
    # Get start and end of previous year
    prev_year_start = timezone.make_aware(datetime(previous_year, 1, 1))
    prev_year_end = timezone.make_aware(datetime(previous_year + 1, 1, 1))
    
    # Get all quotations with their orders for the current year only
    # Filter by both year start and end to ensure we only get current year data
    quotations = Quotation.objects.filter(
        order__created_at__gte=year_start,
        order__created_at__lt=year_end
    ).select_related('order').defer('order__client')  # Exclude client field to avoid client_id column error
    
    # Get quotations for previous year for growth rate calculations
    prev_quotations = Quotation.objects.filter(
        order__created_at__gte=prev_year_start,
        order__created_at__lt=prev_year_end
    ).select_related('order').defer('order__client')  # Exclude client field to avoid client_id column error
    
    # Initialize monthly data arrays (12 months)
    month_labels = []
    income_data = [0.0] * 12
    expenses_data = [0.0] * 12
    
    # Aggregate income (grand_total) and expenses (subtotal = products + operational costs) by month
    # Income: Sum of grand_total grouped by month
    # Note: We already filtered by date range above, so all quotations are from current year
    income_by_month = quotations.annotate(
        month=Extract('order__created_at', 'month')
    ).values('month').annotate(
        total_income=Sum('grand_total')
    ).order_by('month')
    
    # Expenses: Sum of subtotal (products_subtotal + other_subtotal) grouped by month
    # This includes both product costs and operational costs
    expenses_by_month = quotations.annotate(
        month=Extract('order__created_at', 'month')
    ).values('month').annotate(
        total_expenses=Sum('subtotal')
    ).order_by('month')
    
    # Populate income data
    for item in income_by_month:
        month_num = item['month']
        if 1 <= month_num <= 12:
            # Ensure we handle None values from Sum() aggregation
            income_value = item['total_income']
            income_data[month_num - 1] = float(income_value) if income_value is not None else 0.0
    
    # Populate expenses data
    for item in expenses_by_month:
        month_num = item['month']
        if 1 <= month_num <= 12:
            # Ensure we handle None values from Sum() aggregation
            expenses_value = item['total_expenses']
            expenses_data[month_num - 1] = float(expenses_value) if expenses_value is not None else 0.0
    
    # Calculate totals for current year
    total_income = sum(income_data)
    total_expenses = sum(expenses_data)
    total_net_income = total_income - total_expenses
    
    # Calculate totals for previous year
    prev_total_income = prev_quotations.aggregate(
        total=Sum('grand_total')
    )['total'] or 0.0
    prev_total_expenses = prev_quotations.aggregate(
        total=Sum('subtotal')
    )['total'] or 0.0
    prev_total_net_income = float(prev_total_income) - float(prev_total_expenses)
    
    # Calculate growth rates
    income_growth_rate = 0.0
    if prev_total_income > 0:
        income_growth_rate = ((total_income - float(prev_total_income)) / float(prev_total_income)) * 100
    
    expenses_growth_rate = 0.0
    if prev_total_expenses > 0:
        expenses_growth_rate = ((total_expenses - float(prev_total_expenses)) / float(prev_total_expenses)) * 100
    
    net_income_growth_rate = 0.0
    if prev_total_net_income != 0:
        net_income_growth_rate = ((total_net_income - prev_total_net_income) / abs(prev_total_net_income)) * 100
    
    # Generate month labels
    month_labels = [month_abbr[i] for i in range(1, 13)]
    
    return Response({
        'months': month_labels,
        'income': income_data,
        'expenses': expenses_data,
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'total_net_income': float(total_net_income),
        'income_growth_rate': round(income_growth_rate, 1),
        'expenses_growth_rate': round(expenses_growth_rate, 1),
        'net_income_growth_rate': round(net_income_growth_rate, 1)
    })


@extend_schema(
    operation_id='monthly_orders_data',
    summary='Get Monthly Orders Data',
    description='Returns monthly order counts for the current year',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def monthly_orders_data(request):
    """Get monthly order counts for the current year"""
    now = timezone.now()
    current_year = now.year
    previous_year = current_year - 1
    
    # Get start and end of current year
    year_start = timezone.make_aware(datetime(current_year, 1, 1))
    year_end = timezone.make_aware(datetime(current_year + 1, 1, 1))
    
    # Get start and end of previous year
    prev_year_start = timezone.make_aware(datetime(previous_year, 1, 1))
    prev_year_end = timezone.make_aware(datetime(previous_year + 1, 1, 1))
    
    # Get all orders for the current year
    current_year_orders = Order.objects.filter(
        created_at__gte=year_start,
        created_at__lt=year_end
    )
    
    # Get all orders for previous year
    prev_year_orders = Order.objects.filter(
        created_at__gte=prev_year_start,
        created_at__lt=prev_year_end
    )
    
    # Initialize monthly data array (12 months)
    orders_data = [0] * 12
    
    # Count orders by month for current year
    orders_by_month = current_year_orders.annotate(
        month=Extract('created_at', 'month')
    ).values('month').annotate(
        order_count=Count('id')
    ).order_by('month')
    
    # Populate orders data
    for item in orders_by_month:
        month_num = item['month']
        if 1 <= month_num <= 12:
            orders_data[month_num - 1] = item['order_count']
    
    # Calculate total orders for current year
    total_orders = current_year_orders.count()
    
    # Calculate total orders for previous year
    prev_total_orders = prev_year_orders.count()
    
    # Calculate growth rate
    growth_rate = 0.0
    if prev_total_orders > 0:
        growth_rate = ((total_orders - prev_total_orders) / prev_total_orders) * 100
    
    # Generate month labels
    month_labels = [month_abbr[i] for i in range(1, 13)]
    
    return Response({
        'months': month_labels,
        'orders': orders_data,
        'total_orders': total_orders,
        'growth_rate': round(growth_rate, 1)
    })


# ========== Designer Dashboard Endpoints ==========

@extend_schema(
    operation_id='designer_kpis',
    summary='Get Designer KPIs',
    description='Returns key performance indicators for designer dashboard',
    tags=['Dashboard', 'Designer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def designer_kpis(request):
    """Get designer-specific KPIs"""
    username = request.user.username
    
    # Base queryset: orders assigned to this designer or in design stage
    designer_orders = Order.objects.filter(
        Q(assigned_designer=username) | 
        Q(status='sent_to_designer') |
        Q(stage='design')
    ).distinct()
    
    # Active orders: orders currently in design stage
    active_orders = designer_orders.filter(
        Q(status='sent_to_designer') | Q(stage='design')
    ).exclude(
        status__in=['sent_to_production', 'delivered', 'completed']
    ).count()
    
    # Orders due this week (orders created this week that are still active)
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)
    due_this_week = designer_orders.filter(
        created_at__date__gte=week_start,
        created_at__date__lt=week_end
    ).exclude(
        status__in=['sent_to_production', 'delivered', 'completed']
    ).count()
    
    # Pending feedback: orders awaiting approval
    pending_feedback = designer_orders.filter(
        status='sent_for_approval'
    ).count()
    
    # Average revisions per order: count design approvals per order
    orders_with_approvals = designer_orders.filter(
        design_approvals__isnull=False
    ).distinct()
    
    total_revisions = DesignApproval.objects.filter(
        order__in=designer_orders,
        designer=username
    ).count()
    
    avg_revisions = 0.0
    if orders_with_approvals.count() > 0:
        avg_revisions = total_revisions / orders_with_approvals.count()
    
    # Calculate change vs last month
    now = timezone.now()
    this_month = now.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    avg_revisions_this_month = 0.0
    orders_this_month = designer_orders.filter(
        created_at__gte=this_month,
        design_approvals__isnull=False
    ).distinct()
    revisions_this_month = DesignApproval.objects.filter(
        order__in=orders_this_month,
        designer=username,
        submitted_at__gte=this_month
    ).count()
    if orders_this_month.count() > 0:
        avg_revisions_this_month = revisions_this_month / orders_this_month.count()
    
    avg_revisions_last_month = 0.0
    orders_last_month = designer_orders.filter(
        created_at__gte=last_month,
        created_at__lt=this_month,
        design_approvals__isnull=False
    ).distinct()
    revisions_last_month = DesignApproval.objects.filter(
        order__in=orders_last_month,
        designer=username,
        submitted_at__gte=last_month,
        submitted_at__lt=this_month
    ).count()
    if orders_last_month.count() > 0:
        avg_revisions_last_month = revisions_last_month / orders_last_month.count()
    
    revision_change = avg_revisions_this_month - avg_revisions_last_month
    
    # On-time delivery: percentage of orders delivered on or before expected date
    delivered_orders = designer_orders.filter(
        status__in=['delivered', 'completed'],
        delivered_at__isnull=False
    )
    
    on_time_count = 0
    total_delivered = delivered_orders.count()
    
    for order in delivered_orders:
        try:
            delivery_stage = order.delivery_stage
            if delivery_stage and delivery_stage.expected_delivery_date and order.delivered_at:
                expected_date = delivery_stage.expected_delivery_date
                delivered_date = order.delivered_at.date()
                if delivered_date <= expected_date:
                    on_time_count += 1
        except:
            pass
    
    on_time_delivery = (on_time_count / total_delivered * 100) if total_delivered > 0 else 0.0
    
    # Calculate on-time delivery change vs last month
    delivered_this_month = designer_orders.filter(
        status__in=['delivered', 'completed'],
        delivered_at__gte=this_month,
        delivered_at__isnull=False
    )
    on_time_this_month = 0
    total_delivered_this_month = delivered_this_month.count()
    for order in delivered_this_month:
        try:
            delivery_stage = order.delivery_stage
            if delivery_stage and delivery_stage.expected_delivery_date and order.delivered_at:
                if order.delivered_at.date() <= delivery_stage.expected_delivery_date:
                    on_time_this_month += 1
        except:
            pass
    on_time_rate_this_month = (on_time_this_month / total_delivered_this_month * 100) if total_delivered_this_month > 0 else 0.0
    
    delivered_last_month = designer_orders.filter(
        status__in=['delivered', 'completed'],
        delivered_at__gte=last_month,
        delivered_at__lt=this_month,
        delivered_at__isnull=False
    )
    on_time_last_month = 0
    total_delivered_last_month = delivered_last_month.count()
    for order in delivered_last_month:
        try:
            delivery_stage = order.delivery_stage
            if delivery_stage and delivery_stage.expected_delivery_date and order.delivered_at:
                if order.delivered_at.date() <= delivery_stage.expected_delivery_date:
                    on_time_last_month += 1
        except:
            pass
    on_time_rate_last_month = (on_time_last_month / total_delivered_last_month * 100) if total_delivered_last_month > 0 else 0.0
    
    on_time_change = on_time_rate_this_month - on_time_rate_last_month
    
    return Response({
        'active_orders': active_orders,
        'due_this_week': due_this_week,
        'pending_feedback': pending_feedback,
        'avg_revisions': round(avg_revisions, 1),
        'revision_change': round(revision_change, 1),
        'revision_change_direction': 'down' if revision_change < 0 else 'up',
        'on_time_delivery': round(on_time_delivery, 1),
        'on_time_change': round(abs(on_time_change), 1),
        'on_time_change_direction': 'up' if on_time_change > 0 else 'down'
    })


@extend_schema(
    operation_id='designer_time_spent',
    summary='Get Designer Time Spent by Order',
    description='Returns time spent on orders for the designer',
    tags=['Dashboard', 'Designer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def designer_time_spent(request):
    """Get time spent by order for designer"""
    username = request.user.username
    
    # Get orders assigned to this designer
    designer_orders = Order.objects.filter(
        Q(assigned_designer=username) | 
        Q(status='sent_to_designer') |
        Q(stage='design')
    ).distinct().exclude(
        status__in=['draft']
    ).order_by('-updated_at')[:10]  # Top 10 most recent
    
    result = []
    for order in designer_orders:
        # Calculate time spent: difference between when order entered design and when it left (or now)
        # Use design_stage created_at as start, and updated_at or sent_to_production time as end
        try:
            design_stage = order.design_stage
            start_time = design_stage.created_at if design_stage else order.created_at
        except:
            start_time = order.created_at
        
        # End time: when order moved to production, or current time if still in design
        if order.status in ['sent_to_production', 'getting_ready', 'sent_for_delivery', 'delivered', 'completed']:
            # Find when it transitioned - use updated_at as approximation
            end_time = order.updated_at
        else:
            end_time = timezone.now()
        
        # Calculate hours
        if start_time and end_time:
            delta = end_time - start_time
            hours = delta.total_seconds() / 3600
        else:
            hours = 0
        
        # Get order title from order_code or client_name
        order_title = order.order_code or order.client_name
        
        result.append({
            'order_code': order.order_code,
            'title': order_title,
            'hours': round(hours, 1),
            'client_name': order.client_name
        })
    
    # Sort by hours descending
    result.sort(key=lambda x: x['hours'], reverse=True)
    
    return Response(result[:5])  # Return top 5


@extend_schema(
    operation_id='designer_order_status',
    summary='Get Designer Order Status Distribution',
    description='Returns order counts grouped by status for designer',
    tags=['Dashboard', 'Designer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def designer_order_status(request):
    """Get order status distribution for designer"""
    username = request.user.username
    
    # Get orders assigned to this designer
    designer_orders = Order.objects.filter(
        Q(assigned_designer=username) | 
        Q(status='sent_to_designer') |
        Q(stage='design')
    ).distinct()
    
    # Count by status categories
    in_progress = designer_orders.filter(
        Q(status='sent_to_designer') | Q(stage='design')
    ).exclude(
        status__in=['sent_to_production', 'delivered', 'completed', 'sent_for_approval']
    ).count()
    
    awaiting_feedback = designer_orders.filter(
        status='sent_for_approval'
    ).count()
    
    # Revisions: orders with multiple design approvals
    orders_with_revisions = designer_orders.filter(
        design_approvals__isnull=False
    ).annotate(
        revision_count=Count('design_approvals')
    ).filter(
        revision_count__gt=1
    ).count()
    
    # Completed: orders that moved to production or beyond
    completed = designer_orders.filter(
        status__in=['sent_to_production', 'getting_ready', 'sent_for_delivery', 'delivered', 'completed']
    ).count()
    
    return Response({
        'in_progress': in_progress,
        'awaiting_feedback': awaiting_feedback,
        'revisions': orders_with_revisions,
        'completed': completed
    })


@extend_schema(
    operation_id='dashboard_sales_statistics',
    summary='Get Sales Statistics',
    description='Returns sales statistics including total profit, sales revenue, average bill, and monthly chart data',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def dashboard_sales_statistics(request):
    """Get sales statistics for dashboard"""
    now = timezone.now()
    current_year = now.year
    last_year = current_year - 1
    
    # Get start and end of current year
    current_year_start = timezone.make_aware(datetime(current_year, 1, 1))
    current_year_end = timezone.make_aware(datetime(current_year + 1, 1, 1))
    last_year_start = timezone.make_aware(datetime(last_year, 1, 1))
    last_year_end = timezone.make_aware(datetime(last_year + 1, 1, 1))
    
    # Get all quotations
    all_quotations = Quotation.objects.select_related('order').filter(
        order__created_at__isnull=False
    ).defer('order__client')  # Exclude client field to avoid client_id column error
    
    # Calculate total profit: grand_total - subtotal (expenses) from completed/delivered orders
    completed_quotations = all_quotations.filter(
        order__status__in=['delivered', 'completed'],
        order__delivered_at__isnull=False
    )
    total_profit = sum(
        (float(q.grand_total) - float(q.subtotal)) for q in completed_quotations
        if q.grand_total and q.subtotal
    )
    
    # Calculate sales revenue: sum of all grand_totals
    total_revenue = all_quotations.aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    total_revenue = float(total_revenue)
    
    # Calculate average bill
    quotation_count = all_quotations.filter(grand_total__gt=0).count()
    average_bill = (total_revenue / quotation_count) if quotation_count > 0 else 0.0
    
    # Monthly chart data for current year
    monthly_data_current = [0.0] * 12
    monthly_quotations = all_quotations.filter(
        order__created_at__gte=current_year_start,
        order__created_at__lt=current_year_end
    ).annotate(
        month=Extract('order__created_at', 'month')
    ).values('month').annotate(
        total=Sum('grand_total')
    ).order_by('month')
    
    for item in monthly_quotations:
        month_num = item['month']
        if 1 <= month_num <= 12:
            monthly_data_current[month_num - 1] = float(item['total'] or 0)
    
    # Monthly chart data for previous year (optional)
    monthly_data_previous = [0.0] * 12
    last_year_quotations = all_quotations.filter(
        order__created_at__gte=last_year_start,
        order__created_at__lt=last_year_end
    ).annotate(
        month=Extract('order__created_at', 'month')
    ).values('month').annotate(
        total=Sum('grand_total')
    ).order_by('month')
    
    for item in last_year_quotations:
        month_num = item['month']
        if 1 <= month_num <= 12:
            monthly_data_previous[month_num - 1] = float(item['total'] or 0)
    
    month_labels = [month_abbr[i] for i in range(1, 13)]
    
    return Response({
        'total_profit': round(total_profit, 2),
        'sales_revenue': round(total_revenue, 2),
        'average_bill': round(average_bill, 2),
        'monthly_data': {
            'months': month_labels,
            'this_year': monthly_data_current,
            'previous_year': monthly_data_previous if sum(monthly_data_previous) > 0 else monthly_data_current
        }
    })


@extend_schema(
    operation_id='dashboard_low_stock_alerts',
    summary='Get Low Stock Alerts',
    description='Returns inventory items that are below or at minimum stock threshold',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def dashboard_low_stock_alerts(request):
    """Get low stock alert items"""
    # Filter items where quantity <= minimum_stock
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=models.F('minimum_stock')
    ).order_by('quantity')
    
    # Get last restock date for each item from InventoryMovement
    items_data = []
    for item in low_stock_items:
        # Get last positive delta (restock) for this SKU
        last_restock = InventoryMovement.objects.filter(
            sku=item.sku,
            delta__gt=0
        ).order_by('-created_at').first()
        
        last_restock_date = last_restock.created_at.date().isoformat() if last_restock else None
        
        items_data.append({
            'sku': item.sku,
            'name': item.name,
            'current_stock': item.quantity,
            'minimum_stock': item.minimum_stock,
            'last_restock_date': last_restock_date
        })
    
    return Response({
        'critical_count': len(items_data),
        'items': items_data
    })


@extend_schema(
    operation_id='dashboard_attendance_today',
    summary='Get Today\'s Attendance Summary',
    description='Returns today\'s employee attendance summary with check-in counts and status breakdown',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def dashboard_attendance_today(request):
    """Get today's attendance summary"""
    today = timezone.now().date()
    
    # Get all attendance records for today
    today_attendance = Attendance.objects.filter(date=today)
    checked_in_count = today_attendance.count()
    
    # Get scheduled count (total active employees)
    scheduled_count = Employee.objects.filter(status='active').count()
    
    # Calculate status breakdown
    on_time_count = today_attendance.filter(status=Attendance.STATUS_PRESENT).count()
    late_count = today_attendance.filter(status=Attendance.STATUS_LATE).count()
    absent_count = max(0, scheduled_count - checked_in_count)
    
    # Calculate percentages
    attendance_rate = (checked_in_count / scheduled_count * 100) if scheduled_count > 0 else 0.0
    on_time_percentage = (on_time_count / checked_in_count * 100) if checked_in_count > 0 else 0.0
    late_percentage = (late_count / checked_in_count * 100) if checked_in_count > 0 else 0.0
    absent_percentage = (absent_count / scheduled_count * 100) if scheduled_count > 0 else 0.0
    
    return Response({
        'checked_in': checked_in_count,
        'scheduled': scheduled_count,
        'attendance_rate': round(attendance_rate, 1),
        'on_time': on_time_count,
        'on_time_percentage': round(on_time_percentage, 1),
        'late': late_count,
        'late_percentage': round(late_percentage, 1),
        'absent': absent_count,
        'absent_percentage': round(absent_percentage, 1)
    })


@extend_schema(
    operation_id='dashboard_top_products_week',
    summary='Get Top Products This Week',
    description='Returns top selling products for this week with growth percentage vs last week',
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission])
def dashboard_top_products_week(request):
    """Get top products this week"""
    now = timezone.now()
    
    # Calculate this week start (Monday)
    days_since_monday = now.weekday()
    this_week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    last_week_start = this_week_start - timedelta(days=7)
    
    # Get order items for this week
    this_week_items = OrderItem.objects.filter(
        order__created_at__gte=this_week_start
    ).values('name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:10]
    
    # Get order items for last week
    last_week_items = OrderItem.objects.filter(
        order__created_at__gte=last_week_start,
        order__created_at__lt=this_week_start
    ).values('name').annotate(
        total_quantity=Sum('quantity')
    )
    
    # Create a dictionary for last week sales
    last_week_dict = {item['name']: item['total_quantity'] for item in last_week_items}
    
    # Build products list with growth calculation
    products = []
    for item in this_week_items:
        product_name = item['name']
        this_week_sales = item['total_quantity']
        last_week_sales = last_week_dict.get(product_name, 0)
        
        # Calculate growth percentage
        if last_week_sales > 0:
            growth_percentage = ((this_week_sales - last_week_sales) / last_week_sales) * 100
        else:
            # If no sales last week, set growth to 0 or a default positive value
            growth_percentage = 0.0 if this_week_sales == 0 else 100.0
        
        products.append({
            'name': product_name,
            'sales_count': this_week_sales,
            'growth_percentage': round(growth_percentage, 1)
        })
    
    return Response({
        'products': products
    })

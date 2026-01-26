from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Notification
from clients.models import Client
from orders.models import Order
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_tag_based_followups():
    """
    Send automated follow-ups based on customer profile tags.
    - B2B: Monthly account statements (check last statement date)
    - Online: Thank-you messages after order delivery
    - Walk-In: Promotional reminders
    - B2C: Personalized follow-ups
    """
    try:
        logger.info("Starting tag-based follow-up task")
        
        # B2B: Monthly account statements
        # Check for B2B clients who haven't received a statement in the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        b2b_clients = Client.objects.filter(
            profile_tag='b2b',
            org__isnull=False
        ).select_related('org', 'account_owner')
        
        for client in b2b_clients:
            # Check if there's a recent notification for this client
            last_notification = Notification.objects.filter(
                tag_trigger='b2b',
                user=client.account_owner
            ).order_by('-created_at').first()
            
            # Send monthly statement if no notification in last 30 days
            if not last_notification or last_notification.created_at < thirty_days_ago:
                if client.account_owner:
                    Notification.objects.create(
                        user=client.account_owner,
                        message=f"Monthly account statement ready for {client.org.name}. Please review and send to client.",
                        tag_trigger='b2b',
                        is_read=False
                    )
                    logger.info(f"Created B2B statement notification for {client.org.name}")
        
        # Online: Thank-you messages after order delivery
        # Check for orders delivered in the last 24 hours from Online clients
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        recent_delivered_orders = Order.objects.filter(
            client__profile_tag='online',
            status='delivered',
            delivered_at__gte=twenty_four_hours_ago
        ).select_related('client', 'client__org', 'created_by')
        
        for order in recent_delivered_orders:
            # Check if thank-you already sent
            existing_notification = Notification.objects.filter(
                tag_trigger='online',
                message__icontains=order.order_code
            ).exists()
            
            if not existing_notification and order.created_by:
                Notification.objects.create(
                    user=order.created_by,
                    message=f"Thank you for your order {order.order_code}! We hope you're satisfied with your purchase. Please leave a review.",
                    tag_trigger='online',
                    is_read=False
                )
                logger.info(f"Created Online thank-you notification for order {order.order_code}")
        
        # Walk-In: Promotional reminders
        # Send to sales staff about walk-in customers who haven't ordered in 60 days
        sixty_days_ago = timezone.now() - timedelta(days=60)
        walk_in_clients = Client.objects.filter(
            profile_tag='walk_in'
        ).select_related('org', 'account_owner')
        
        for client in walk_in_clients:
            # Check last order date
            last_order = Order.objects.filter(
                client=client
            ).order_by('-created_at').first()
            
            if not last_order or last_order.created_at < sixty_days_ago:
                if client.account_owner:
                    Notification.objects.create(
                        user=client.account_owner,
                        message=f"Walk-in customer {client.org.name} hasn't placed an order in 60+ days. Consider reaching out with promotional offers.",
                        tag_trigger='walk_in',
                        is_read=False
                    )
                    logger.info(f"Created Walk-In promotional reminder for {client.org.name}")
        
        # B2C: Personalized follow-ups
        # Send follow-up for B2C customers with recent orders (7 days after delivery)
        seven_days_ago = timezone.now() - timedelta(days=7)
        b2c_recent_orders = Order.objects.filter(
            client__profile_tag='b2c',
            status='delivered',
            delivered_at__gte=seven_days_ago,
            delivered_at__lte=seven_days_ago + timedelta(days=1)
        ).select_related('client', 'client__org', 'created_by')
        
        for order in b2c_recent_orders:
            existing_notification = Notification.objects.filter(
                tag_trigger='b2c',
                message__icontains=order.order_code
            ).exists()
            
            if not existing_notification and order.created_by:
                Notification.objects.create(
                    user=order.created_by,
                    message=f"Follow-up reminder: Check in with {order.client_name} about their recent order {order.order_code}. Ensure satisfaction and gather feedback.",
                    tag_trigger='b2c',
                    is_read=False
                )
                logger.info(f"Created B2C follow-up notification for order {order.order_code}")
        
        logger.info("Completed tag-based follow-up task")
        return {'status': 'success', 'notifications_created': 'multiple'}
        
    except Exception as e:
        logger.error(f"Error in send_tag_based_followups task: {e}")
        raise


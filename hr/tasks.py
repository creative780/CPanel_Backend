"""
Celery tasks for HR employee management
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from datetime import timedelta, datetime
from calendar import monthrange
from .models import EmployeeDocument, HREmployee, EmployeeSuspension, EmployeeSalaryExemption
from attendance.models import Attendance, LeaveRequest, Holiday
from attendance.models import AttendanceRule
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_document_expiry():
    """
    Daily task to check document expiry and send alerts
    Marks documents as expired and sends email alerts for documents expiring within 60 days
    """
    today = timezone.now().date()
    threshold_date = today + timedelta(days=60)
    
    # Find documents expiring within 60 days
    expiring_documents = EmployeeDocument.objects.filter(
        expiry_date__lte=threshold_date,
        expiry_date__gte=today,
        status__in=['uploaded', 'verified']
    ).select_related('employee')
    
    # Find expired documents
    expired_documents = EmployeeDocument.objects.filter(
        expiry_date__lt=today,
        status__in=['uploaded', 'verified']
    )
    
    # Mark expired documents
    expired_count = expired_documents.update(status='expired')
    logger.info(f"Marked {expired_count} documents as expired")
    
    # Send email alerts for expiring documents
    alerts_sent = 0
    for doc in expiring_documents:
        try:
            employee = doc.employee
            days_until_expiry = (doc.expiry_date - today).days
            
            # Send email to employee and admin
            subject = f"Document Expiry Alert: {doc.get_document_type_display()}"
            message = (
                f"Dear {employee.name},\n\n"
                f"Your {doc.get_document_type_display()} document is expiring in {days_until_expiry} days "
                f"(Expiry date: {doc.expiry_date}).\n\n"
                f"Please upload a renewed document to avoid any issues.\n\n"
                f"Best regards,\nHR Department"
            )
            
            recipients = [employee.email]
            if employee.user and employee.user.email:
                recipients.append(employee.user.email)
            
            # Also notify admin
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_users = User.objects.filter(roles__contains=['admin'], is_active=True)
            admin_emails = [u.email for u in admin_users if u.email]
            recipients.extend(admin_emails)
            
            # Remove duplicates
            recipients = list(set(recipients))
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            send_mail(subject, message, from_email, recipients, fail_silently=False)
            alerts_sent += 1
            
        except Exception as e:
            logger.error(f"Failed to send expiry alert for document {doc.id}: {e}")
    
    logger.info(f"Sent {alerts_sent} document expiry alerts")
    return {
        'expired_count': expired_count,
        'alerts_sent': alerts_sent,
        'expiring_count': expiring_documents.count()
    }


@shared_task
def end_expired_suspensions():
    """
    Hourly task to automatically end suspensions that have reached their expiry date
    """
    now = timezone.now()
    
    # Find all active suspensions that have expired
    expired_suspensions = EmployeeSuspension.objects.filter(
        is_active=True,
        expiry_date__lte=now
    ).select_related('employee', 'employee__user')
    
    ended_count = 0
    errors = []
    
    for suspension in expired_suspensions:
        try:
            with transaction.atomic():
                # Mark suspension as ended
                suspension.is_active = False
                suspension.ended_at = now
                suspension.ended_by = None  # System ended it
                suspension.save(update_fields=['is_active', 'ended_at', 'ended_by'])
                
                # Restore employee status to Active
                employee = suspension.employee
                employee.status = 'Active'
                employee.save(update_fields=['status'])
                
                # Reactivate user account if exists
                if employee.user:
                    employee.user.is_active = True
                    employee.user.save(update_fields=['is_active'])
                
                # Log activity event
                try:
                    from activity_log.models import ActivityEvent, Verb
                    # Use system user or first admin user for logging
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    system_user = User.objects.filter(roles__contains=['admin'], is_active=True).first()
                    
                    if system_user:
                        role = system_user.roles[0] if hasattr(system_user, 'roles') and system_user.roles else 'admin'
                        prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
                        ActivityEvent.objects.create(
                            timestamp=now,
                            actor_id=system_user.id,
                            actor_role=role,
                            verb=Verb.STATUS_CHANGE,
                            target_type="HREmployee",
                            target_id=str(employee.id),
                            metadata={
                                'action': 'suspension_ended',
                                'suspension_id': suspension.id,
                                'ended_automatically': True,
                                'expiry_date': suspension.expiry_date.isoformat()
                            },
                            prev_hash=prev.hash if prev else None,
                            tenant_id="default"
                        )
                except Exception as log_error:
                    logger.warning(f"Failed to log auto-ended suspension activity: {log_error}")
                
                ended_count += 1
                logger.info(f"Automatically ended suspension {suspension.id} for employee {employee.name}")
        
        except Exception as e:
            error_msg = f"Failed to end suspension {suspension.id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
    
    logger.info(f"Ended {ended_count} expired suspensions automatically")
    return {
        'ended_count': ended_count,
        'errors': errors
    }


@shared_task
def end_expired_exemptions():
    """
    Hourly task to automatically end temporary exemptions that have reached their expiry date
    """
    now = timezone.now()
    
    # Find all active temporary exemptions that have expired
    expired_exemptions = EmployeeSalaryExemption.objects.filter(
        is_active=True,
        exemption_type='Temporary',
        expiry_date__lte=now
    ).select_related('employee')
    
    ended_count = 0
    errors = []
    
    for exemption in expired_exemptions:
        try:
            with transaction.atomic():
                # Mark exemption as ended
                exemption.is_active = False
                exemption.ended_at = now
                exemption.ended_by = None  # System ended it
                exemption.save(update_fields=['is_active', 'ended_at', 'ended_by'])
                
                # Log activity event
                try:
                    from activity_log.models import ActivityEvent, Verb
                    # Use system user or first admin user for logging
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    system_user = User.objects.filter(roles__contains=['admin'], is_active=True).first()
                    
                    if system_user:
                        role = system_user.roles[0] if hasattr(system_user, 'roles') and system_user.roles else 'admin'
                        prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
                        ActivityEvent.objects.create(
                            timestamp=now,
                            actor_id=system_user.id,
                            actor_role=role,
                            verb=Verb.STATUS_CHANGE,
                            target_type="HREmployee",
                            target_id=str(exemption.employee.id),
                            metadata={
                                'action': 'exemption_ended',
                                'exemption_id': exemption.id,
                                'exemption_type': exemption.exemption_type,
                                'ended_automatically': True,
                                'expiry_date': exemption.expiry_date.isoformat() if exemption.expiry_date else None
                            },
                            prev_hash=prev.hash if prev else None,
                            tenant_id="default"
                        )
                except Exception as log_error:
                    logger.warning(f"Failed to log auto-ended exemption activity: {log_error}")
                
                ended_count += 1
                logger.info(f"Automatically ended exemption {exemption.id} for employee {exemption.employee.name}")
        
        except Exception as e:
            error_msg = f"Failed to end exemption {exemption.id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
    
    logger.info(f"Ended {ended_count} expired exemptions automatically")
    return {
        'ended_count': ended_count,
        'errors': errors
    }


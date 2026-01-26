"""
Email service for sending export files and scheduled reports.
"""
import logging
from pathlib import Path
from typing import List, Optional

from django.core.mail import EmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)


def send_export_email(
    recipients: List[str],
    file_path: str,
    report_name: str,
    format: str,
    subject: Optional[str] = None,
    body: Optional[str] = None,
) -> bool:
    """
    Send an export file as email attachment.
    
    Args:
        recipients: List of email addresses to send to
        file_path: Path to the export file
        report_name: Name of the report (for email subject/body)
        format: Export format (CSV, PDF, XML, NDJSON)
        subject: Optional custom email subject
        body: Optional custom email body
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not recipients:
        logger.warning("No recipients provided for export email")
        return False
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        logger.error(f"Export file not found: {file_path}")
        return False
    
    # Generate default subject and body if not provided
    if not subject:
        subject = f"Activity Log Export: {report_name}"
    
    if not body:
        body = f"""
Hello,

Please find attached the activity log export report: {report_name}

Format: {format}
Generated: {Path(file_path).stat().st_mtime if Path(file_path).exists() else 'N/A'}

This is an automated message from the CRM system.

Best regards,
CRM System
"""
    
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        
        # Attach the file
        with open(file_path, 'rb') as f:
            file_name = file_path_obj.name
            email.attach(file_name, f.read())
        
        email.send()
        logger.info(f"Export email sent successfully to {recipients} for report: {report_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send export email: {e}", exc_info=True)
        return False


def send_scheduled_report(
    recipients: List[str],
    file_path: str,
    report: 'ScheduledReport',  # type: ignore
    report_period: Optional[str] = None,
) -> bool:
    """
    Send a scheduled report via email.
    
    Args:
        recipients: List of email addresses to send to
        file_path: Path to the export file
        report: ScheduledReport instance
        report_period: Optional description of the report period (e.g., "Daily Report - 2024-01-15")
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not recipients:
        logger.warning(f"No recipients configured for scheduled report: {report.name}")
        return False
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        logger.error(f"Scheduled report file not found: {file_path}")
        return False
    
    # Generate email subject and body
    period_text = report_period or "Scheduled Report"
    subject = f"Scheduled Activity Log Report: {report.name} - {period_text}"
    
    body = f"""
Hello,

This is your scheduled activity log report.

Report Name: {report.name}
Schedule: {report.get_schedule_type_display()}
Format: {report.get_format_display()}
Period: {period_text}

Please find the report attached.

This is an automated message from the CRM system.

Best regards,
CRM System
"""
    
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        
        # Attach the file
        with open(file_path, 'rb') as f:
            file_name = file_path_obj.name
            email.attach(file_name, f.read())
        
        email.send()
        logger.info(f"Scheduled report email sent successfully to {recipients} for report: {report.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send scheduled report email: {e}", exc_info=True)
        return False















































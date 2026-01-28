from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable, Dict, Any, List
from collections import defaultdict

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    ActivityEvent, ExportJob, JobStatus, ExportFormat, 
    RetentionPolicy, AnonymizationJob, ScheduledReport, ScheduleType
)
from .services.email_service import send_scheduled_report

logger = logging.getLogger(__name__)


def _exports_dir() -> Path:
    base = Path(getattr(settings, "EXPORTS_DIR", settings.MEDIA_ROOT))
    d = base / "activity_exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _generate_pdf_export(file_path: Path, events: Iterable[ActivityEvent], filters: Dict[str, Any]) -> None:
    """Generate PDF export file with professional audit report format."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError as e:
        error_msg = "reportlab is required for PDF exports. Install it with: pip install reportlab"
        logger.error(f"{error_msg}: {e}")
        raise ImportError(error_msg) from e
    
    doc = SimpleDocTemplate(str(file_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
    )
    
    # Cover page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Activity Log Export Report", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Metadata
    metadata_data = [
        ['Generated:', datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")],
        ['Report ID:', f"EXPORT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"],
    ]
    
    if filters.get('since'):
        metadata_data.append(['From:', str(filters['since'])])
    if filters.get('until'):
        metadata_data.append(['To:', str(filters['until'])])
    if filters.get('actor_role'):
        metadata_data.append(['Department:', str(filters['actor_role'])])
    if filters.get('severity'):
        metadata_data.append(['Severity:', str(filters['severity'])])
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(metadata_table)
    story.append(PageBreak())
    
    # Summary page
    story.append(Paragraph("Summary Statistics", heading_style))
    
    # Collect summary data
    event_list = list(events)
    total_events = len(event_list)
    
    severity_count = defaultdict(int)
    verb_count = defaultdict(int)
    actor_role_count = defaultdict(int)
    
    for ev in event_list:
        severity = ev.context.get('severity', 'unknown') if ev.context else 'unknown'
        severity_count[severity] += 1
        verb_count[ev.verb] += 1
        actor_role_count[ev.actor_role] += 1
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Events', str(total_events)],
    ]
    
    if severity_count:
        summary_data.append(['', ''])
        summary_data.append(['Severity Breakdown', ''])
        for sev, count in sorted(severity_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary_data.append([f'  {sev}', str(count)])
    
    if verb_count:
        summary_data.append(['', ''])
        summary_data.append(['Top Actions', ''])
        for verb, count in sorted(verb_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary_data.append([f'  {verb}', str(count)])
    
    if actor_role_count:
        summary_data.append(['', ''])
        summary_data.append(['Department Breakdown', ''])
        for role, count in sorted(actor_role_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary_data.append([f'  {role}', str(count)])
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(summary_table)
    story.append(PageBreak())
    
    # Events table
    story.append(Paragraph("Activity Events", heading_style))
    
    # Table headers
    headers = ['Timestamp', 'User/Role', 'Action', 'Target Type', 'Target ID', 'Severity']
    table_data = [headers]
    
    # Add event rows (limit to prevent huge PDFs)
    max_rows = 1000
    for idx, ev in enumerate(event_list[:max_rows]):
        actor_name = ev.actor.username if ev.actor else 'System'
        role = ev.actor_role
        user_display = f"{actor_name} ({role})" if ev.actor else role
        
        severity = ev.context.get('severity', '-') if ev.context else '-'
        
        row = [
            ev.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            user_display[:30],  # Truncate long names
            ev.verb,
            ev.target_type[:20],
            str(ev.target_id)[:30],
            severity,
        ]
        table_data.append(row)
    
    if len(event_list) > max_rows:
        table_data.append(['', '', f'... and {len(event_list) - max_rows} more events', '', '', ''])
    
    events_table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1*inch, 1.3*inch, 0.8*inch])
    events_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(events_table)
    
    # Footer note
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "<i>This is an automated audit report generated by the CRM system. "
        "This document contains confidential information and should be handled accordingly.</i>",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)


def _generate_xml_export(file_path: Path, events: Iterable[ActivityEvent], filters: Dict[str, Any]) -> None:
    """Generate XML export file with legal compliance structure."""
    try:
        from lxml import etree
    except ImportError:
        import xml.etree.ElementTree as etree
    
    # Create root element with namespace
    root = etree.Element('ActivityLogExport', xmlns='http://crm.click2print.store/schemas/activity-log/v1')
    
    # Metadata section
    metadata = etree.SubElement(root, 'Metadata')
    etree.SubElement(metadata, 'ExportDate').text = datetime.now(timezone.utc).isoformat()
    etree.SubElement(metadata, 'TotalEvents').text = str(len(list(events)) if hasattr(events, '__len__') else 'N/A')
    
    filters_elem = etree.SubElement(metadata, 'Filters')
    if filters.get('since'):
        etree.SubElement(filters_elem, 'Since').text = str(filters['since'])
    if filters.get('until'):
        etree.SubElement(filters_elem, 'Until').text = str(filters['until'])
    if filters.get('actor_role'):
        etree.SubElement(filters_elem, 'Department').text = str(filters['actor_role'])
    if filters.get('severity'):
        etree.SubElement(filters_elem, 'Severity').text = str(filters['severity'])
    
    # Events section
    events_elem = etree.SubElement(root, 'Events')
    
    for ev in events:
        event_elem = etree.SubElement(events_elem, 'Event')
        etree.SubElement(event_elem, 'ID').text = str(ev.id)
        etree.SubElement(event_elem, 'Timestamp').text = ev.timestamp.isoformat()
        
        actor_elem = etree.SubElement(event_elem, 'Actor')
        etree.SubElement(actor_elem, 'ID').text = str(ev.actor_id) if ev.actor_id else ''
        etree.SubElement(actor_elem, 'Role').text = ev.actor_role
        if ev.actor:
            etree.SubElement(actor_elem, 'Username').text = ev.actor.username if ev.actor else ''
        
        etree.SubElement(event_elem, 'Verb').text = ev.verb
        
        target_elem = etree.SubElement(event_elem, 'Target')
        etree.SubElement(target_elem, 'Type').text = ev.target_type
        etree.SubElement(target_elem, 'ID').text = str(ev.target_id)
        
        context_elem = etree.SubElement(event_elem, 'Context')
        if ev.context:
            # Convert context dict to XML
            for key, value in ev.context.items():
                ctx_item = etree.SubElement(context_elem, 'Item')
                etree.SubElement(ctx_item, 'Key').text = str(key)
                etree.SubElement(ctx_item, 'Value').text = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        
        etree.SubElement(event_elem, 'Source').text = ev.source
        etree.SubElement(event_elem, 'Hash').text = ev.hash
        etree.SubElement(event_elem, 'TenantID').text = ev.tenant_id
    
    # Write to file
    tree = etree.ElementTree(root)
    
    # Pretty print
    try:
        from lxml import etree as lxml_etree
        tree_str = lxml_etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        with open(file_path, 'wb') as f:
            f.write(tree_str)
    except ImportError:
        # Fallback to standard library - format manually
        from xml.dom import minidom
        rough_string = etree.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="  ")
        with open(file_path, 'w', encoding='UTF-8') as f:
            f.write(pretty_string)


def _execute_export_job(job_id: int) -> None:
    """Core export job execution logic (called by both task and management command)"""
    try:
        job = ExportJob.objects.get(id=job_id)
    except ObjectDoesNotExist:
        logger.error(f"Export job {job_id} not found")
        return
    
    try:
        logger.info(f"Starting export job {job_id} (format: {job.format})")
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        job.save(update_fields=["status", "started_at"])
    except Exception as e:
        logger.error(f"Failed to update job {job_id} status to RUNNING: {e}", exc_info=True)
        # Try to mark as failed
        try:
            job.status = JobStatus.FAILED
            job.error = f"Failed to start: {str(e)}"
            job.finished_at = datetime.now(timezone.utc)
            job.save(update_fields=["status", "error", "finished_at"])
        except:
            pass
        raise
    
    try:
        # Start with base queryset
        qs = ActivityEvent.objects.all()
        # basic filters from job
        filters = job.filters_json or {}
        
        logger.info(f"Applying filters: {filters}")
        for k, v in filters.items():
            if k in {"verb", "target_type", "target_id", "source", "tenant_id"}:
                qs = qs.filter(**{k: v})
            elif k == "actor_id":
                # Support both single ID and list of IDs
                if isinstance(v, list):
                    qs = qs.filter(actor_id__in=v)
                else:
                    qs = qs.filter(actor_id=v)
            elif k == "actor_role":
                # Support both single role and list of roles (department filter)
                if isinstance(v, list):
                    qs = qs.filter(actor_role__in=v)
                else:
                    qs = qs.filter(actor_role=v)
            elif k == "department":
                # Map department to actor_role
                if isinstance(v, list):
                    qs = qs.filter(actor_role__in=v)
                else:
                    qs = qs.filter(actor_role=v)
            elif k == "since":
                qs = qs.filter(timestamp__gte=v)
            elif k == "until":
                qs = qs.filter(timestamp__lte=v)
            elif k == "severity":
                # Support both single severity and list of severities
                if isinstance(v, list):
                    # Need to handle JSON field filtering for multiple values
                    from django.db.models import Q
                    severity_filter = Q()
                    for sev in v:
                        severity_filter |= Q(context__severity=sev)
                    qs = qs.filter(severity_filter)
                else:
                    qs = qs.filter(context__severity=v)
        out_dir = _exports_dir()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        # Order queryset for consistent results
        qs = qs.order_by('-timestamp')
        
        # For PDF and XML, we need to load all events into memory (with limit)
        if job.format == ExportFormat.PDF:
            fp = out_dir / f"export_{job.id}_{ts}.pdf"
            # Limit PDF exports to prevent memory issues
            try:
                events_list = list(qs.select_related('actor')[:10000])
                logger.info(f"Generating PDF export with {len(events_list)} events")
                _generate_pdf_export(fp, events_list, filters)
            except ImportError as import_err:
                logger.error(f"Import error for PDF export: {import_err}", exc_info=True)
                raise ImportError("PDF export requires reportlab library. Please install it: pip install reportlab") from import_err
            except Exception as pdf_err:
                logger.error(f"Error generating PDF: {pdf_err}", exc_info=True)
                raise
        elif job.format == ExportFormat.XML:
            fp = out_dir / f"export_{job.id}_{ts}.xml"
            # Limit XML exports to prevent memory issues
            try:
                events_list = list(qs.select_related('actor')[:50000])
                logger.info(f"Generating XML export with {len(events_list)} events")
                _generate_xml_export(fp, events_list, filters)
            except ImportError as import_err:
                logger.error(f"Import error for XML export: {import_err}", exc_info=True)
                raise ImportError("XML export requires lxml library. Please install it: pip install lxml") from import_err
            except Exception as xml_err:
                logger.error(f"Error generating XML: {xml_err}", exc_info=True)
                raise
        elif job.format == ExportFormat.NDJSON:
            fp = out_dir / f"export_{job.id}_{ts}.ndjson"
            with fp.open("w", encoding="utf-8") as f:
                for ev in qs.iterator(chunk_size=1000):
                    row = {
                        "id": str(ev.id),
                        "timestamp": ev.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "actor": {"id": str(ev.actor_id) if ev.actor_id else None, "role": ev.actor_role},
                        "verb": ev.verb,
                        "target": {"type": ev.target_type, "id": ev.target_id},
                        "context": ev.context,
                        "source": ev.source,
                        "hash": ev.hash,
                    }
                    f.write(json.dumps(row, separators=(",", ":")) + "\n")
        elif job.format == ExportFormat.CSV:
            fp = out_dir / f"export_{job.id}_{ts}.csv"
            fields: Iterable[str] = (
                job.filters_json.get("fields")
                if isinstance(job.filters_json, dict)
                else None
            ) or [
                "timestamp",
                "actor.role",
                "verb",
                "target.type",
                "target.id",
                "context.severity",
                "context.tags",
            ]
            try:
                with fp.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(fields)
                    # Use select_related for actor to avoid N+1 queries
                    qs_with_actor = qs.select_related('actor')
                    count = 0
                    for ev in qs_with_actor.iterator(chunk_size=1000):
                        row = []
                        data = {
                            "timestamp": ev.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "actor.role": ev.actor_role,
                            "actor.id": str(ev.actor_id) if ev.actor_id else "",
                            "verb": ev.verb,
                            "target.type": ev.target_type,
                            "target.id": ev.target_id,
                            "context.severity": ev.context.get("severity") if ev.context else "",
                            "context.tags": ",".join(ev.context.get("tags", [])) if ev.context and isinstance(ev.context.get("tags"), list) else "",
                        }
                        for field in fields:
                            row.append(str(data.get(field, "")))
                        writer.writerow(row)
                        count += 1
                    logger.info(f"CSV export wrote {count} rows to {fp}")
            except Exception as csv_error:
                logger.error(f"Error writing CSV file: {csv_error}", exc_info=True)
                raise
        job.file_path = str(fp)
        job.status = JobStatus.COMPLETED
        job.finished_at = datetime.now(timezone.utc)
        job.save(update_fields=["file_path", "status", "finished_at"])
        logger.info(f"Export job {job_id} completed successfully. File: {fp}")
        
        # Update scheduled report's last_run if this export was triggered by "Run Now"
        if job.scheduled_report:
            job.scheduled_report.last_run = datetime.now(timezone.utc)
            job.scheduled_report.save(update_fields=['last_run'])
            logger.info(f"Updated last_run for scheduled report {job.scheduled_report.id} ({job.scheduled_report.name})")
    except Exception as e:  # pragma: no cover - best effort
        logger.error(f"Export job {job_id} failed: {e}", exc_info=True)
        error_message = str(e)
        # Provide more helpful error messages for common issues
        if "reportlab" in error_message.lower() or "ImportError" in str(type(e).__name__):
            error_message = "PDF export requires reportlab library. Please install it: pip install reportlab"
        elif "lxml" in error_message.lower():
            error_message = "XML export requires lxml library. Please install it: pip install lxml"
        
        try:
            job.refresh_from_db()
            job.status = JobStatus.FAILED
            job.error = error_message[:1000]  # Limit error message length
            job.finished_at = datetime.now(timezone.utc)
            job.save(update_fields=["status", "error", "finished_at"])
            logger.info(f"Export job {job_id} marked as failed with error: {error_message}")
        except Exception as save_error:
            logger.error(f"Failed to save error status for job {job_id}: {save_error}", exc_info=True)
            # Re-raise the original exception
            raise


@shared_task(bind=True, max_retries=3)
def run_export_job(self, job_id: int) -> None:
    """Celery task wrapper for export job execution"""
    _execute_export_job(job_id)


# Also allow calling directly (not just as Celery task)
def run_export_job_sync(job_id: int) -> None:
    """Synchronous version of export job execution (can be called directly)"""
    _execute_export_job(job_id)


@shared_task
def process_scheduled_reports() -> None:
    """Process all active scheduled reports that are due to run."""
    now = datetime.now(timezone.utc)
    
    # Get all active scheduled reports where next_run <= now
    due_reports = ScheduledReport.objects.filter(
        is_active=True,
        next_run__lte=now
    ).select_related('created_by')
    
    report_count = due_reports.count()
    logger.info(f"Processing {report_count} due scheduled reports")
    
    if report_count == 0:
        logger.debug("No scheduled reports due at this time")
        return
    
    success_count = 0
    failure_count = 0
    
    for report in due_reports:
        try:
            logger.info(f"Processing scheduled report: {report.name} (ID: {report.id})")
            
            # Validate recipients
            if not report.recipients or len(report.recipients) == 0:
                logger.error(f"Scheduled report {report.id} ({report.name}) has no recipients. Skipping.")
                # Update next_run to prevent immediate retry
                report.next_run = _calculate_next_run(report, now)
                report.save(update_fields=['next_run'])
                failure_count += 1
                continue
            
            # Validate email addresses
            import re
            email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            invalid_emails = [email for email in report.recipients if not email_regex.match(email)]
            if invalid_emails:
                logger.error(f"Scheduled report {report.id} ({report.name}) has invalid email addresses: {invalid_emails}")
                # Update next_run but log error
                report.next_run = _calculate_next_run(report, now)
                report.save(update_fields=['next_run'])
                failure_count += 1
                continue
            
            # Calculate report period for email
            period_start = report.last_run if report.last_run else (
                now - timedelta(days=1) if report.schedule_type == ScheduleType.DAILY else
                now - timedelta(days=7)
            )
            period_text = f"{period_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
            
            # Create export job with report's filters and format
            try:
                export_job = ExportJob.objects.create(
                    format=report.format,
                    filters_json=report.filters_json,
                    requested_by=report.created_by,
                    status=JobStatus.PENDING,
                )
            except Exception as e:
                logger.error(f"Failed to create export job for scheduled report {report.id}: {e}", exc_info=True)
                report.next_run = _calculate_next_run(report, now)
                report.save(update_fields=['next_run'])
                failure_count += 1
                continue
            
            # Execute export
            try:
                _execute_export_job(export_job.id)
            except Exception as e:
                logger.error(f"Export execution failed for scheduled report {report.id}: {e}", exc_info=True)
                export_job.refresh_from_db()
                if export_job.status == JobStatus.FAILED:
                    logger.error(f"Export job {export_job.id} failed: {export_job.error}")
                report.next_run = _calculate_next_run(report, now)
                report.save(update_fields=['next_run'])
                failure_count += 1
                continue
            
            # Refresh job to get updated status
            export_job.refresh_from_db()
            
            if export_job.status == JobStatus.COMPLETED and export_job.file_path:
                # Send email with attachment
                try:
                    email_sent = send_scheduled_report(
                        recipients=report.recipients,
                        file_path=export_job.file_path,
                        report=report,
                        report_period=period_text,
                    )
                    
                    if email_sent:
                        # Update report tracking
                        report.last_run = now
                        report.next_run = _calculate_next_run(report, now)
                        report.save(update_fields=['last_run', 'next_run'])
                        logger.info(f"Successfully processed scheduled report: {report.name} (ID: {report.id})")
                        success_count += 1
                    else:
                        logger.error(f"Failed to send email for scheduled report: {report.name} (ID: {report.id})")
                        # Still update next_run to prevent immediate retry
                        report.next_run = _calculate_next_run(report, now)
                        report.save(update_fields=['next_run'])
                        failure_count += 1
                except Exception as e:
                    logger.error(f"Error sending email for scheduled report {report.id}: {e}", exc_info=True)
                    report.next_run = _calculate_next_run(report, now)
                    report.save(update_fields=['next_run'])
                    failure_count += 1
            else:
                error_msg = export_job.error or "Unknown error"
                logger.error(
                    f"Export job failed for scheduled report: {report.name} (ID: {report.id}), "
                    f"error: {error_msg}"
                )
                # Still update next_run to prevent retrying immediately
                report.next_run = _calculate_next_run(report, now)
                report.save(update_fields=['next_run'])
                failure_count += 1
                
        except Exception as e:
            logger.error(f"Unexpected error processing scheduled report {report.id}: {e}", exc_info=True)
            # Update next_run to prevent stuck reports
            try:
                report.next_run = _calculate_next_run(report, now)
                report.save(update_fields=['next_run'])
            except Exception as save_error:
                logger.error(f"Failed to update next_run for report {report.id}: {save_error}", exc_info=True)
            failure_count += 1
    
    logger.info(
        f"Scheduled report processing completed: {success_count} succeeded, {failure_count} failed "
        f"out of {report_count} total"
    )


def _calculate_next_run(report: ScheduledReport, current_time: datetime) -> datetime:
    """Calculate the next run time for a scheduled report."""
    from datetime import time as dt_time
    
    schedule_time = report.schedule_time
    
    if report.schedule_type == ScheduleType.DAILY:
        # Next occurrence of schedule_time today or tomorrow
        next_run = current_time.replace(
            hour=schedule_time.hour,
            minute=schedule_time.minute,
            second=0,
            microsecond=0
        )
        # If time has passed today, use tomorrow
        if next_run <= current_time:
            next_run += timedelta(days=1)
        return next_run
    
    elif report.schedule_type == ScheduleType.WEEKLY:
        # Next occurrence of schedule_day at schedule_time
        if report.schedule_day is None:
            # Default to Monday if not set
            schedule_day = 0
        else:
            schedule_day = report.schedule_day
        
        # Calculate days until next schedule_day
        current_weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        days_ahead = schedule_day - current_weekday
        
        # If schedule_day is today but time has passed, or schedule_day is in the past this week
        target_time = current_time.replace(
            hour=schedule_time.hour,
            minute=schedule_time.minute,
            second=0,
            microsecond=0
        )
        
        if days_ahead < 0:
            # Schedule day is next week
            days_ahead += 7
        elif days_ahead == 0 and target_time <= current_time:
            # Schedule day is today but time has passed, use next week
            days_ahead = 7
        
        next_run = target_time + timedelta(days=days_ahead)
        return next_run
    
    # Fallback (shouldn't happen)
    return current_time + timedelta(days=1)


@shared_task
def run_retention(policy_id: int) -> None:
    """
    Retention policy execution is disabled for compliance.
    Logs cannot be deleted or modified per security requirements.
    This function now only reports statistics without making changes.
    """
    policy = RetentionPolicy.objects.get(id=policy_id)
    job = AnonymizationJob.objects.create(policy=policy, status=JobStatus.RUNNING, started_at=datetime.now(timezone.utc))
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=policy.keep_days)
        qs = ActivityEvent.objects.all()
        if policy.role_filter:
            qs = qs.filter(actor_role__in=policy.role_filter)
        if policy.target_type_filter:
            qs = qs.filter(target_type__in=policy.target_type_filter)
        if cutoff:
            qs = qs.filter(timestamp__lte=cutoff)
        total = qs.count()
        
        # Logs cannot be deleted or modified for compliance
        # Only report statistics
        affected = 0
        error_message = (
            "Retention policies are disabled for compliance. "
            "Logs cannot be deleted or modified per security requirements. "
            f"Policy '{policy.name}' would affect {total} events, but no changes were made."
        )
        
        job.total_events = total
        job.affected_events = affected
        job.status = JobStatus.FAILED
        job.log = error_message
        job.finished_at = datetime.now(timezone.utc)
        job.save(update_fields=["status", "log", "finished_at", "total_events", "affected_events"])
    except Exception as e:  # pragma: no cover - best effort
        job.status = JobStatus.FAILED
        job.log = f"Error: {str(e)}. Note: Logs cannot be deleted or modified for compliance."
        job.finished_at = datetime.now(timezone.utc)
        job.save(update_fields=["status", "log", "finished_at"])

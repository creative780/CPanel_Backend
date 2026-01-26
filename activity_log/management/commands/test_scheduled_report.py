"""
Django management command to manually test scheduled report processing.
Usage: python manage.py test_scheduled_report [report_id]
Or: python manage.py test_scheduled_report --all (to test all active reports)
"""
from django.core.management.base import BaseCommand, CommandError
from activity_log.models import ScheduledReport
from activity_log.tasks import process_scheduled_reports


class Command(BaseCommand):
    help = 'Manually trigger scheduled report processing for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            'report_id',
            type=int,
            nargs='?',
            help='ID of the scheduled report to test (optional)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all active scheduled reports that are due',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force process even if not due (for testing)',
        )

    def handle(self, *args, **options):
        report_id = options.get('report_id')
        process_all = options.get('all', False)
        force = options.get('force', False)
        
        if process_all:
            self.stdout.write('Processing all active scheduled reports...')
            try:
                process_scheduled_reports()
                self.stdout.write(
                    self.style.SUCCESS('Successfully processed scheduled reports!')
                )
            except Exception as e:
                raise CommandError(f'Failed to process scheduled reports: {e}')
            return
        
        if not report_id:
            # List all scheduled reports
            reports = ScheduledReport.objects.all().order_by('-created_at')
            if not reports.exists():
                self.stdout.write(self.style.WARNING('No scheduled reports found.'))
                return
            
            self.stdout.write('\nScheduled Reports:')
            self.stdout.write('-' * 80)
            for report in reports[:20]:  # Show first 20
                status = 'Active' if report.is_active else 'Inactive'
                next_run = report.next_run.strftime('%Y-%m-%d %H:%M:%S') if report.next_run else 'Not set'
                self.stdout.write(
                    f'ID: {report.id:3d} | {report.name:30s} | {status:8s} | Next: {next_run}'
                )
            self.stdout.write('-' * 80)
            self.stdout.write('\nUsage: python manage.py test_scheduled_report <report_id>')
            self.stdout.write('       python manage.py test_scheduled_report --all')
            return
        
        # Process specific report
        try:
            report = ScheduledReport.objects.get(id=report_id)
        except ScheduledReport.DoesNotExist:
            raise CommandError(f'Scheduled report with ID {report_id} not found.')
        
        self.stdout.write(f'Testing scheduled report: {report.name} (ID: {report.id})')
        self.stdout.write(f'Schedule: {report.get_schedule_type_display()} at {report.schedule_time}')
        self.stdout.write(f'Format: {report.format}')
        self.stdout.write(f'Recipients: {", ".join(report.recipients)}')
        self.stdout.write(f'Active: {report.is_active}')
        self.stdout.write('')
        
        if not report.is_active and not force:
            raise CommandError(
                f'Report is inactive. Use --force to process anyway.'
            )
        
        # Temporarily set next_run to now to make it due
        if force:
            from django.utils import timezone
            original_next_run = report.next_run
            report.next_run = timezone.now()
            report.save(update_fields=['next_run'])
            self.stdout.write(self.style.WARNING('Forced report to be due (next_run set to now)'))
        
        try:
            self.stdout.write('Processing scheduled report...')
            process_scheduled_reports()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully processed scheduled report: {report.name}')
            )
            
            # Refresh to see updated status
            report.refresh_from_db()
            if report.last_run:
                self.stdout.write(f'Last run: {report.last_run}')
            if report.next_run:
                self.stdout.write(f'Next run: {report.next_run}')
                
        except Exception as e:
            raise CommandError(f'Failed to process scheduled report: {e}')
        finally:
            if force and 'original_next_run' in locals():
                # Restore original next_run
                report.next_run = original_next_run
                report.save(update_fields=['next_run'])















































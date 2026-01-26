"""
Management command to manually process pending export jobs.
Useful when Celery workers are not running or jobs are stuck.
"""
from django.core.management.base import BaseCommand
from activity_log.models import ExportJob, JobStatus
from activity_log.tasks import _execute_export_job
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process pending export jobs manually'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job-id',
            type=int,
            help='Process a specific job ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all pending jobs',
        )

    def handle(self, *args, **options):
        if options['job_id']:
            try:
                job = ExportJob.objects.get(id=options['job_id'])
                if job.status == JobStatus.PENDING:
                    self.stdout.write(f'Processing job {job.id}...')
                    # Call the export function directly (synchronously)
                    _execute_export_job(job.id)
                    # Refresh from DB to get updated status
                    job.refresh_from_db()
                    if job.status == JobStatus.COMPLETED:
                        self.stdout.write(self.style.SUCCESS(f'Job {job.id} processed successfully'))
                    elif job.status == JobStatus.FAILED:
                        self.stdout.write(self.style.ERROR(f'Job {job.id} failed: {job.error}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Job {job.id} status: {job.status}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Job {job.id} is not pending (status: {job.status})'))
            except ExportJob.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Job {options["job_id"]} not found'))
        elif options['all']:
            pending_jobs = ExportJob.objects.filter(status=JobStatus.PENDING)
            count = pending_jobs.count()
            self.stdout.write(f'Found {count} pending jobs')
            
            for job in pending_jobs:
                try:
                    self.stdout.write(f'Processing job {job.id}...')
                    _execute_export_job(job.id)
                    job.refresh_from_db()
                    if job.status == JobStatus.COMPLETED:
                        self.stdout.write(self.style.SUCCESS(f'Job {job.id} completed'))
                    elif job.status == JobStatus.FAILED:
                        self.stdout.write(self.style.ERROR(f'Job {job.id} failed: {job.error}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Job {job.id} status: {job.status}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Job {job.id} failed: {e}'))
        else:
            self.stdout.write(self.style.ERROR('Please specify --job-id or --all'))


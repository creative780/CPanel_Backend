# Merge migration to resolve conflict between branches
# Branch 1 (if exists): 0001 -> ... -> 0004 -> 0005
# Branch 2: 0001 -> 0006
# Depend on 0001_initial and 0006 to work even if 0005 doesn't exist on production
# If 0005 exists, it will be applied before this merge since it's in the chain from 0001

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial (always exists) and 0006 (latest in branch 2)
        # Also depend on 0002 to ensure AttendanceRule exists in state for subsequent migrations
        # This ensures the merge works on production even if 0005 doesn't exist
        ('attendance', '0001_initial'),
        ('attendance', '0002_attendancerule_attendance_device_info_and_more'),
        ('attendance', '0006_attendancebreak_and_effective_minutes'),
    ]

    operations = [
    ]


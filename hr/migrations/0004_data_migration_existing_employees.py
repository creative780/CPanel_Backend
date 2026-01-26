# Generated manually for data migration

from django.db import migrations


def create_verification_records(apps, schema_editor):
    """Create EmployeeVerification records for existing employees"""
    HREmployee = apps.get_model('hr', 'HREmployee')
    EmployeeVerification = apps.get_model('hr', 'EmployeeVerification')
    
    for employee in HREmployee.objects.all():
        EmployeeVerification.objects.get_or_create(employee=employee)


def reverse_create_verification_records(apps, schema_editor):
    """Reverse migration - delete verification records"""
    EmployeeVerification = apps.get_model('hr', 'EmployeeVerification')
    EmployeeVerification.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0003_employeebankdetails_employeedocument_and_more'),
    ]

    operations = [
        migrations.RunPython(create_verification_records, reverse_create_verification_records),
    ]


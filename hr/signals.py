"""
Django signals for HR employee management
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    HREmployee, EmployeeVerification, EmployeeReference,
    EmployeeBankDetails, EmployeeDocument, EmployeeExemption
)
from .services import calculate_behavior_index
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=HREmployee)
def create_verification_record(sender, instance, created, **kwargs):
    """Create EmployeeVerification record when HREmployee is created"""
    if created:
        EmployeeVerification.objects.get_or_create(employee=instance)
        logger.info(f"Created verification record for employee {instance.id}")


@receiver(post_save, sender=EmployeeReference)
def update_reference_verification(sender, instance, **kwargs):
    """Update verification status when reference is verified"""
    if instance.otp_verified:
        verification, _ = EmployeeVerification.objects.get_or_create(employee=instance.employee)
        # Check if all references are verified
        all_references = EmployeeReference.objects.filter(employee=instance.employee)
        all_verified = all_references.exists() and all_references.filter(otp_verified=False).count() == 0
        if all_verified:
            verification.reference_verified = True
            verification.save()
            logger.info(f"All references verified for employee {instance.employee.id}")
            
            # Check if salary should be activated
            from .services import check_and_activate_salary
            check_and_activate_salary(instance.employee)


@receiver(post_save, sender=EmployeeBankDetails)
def update_bank_verification(sender, instance, **kwargs):
    """Update verification status when bank is verified"""
    if instance.status == 'verified':
        verification, _ = EmployeeVerification.objects.get_or_create(employee=instance.employee)
        verification.bank_verified = True
        verification.save()
        logger.info(f"Bank verified for employee {instance.employee.id}")


@receiver(post_save, sender=EmployeeDocument)
def update_document_verification(sender, instance, **kwargs):
    """Update verification status when address proof document is uploaded/verified"""
    if instance.document_type == 'address_proof' and instance.status in ['uploaded', 'verified']:
        verification, _ = EmployeeVerification.objects.get_or_create(employee=instance.employee)
        verification.address_proof_verified = True
        verification.save()
        logger.info(f"Address proof verified for employee {instance.employee.id}")


@receiver(post_save, sender=EmployeeExemption)
def update_exemption_verification(sender, instance, **kwargs):
    """Update verification status when bank exemption is granted"""
    if instance.bank_exempted:
        verification, _ = EmployeeVerification.objects.get_or_create(employee=instance.employee)
        verification.bank_verified = True  # Consider exempted as verified
        verification.save()
        logger.info(f"Bank exemption granted for employee {instance.employee.id}")


@receiver(post_save, sender=HREmployee)
def update_email_verification(sender, instance, **kwargs):
    """Update email verification status when employee email is set"""
    if instance.email:
        verification, _ = EmployeeVerification.objects.get_or_create(employee=instance)
        # Email is considered verified if employee has email (can be enhanced with email verification)
        verification.email_verified = True
        verification.save()


@receiver(post_save, sender=HREmployee)
def update_phone_verification(sender, instance, **kwargs):
    """Update phone verification status and check salary activation"""
    if instance.phone_verified:
        verification, _ = EmployeeVerification.objects.get_or_create(employee=instance)
        verification.phone_verified = True
        verification.save()
        logger.info(f"Phone verification updated for employee {instance.id}")
        
        # Check if salary should be activated
        from .services import check_and_activate_salary
        check_and_activate_salary(instance)


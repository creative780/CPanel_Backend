from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from monitoring.models import Employee

User = get_user_model()


class HREmployee(models.Model):
    """Separate HR Employee model for employee management"""
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Inactive', 'Inactive'),
        ('Suspended', 'Suspended'),
    )
    
    BRANCH_CHOICES = (
        ('dubai', 'Dubai'),
        ('pakistan', 'Pakistan'),
    )
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('sales', 'Sales'),
        ('designer', 'Designer'),
        ('production', 'Production'),
        ('delivery', 'Delivery'),
        ('finance', 'Finance'),
    )
    
    SALARY_STATUS_CHOICES = (
        ('ON_HOLD', 'On Hold'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
    )
    
    # Basic employee information
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    image = models.CharField(max_length=500, blank=True)  # store URL/path
    
    # Employment details
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    designation = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES, default='dubai')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')
    
    # New fields for verification system
    department = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    phone_verified = models.BooleanField(default=False)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    salary_status = models.CharField(max_length=20, choices=SALARY_STATUS_CHOICES, default='ON_HOLD')
    verification_status = models.CharField(max_length=50, default='not_started', blank=True)
    
    # Authentication fields (linked to User model)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hr_employee', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Override save to enforce salary hold if bank not verified"""
        # Only check bank verification if this is an update (pk exists)
        # During creation, we don't want to enforce this yet
        is_update = self.pk is not None
        
        super().save(*args, **kwargs)
        
        # Check bank verification status and enforce hold if needed (only on updates)
        if is_update:
            try:
                from .services import check_bank_verification_status
                if not check_bank_verification_status(self):
                    if self.salary_status != 'ON_HOLD':
                        self.salary_status = 'ON_HOLD'
                        # Use update_fields to avoid recursion
                        HREmployee.objects.filter(pk=self.pk).update(salary_status='ON_HOLD')
            except (ImportError, Exception):
                # Services not yet created or other errors, skip for now
                pass
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['salary_status']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['department']),
        ]


class SalarySlip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_slips')
    period = models.CharField(max_length=20)
    gross = models.DecimalField(max_digits=12, decimal_places=2)
    net = models.DecimalField(max_digits=12, decimal_places=2)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EmployeePersonalDetails(models.Model):
    """Personal details for employee verification"""
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )
    
    employee = models.OneToOneField(HREmployee, on_delete=models.CASCADE, related_name='personal_details')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    present_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Personal Details - {self.employee.name}"


class EmployeeFamilyMember(models.Model):
    """Family members information"""
    RELATIONSHIP_CHOICES = (
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('child', 'Child'),
    )
    
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='family_members')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.relationship.title()} - {self.name} ({self.employee.name})"
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'relationship']),
        ]


class EmployeeEmergencyContact(models.Model):
    """Emergency contacts - minimum 2 required"""
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Emergency Contact - {self.name} ({self.employee.name})"
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'is_primary']),
        ]


class EmployeeReference(models.Model):
    """Professional references with OTP verification"""
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='references')
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    otp_code = models.CharField(max_length=6, blank=True)
    otp_verified = models.BooleanField(default=False)
    otp_sent_at = models.DateTimeField(null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reference - {self.name} ({self.employee.name})"
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'otp_verified']),
        ]


class EmployeeBankDetails(models.Model):
    """Bank account details with verification"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verification_requested', 'Verification Requested'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    employee = models.OneToOneField(HREmployee, on_delete=models.CASCADE, related_name='bank_details')
    bank_name = models.CharField(max_length=255)
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, blank=True)
    iban = models.CharField(max_length=50)
    swift_code = models.CharField(max_length=20, blank=True)
    branch_name = models.CharField(max_length=255, blank=True)
    proof_document = models.FileField(upload_to='employee_documents/bank_proofs/%Y/%m/%d/', blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_banks')
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    verification_requested_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_banks')
    rejected_at = models.DateTimeField(null=True, blank=True)
    exemption_reason = models.TextField(blank=True)
    exemption_granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='exempted_banks')
    exemption_granted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bank Details - {self.employee.name} ({self.bank_name})"
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'status']),
        ]


class EmployeeDocument(models.Model):
    """Employee documents with expiry tracking"""
    DOCUMENT_TYPE_CHOICES = (
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('emirates_id', 'Emirates ID'),
        ('address_proof', 'Address Proof'),
        ('certificate', 'Certificate'),
    )
    
    STATUS_CHOICES = (
        ('uploaded', 'Uploaded'),
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('expired', 'Expired'),
    )
    
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    address_proof_type = models.CharField(
        max_length=20,
        choices=[('tenancy_contract', 'Tenancy Contract'), ('dewa_bill', 'DEWA Bill')],
        blank=True,
        null=True,
        help_text="Required if document_type is 'address_proof'"
    )
    file = models.FileField(upload_to='employee_documents/%Y/%m/%d/')
    expiry_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.document_type.title()} - {self.employee.name}"
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'document_type']),
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['expiry_date']),
        ]


class EmployeeVerification(models.Model):
    """Verification status tracking"""
    employee = models.OneToOneField(HREmployee, on_delete=models.CASCADE, related_name='verification')
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    reference_verified = models.BooleanField(default=False)
    bank_verified = models.BooleanField(default=False)
    address_proof_verified = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_verification_percentage(self):
        """Calculate verification percentage based on completed verifications"""
        weights = {
            'phone': 20,
            'email': 10,
            'references': 20,
            'bank': 30,
            'documents': 20,
        }
        
        total = 0
        if self.phone_verified:
            total += weights['phone']
        if self.email_verified:
            total += weights['email']
        if self.reference_verified:
            total += weights['references']
        if self.bank_verified:
            total += weights['bank']
        if self.address_proof_verified:
            total += weights['documents']
        
        return total
    
    @property
    def verification_percentage(self):
        """Computed property for verification percentage"""
        return self.calculate_verification_percentage()
    
    def __str__(self):
        return f"Verification - {self.employee.name} ({self.verification_percentage}%)"


class EmployeeExemption(models.Model):
    """Employee exemptions from verification requirements"""
    employee = models.OneToOneField(HREmployee, on_delete=models.CASCADE, related_name='exemption')
    bank_exempted = models.BooleanField(default=False)
    bank_exemption_reason = models.TextField(blank=True)
    bank_exempted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_bank_exemptions')
    bank_exempted_at = models.DateTimeField(null=True, blank=True)
    other_exemptions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Exemption - {self.employee.name}"


class HRWarning(models.Model):
    """HR warnings for employees"""
    WARNING_TYPE_CHOICES = (
        ('behavior', 'Behavior'),
        ('attendance', 'Attendance'),
        ('other', 'Other'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    STATUS_CHOICES = (
        ('pending_explanation', 'Pending Explanation'),
        ('explanation_submitted', 'Explanation Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated'),
    )
    
    VIOLATION_CATEGORY_CHOICES = (
        ('late_arrival', 'Late Arrival'),
        ('unapproved_absence', 'Unapproved Absence'),
        ('early_exit', 'Early Exit'),
        ('behavioral', 'Behavioral'),
        ('manual', 'Manual'),
    )
    
    REVIEW_DECISION_CHOICES = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated'),
    )
    
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='warnings')
    warning_type = models.CharField(max_length=20, choices=WARNING_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    reason = models.TextField()
    behavior_index_score = models.FloatField(null=True, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_warnings')
    issued_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # New fields for violation management system
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_explanation')
    violation_date = models.DateTimeField(null=True, blank=True, help_text="Date and time of the violation")
    violation_category = models.CharField(max_length=30, choices=VIOLATION_CATEGORY_CHOICES, default='manual')
    reference_attendance = models.ForeignKey(
        'attendance.Attendance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warnings',
        help_text="Reference to attendance record if applicable"
    )
    explanation_submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_warnings'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_decision = models.CharField(
        max_length=20,
        choices=REVIEW_DECISION_CHOICES,
        null=True,
        blank=True
    )
    review_notes = models.TextField(blank=True)
    escalation_level = models.IntegerField(default=0, help_text="Escalation level (1-4)")
    portal_access_locked = models.BooleanField(default=False)
    salary_on_hold = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Warning - {self.employee.name} ({self.warning_type}) - {self.status}"
    
    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['employee', 'warning_type']),
            models.Index(fields=['employee', 'severity']),
            models.Index(fields=['issued_at']),
            models.Index(fields=['status']),
            models.Index(fields=['violation_category']),
            models.Index(fields=['portal_access_locked']),
            models.Index(fields=['escalation_level']),
        ]


class OTPVerification(models.Model):
    """OTP verification records"""
    DELIVERY_METHOD_CHOICES = (
        ('email', 'Email'),
    )
    
    PURPOSE_CHOICES = (
        ('email_verification', 'Email Verification'),
        ('reference_verification', 'Reference Verification'),
    )
    
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='otp_verifications')
    phone_number = models.CharField(max_length=32, blank=True)  # Kept for backward compatibility, always empty now
    email = models.EmailField(blank=True)
    otp_code = models.CharField(max_length=6)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHOD_CHOICES, default='email')
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP - {self.employee.name} ({self.purpose})"
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'purpose']),
            models.Index(fields=['otp_code', 'is_used']),
            models.Index(fields=['expires_at']),
        ]


class EmployeeVerificationDraft(models.Model):
    """Draft data for verification wizard"""
    STEP_CHOICES = (
        ('personal', 'Personal Details'),
        ('family', 'Family Details'),
        ('contact', 'Contact Info'),
        ('references', 'References'),
        ('bank', 'Bank Details'),
        ('government', 'Government ID'),
        ('address', 'Address Proof'),
    )
    
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='verification_drafts')
    step = models.CharField(max_length=20, choices=STEP_CHOICES)
    draft_data = models.JSONField(default=dict)
    last_saved_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Draft - {self.employee.name} ({self.step})"
    
    class Meta:
        unique_together = ['employee', 'step']
        indexes = [
            models.Index(fields=['employee', 'step']),
        ]


class SalaryStatusLog(models.Model):
    """Log of salary status changes"""
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='salary_status_logs')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='salary_status_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Status Log - {self.employee.name} ({self.old_status} -> {self.new_status})"
    
    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['employee', 'changed_at']),
        ]


class WarningExplanation(models.Model):
    """Employee explanation for a warning"""
    warning = models.OneToOneField(HRWarning, on_delete=models.CASCADE, related_name='explanation')
    explanation_text = models.TextField(max_length=5000)
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_explanations')
    
    def __str__(self):
        return f"Explanation for Warning #{self.warning.id}"
    
    class Meta:
        ordering = ['-submitted_at']


class WarningAttachment(models.Model):
    """File attachments for warning explanations"""
    warning = models.ForeignKey(HRWarning, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='warning_attachments/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment - {self.file_name} (Warning #{self.warning.id})"
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['warning', 'uploaded_at']),
        ]


class WarningLog(models.Model):
    """Audit log for all warning-related actions"""
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('explanation_submitted', 'Explanation Submitted'),
        ('reviewed', 'Reviewed'),
        ('escalated', 'Escalated'),
        ('access_locked', 'Access Locked'),
        ('access_unlocked', 'Access Unlocked'),
        ('salary_held', 'Salary Held'),
        ('salary_released', 'Salary Released'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    warning = models.ForeignKey(HRWarning, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='warning_actions')
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Log - {self.action} for Warning #{self.warning.id} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['warning', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]


class WarningEscalation(models.Model):
    """Escalation records for warnings"""
    warning = models.ForeignKey(HRWarning, on_delete=models.CASCADE, related_name='escalations')
    escalation_level = models.IntegerField(help_text="Escalation level (1-4)")
    escalation_reason = models.TextField()
    escalated_at = models.DateTimeField(auto_now_add=True)
    escalated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='escalated_warnings',
        help_text="System or admin who escalated"
    )
    action_taken = models.TextField(blank=True)
    
    def __str__(self):
        return f"Escalation Level {self.escalation_level} - Warning #{self.warning.id}"
    
    class Meta:
        ordering = ['-escalated_at']
        indexes = [
            models.Index(fields=['warning', 'escalation_level']),
            models.Index(fields=['escalated_at']),
        ]


class EmployeeSuspension(models.Model):
    """Employee suspension records with reason, expiry date, and remarks"""
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='suspensions')
    reason = models.TextField(help_text="Reason for suspension")
    expiry_date = models.DateTimeField(help_text="Date and time when suspension should automatically end")
    remarks = models.TextField(blank=True, help_text="Additional remarks or notes")
    suspended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='suspended_employees')
    suspended_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True, help_text="When suspension was ended (manually or automatically)")
    ended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ended_suspensions')
    is_active = models.BooleanField(default=True, help_text="True if suspension is currently active")
    
    def __str__(self):
        status = "Active" if self.is_active else "Ended"
        return f"Suspension - {self.employee.name} ({status})"
    
    class Meta:
        ordering = ['-suspended_at']
        indexes = [
            models.Index(fields=['employee', 'is_active']),
            models.Index(fields=['expiry_date', 'is_active']),
            models.Index(fields=['is_active']),
        ]


class EmployeeSalaryExemption(models.Model):
    """Employee salary exemptions - temporary or permanent"""
    EXEMPTION_TYPE_CHOICES = (
        ('Temporary', 'Temporary'),
        ('Permanent', 'Permanent'),
    )
    
    employee = models.ForeignKey(HREmployee, on_delete=models.CASCADE, related_name='salary_exemptions')
    exemption_type = models.CharField(max_length=20, choices=EXEMPTION_TYPE_CHOICES)
    reason = models.TextField(help_text="Reason for exemption")
    expiry_date = models.DateTimeField(null=True, blank=True, help_text="Expiry date (required for temporary exemptions, not applicable for permanent)")
    remarks = models.TextField(blank=True, help_text="Additional remarks or notes")
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_salary_exemptions')
    granted_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True, help_text="When exemption was ended (manually or automatically)")
    ended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ended_salary_exemptions')
    is_active = models.BooleanField(default=True, help_text="True if exemption is currently active")
    
    def clean(self):
        """Validate that temporary exemptions have expiry_date"""
        from django.core.exceptions import ValidationError
        if self.exemption_type == 'Temporary' and not self.expiry_date:
            raise ValidationError("Expiry date is required for temporary exemptions")
        if self.exemption_type == 'Permanent' and self.expiry_date:
            raise ValidationError("Permanent exemptions should not have an expiry date")
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "Active" if self.is_active else "Ended"
        return f"Salary Exemption - {self.employee.name} ({self.exemption_type}, {status})"
    
    class Meta:
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['employee', 'is_active'], name='hr_empsalaryex_employee_idx'),
            models.Index(fields=['exemption_type', 'is_active'], name='hr_empsalaryex_exempti_idx'),
            models.Index(fields=['expiry_date', 'is_active'], name='hr_empsalaryex_expiry_d_idx'),
            models.Index(fields=['is_active'], name='hr_empsalaryex_is_acti_idx'),
        ]

# Create your models here.

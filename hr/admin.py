from django.contrib import admin
from .models import (
    HREmployee, SalarySlip, EmployeePersonalDetails, EmployeeFamilyMember,
    EmployeeEmergencyContact, EmployeeReference, EmployeeBankDetails,
    EmployeeDocument, EmployeeVerification, EmployeeExemption, HRWarning,
    OTPVerification, EmployeeVerificationDraft, SalaryStatusLog,
    WarningExplanation, WarningAttachment, WarningLog, WarningEscalation
)


@admin.register(HREmployee)
class HREmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'branch', 'status', 'salary_status', 'designation', 'salary', 'created_at']
    list_filter = ['role', 'branch', 'status', 'salary_status', 'verification_status', 'created_at']
    search_fields = ['name', 'email', 'designation', 'department']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'image', 'phone_verified', 'phone_verified_at')
        }),
        ('Employment Details', {
            'fields': ('salary', 'designation', 'status', 'branch', 'role', 'department', 'manager')
        }),
        ('Verification & Salary', {
            'fields': ('salary_status', 'verification_status')
        }),
        ('Authentication', {
            'fields': ('user',),
            'description': 'Linked User account for login'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'period', 'gross', 'net', 'created_at']
    list_filter = ['created_at', 'period']
    search_fields = ['employee__name', 'period']
    readonly_fields = ['created_at']


@admin.register(EmployeePersonalDetails)
class EmployeePersonalDetailsAdmin(admin.ModelAdmin):
    list_display = ['employee', 'gender', 'date_of_birth', 'nationality', 'marital_status']
    search_fields = ['employee__name', 'nationality']
    list_filter = ['gender', 'marital_status', 'nationality']


@admin.register(EmployeeFamilyMember)
class EmployeeFamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['employee', 'relationship', 'name', 'phone']
    list_filter = ['relationship']
    search_fields = ['employee__name', 'name', 'phone']


@admin.register(EmployeeEmergencyContact)
class EmployeeEmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['employee', 'name', 'relationship', 'phone', 'is_primary']
    list_filter = ['is_primary', 'relationship']
    search_fields = ['employee__name', 'name', 'phone']


@admin.register(EmployeeReference)
class EmployeeReferenceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'name', 'company', 'phone', 'otp_verified']
    list_filter = ['otp_verified']
    search_fields = ['employee__name', 'name', 'company', 'phone']


@admin.register(EmployeeBankDetails)
class EmployeeBankDetailsAdmin(admin.ModelAdmin):
    list_display = ['employee', 'bank_name', 'account_holder_name', 'status', 'verified_at']
    list_filter = ['status', 'verified_at']
    search_fields = ['employee__name', 'bank_name', 'iban']
    readonly_fields = ['verified_at', 'verified_by', 'exemption_granted_at', 'exemption_granted_by']


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'status', 'expiry_date', 'uploaded_at']
    list_filter = ['document_type', 'status', 'expiry_date']
    search_fields = ['employee__name']
    readonly_fields = ['uploaded_at', 'verified_at', 'verified_by']


@admin.register(EmployeeVerification)
class EmployeeVerificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'phone_verified', 'email_verified', 'reference_verified', 'bank_verified', 'address_proof_verified', 'verification_percentage']
    list_filter = ['phone_verified', 'email_verified', 'reference_verified', 'bank_verified', 'address_proof_verified']
    search_fields = ['employee__name']
    readonly_fields = ['verification_percentage', 'last_updated']


@admin.register(EmployeeExemption)
class EmployeeExemptionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'bank_exempted', 'bank_exempted_at', 'bank_exempted_by']
    list_filter = ['bank_exempted']
    search_fields = ['employee__name']
    readonly_fields = ['bank_exempted_at', 'bank_exempted_by']


@admin.register(HRWarning)
class HRWarningAdmin(admin.ModelAdmin):
    list_display = ['employee', 'warning_type', 'severity', 'status', 'violation_category', 'escalation_level', 'issued_at', 'portal_access_locked', 'salary_on_hold']
    list_filter = ['warning_type', 'severity', 'status', 'violation_category', 'acknowledged', 'portal_access_locked', 'salary_on_hold', 'issued_at']
    search_fields = ['employee__name', 'reason', 'review_notes']
    readonly_fields = ['issued_at', 'issued_by', 'explanation_submitted_at', 'reviewed_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'warning_type', 'severity', 'reason', 'behavior_index_score')
        }),
        ('Violation Details', {
            'fields': ('violation_date', 'violation_category', 'reference_attendance')
        }),
        ('Status & Workflow', {
            'fields': ('status', 'escalation_level', 'portal_access_locked', 'salary_on_hold')
        }),
        ('Explanation', {
            'fields': ('explanation_submitted_at',)
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_decision', 'review_notes')
        }),
        ('Issuance', {
            'fields': ('issued_by', 'issued_at', 'acknowledged', 'acknowledged_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'purpose', 'delivery_method', 'is_used', 'sent_at', 'expires_at']
    list_filter = ['purpose', 'delivery_method', 'is_used', 'sent_at']
    search_fields = ['employee__name', 'phone_number', 'email']
    readonly_fields = ['sent_at', 'expires_at', 'verified_at']


@admin.register(EmployeeVerificationDraft)
class EmployeeVerificationDraftAdmin(admin.ModelAdmin):
    list_display = ['employee', 'step', 'last_saved_at']
    list_filter = ['step', 'last_saved_at']
    search_fields = ['employee__name']


@admin.register(SalaryStatusLog)
class SalaryStatusLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'old_status', 'new_status', 'changed_at', 'changed_by']
    list_filter = ['old_status', 'new_status', 'changed_at']
    search_fields = ['employee__name', 'reason']
    readonly_fields = ['changed_at', 'changed_by']


@admin.register(WarningExplanation)
class WarningExplanationAdmin(admin.ModelAdmin):
    list_display = ['warning', 'submitted_at', 'submitted_by']
    list_filter = ['submitted_at']
    search_fields = ['warning__employee__name', 'explanation_text']
    readonly_fields = ['submitted_at', 'submitted_by']
    raw_id_fields = ['warning']


@admin.register(WarningAttachment)
class WarningAttachmentAdmin(admin.ModelAdmin):
    list_display = ['warning', 'file_name', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['warning__employee__name', 'file_name']
    readonly_fields = ['uploaded_at']
    raw_id_fields = ['warning']


@admin.register(WarningLog)
class WarningLogAdmin(admin.ModelAdmin):
    list_display = ['warning', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['warning__employee__name']
    readonly_fields = ['timestamp', 'performed_by']
    raw_id_fields = ['warning', 'performed_by']


@admin.register(WarningEscalation)
class WarningEscalationAdmin(admin.ModelAdmin):
    list_display = ['warning', 'escalation_level', 'escalated_at', 'escalated_by']
    list_filter = ['escalation_level', 'escalated_at']
    search_fields = ['warning__employee__name', 'escalation_reason', 'action_taken']
    readonly_fields = ['escalated_at', 'escalated_by']
    raw_id_fields = ['warning', 'escalated_by']

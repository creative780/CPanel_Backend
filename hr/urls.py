from django.urls import path
from .views import (
    HREmployeesListView, HREmployeeDetailView, MyEmployeeView,
    LegacyHREmployeesListView, SalarySlipCreateView,
    SendPhoneOTPView, VerifyPhoneOTPView,
    SendReferenceOTPView, VerifyReferenceOTPView,
    VerificationWizardView, SaveVerificationDraftView,
    SubmitVerificationStepView, VerificationProgressView,
    RequestBankVerificationView, BankVerificationView, RejectBankVerificationView,
    GetPendingBankVerificationsView, BankExemptionView, BankStatusView,
    DocumentUploadView, DocumentListView, DocumentDeleteView, DocumentVerifyView, DocumentDownloadView,
    BehaviorIndexView, EmailConfigurationDiagnosticView,
    EmployeeSuspendView, EmployeeEndSuspensionView, EmployeeSuspensionHistoryView,
    EmployeeGrantExemptionView, EmployeeEndExemptionView, EmployeeExemptionHistoryView
)

urlpatterns = [
    # New HR Employee endpoints
    path('hr/employees', HREmployeesListView.as_view(), name='hr-employees'),
    path('hr/employees/me/', MyEmployeeView.as_view(), name='hr-employee-me'),
    path('hr/employees/<int:pk>/', HREmployeeDetailView.as_view(), name='hr-employee-detail'),
    
    # OTP endpoints
    path('hr/employees/<int:pk>/send-phone-otp', SendPhoneOTPView.as_view(), name='hr-send-phone-otp'),
    path('hr/employees/<int:pk>/verify-phone-otp', VerifyPhoneOTPView.as_view(), name='hr-verify-phone-otp'),
    path('hr/employees/<int:pk>/references/<int:ref_id>/send-otp', SendReferenceOTPView.as_view(), name='hr-send-reference-otp'),
    path('hr/employees/<int:pk>/references/<int:ref_id>/verify-otp', VerifyReferenceOTPView.as_view(), name='hr-verify-reference-otp'),
    
    # Verification wizard endpoints
    path('hr/employees/<int:pk>/verification-wizard', VerificationWizardView.as_view(), name='hr-verification-wizard'),
    path('hr/employees/<int:pk>/verification-wizard/save-draft', SaveVerificationDraftView.as_view(), name='hr-save-verification-draft'),
    path('hr/employees/<int:pk>/verification-wizard/step/<str:step>', SubmitVerificationStepView.as_view(), name='hr-submit-verification-step'),
    path('hr/employees/<int:pk>/verification-progress', VerificationProgressView.as_view(), name='hr-verification-progress'),
    
    # Bank verification endpoints
    path('hr/employees/<int:pk>/bank-details/request-verification', RequestBankVerificationView.as_view(), name='hr-request-bank-verification'),
    path('hr/employees/<int:pk>/bank-details/approve', BankVerificationView.as_view(), name='hr-approve-bank'),
    path('hr/employees/<int:pk>/bank-details/reject', RejectBankVerificationView.as_view(), name='hr-reject-bank'),
    path('hr/employees/<int:pk>/bank-details/verify', BankVerificationView.as_view(), name='hr-verify-bank'),  # Legacy endpoint
    path('hr/employees/<int:pk>/bank-details/exempt', BankExemptionView.as_view(), name='hr-exempt-bank'),
    path('hr/employees/<int:pk>/bank-status', BankStatusView.as_view(), name='hr-bank-status'),
    path('hr/employees/pending-bank-verifications', GetPendingBankVerificationsView.as_view(), name='hr-pending-bank-verifications'),
    
    # Document management endpoints
    path('hr/employees/<int:pk>/documents/upload', DocumentUploadView.as_view(), name='hr-upload-document'),
    path('hr/employees/<int:pk>/documents', DocumentListView.as_view(), name='hr-list-documents'),
    path('hr/employees/<int:pk>/documents/<int:doc_id>', DocumentDeleteView.as_view(), name='hr-delete-document'),
    path('hr/employees/<int:pk>/documents/<int:doc_id>/verify', DocumentVerifyView.as_view(), name='hr-verify-document'),
    path('hr/employees/<int:pk>/documents/<int:doc_id>/download', DocumentDownloadView.as_view(), name='hr-download-document'),
    
    # Behavior index
    path('hr/employees/<int:pk>/behavior-index', BehaviorIndexView.as_view(), name='hr-behavior-index'),
    
    # Employee suspension endpoints
    path('hr/employees/<int:pk>/suspend', EmployeeSuspendView.as_view(), name='hr-employee-suspend'),
    path('hr/employees/<int:pk>/end-suspension', EmployeeEndSuspensionView.as_view(), name='hr-employee-end-suspension'),
    path('hr/employees/<int:pk>/suspensions', EmployeeSuspensionHistoryView.as_view(), name='hr-employee-suspension-history'),
    
    # Employee salary exemption endpoints
    path('hr/employees/<int:pk>/grant-exemption', EmployeeGrantExemptionView.as_view(), name='hr-employee-grant-exemption'),
    path('hr/employees/<int:pk>/end-exemption', EmployeeEndExemptionView.as_view(), name='hr-employee-end-exemption'),
    path('hr/employees/<int:pk>/exemptions', EmployeeExemptionHistoryView.as_view(), name='hr-employee-exemption-history'),
    
    # Email configuration diagnostic (admin only)
    path('hr/email-config-diagnostic', EmailConfigurationDiagnosticView.as_view(), name='hr-email-config-diagnostic'),
    
    # Legacy endpoints
    path('hr/legacy-employees', LegacyHREmployeesListView.as_view(), name='hr-legacy-employees'),
    path('hr/salary-slips', SalarySlipCreateView.as_view(), name='hr-salary-slips'),
]

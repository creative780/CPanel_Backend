from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import UserRateThrottle
from django.db import transaction, IntegrityError, models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
import mimetypes
from monitoring.models import Employee
from .models import (
    SalarySlip, HREmployee, EmployeeReference, SalaryStatusLog, 
    EmployeeDocument, OTPVerification, EmployeeSuspension, EmployeeSalaryExemption
)
from .serializers import (
    HREmployeeSerializer, LegacyHREmployeeSerializer, SalarySlipSerializer,
    EmployeeDocumentSerializer, EmployeeSuspensionSerializer, EmployeeSalaryExemptionSerializer
)
from .services import send_otp, verify_otp, verify_bank_details, grant_bank_exemption, check_bank_verification_status, request_bank_verification, reject_bank_verification, validate_email_configuration
from accounts.permissions import RolePermission
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def check_employee_access(user, employee):
    """
    Standardized permission check for employee access.
    Returns (has_access, is_admin, is_finance)
    """
    # Check if user has has_role method
    if hasattr(user, 'has_role'):
        is_admin = user.has_role('admin')
        is_finance = user.has_role('finance')
    else:
        # Fallback for users without has_role method
        is_admin = user.is_staff
        is_finance = False
    
    # Admin and finance can access all employees
    if is_admin or is_finance:
        return (True, is_admin, is_finance)
    
    # Regular employees can only access their own record
    if employee.user and employee.user == user:
        return (True, False, False)
    
    return (False, False, False)


class HREmployeesListView(APIView):
    """List and create HR employees"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all HR employees"""
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        is_finance = request.user.has_role('finance') if hasattr(request.user, 'has_role') else False
        
        if is_admin or is_finance:
            employees = HREmployee.objects.all().order_by('-created_at')
        else:
            # Regular employees can only see their own record
            employees = HREmployee.objects.filter(user=request.user)
        
        # Pass request context to serializer for building absolute URLs
        serializer = HREmployeeSerializer(employees, many=True, context={'request': request})
        
        # Log the count for debugging
        logger.info(f"Serializing {employees.count()} employees for user {request.user.id}")
        
        try:
            serialized_data = serializer.data
            logger.info(f"Successfully serialized {len(serialized_data)} employees")
            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error serializing employees: {e}", exc_info=True)
            # Try to return partial data if possible
            try:
                # Attempt to serialize individually to identify problematic employees
                partial_data = []
                for emp in employees:
                    try:
                        emp_serializer = HREmployeeSerializer(emp, context={'request': request})
                        partial_data.append(emp_serializer.data)
                    except Exception as emp_error:
                        logger.error(f"Failed to serialize employee {emp.id} ({emp.name}): {emp_error}")
                return Response(partial_data, status=status.HTTP_200_OK)
            except Exception as fallback_error:
                logger.error(f"Fallback serialization also failed: {fallback_error}")
                return Response(
                    {'error': 'Failed to serialize employees. Check server logs for details.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    def post(self, request):
        """Create a new HR employee"""
        # Only admin can create employees
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        
        serializer = HREmployeeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                # The serializer handles its own transaction, so we don't need to wrap it here
                employee = serializer.save()
                logger.info(f"Created HR employee: {employee.name} with user: {employee.user}")
                return Response(HREmployeeSerializer(employee, context={'request': request}).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Failed to create HR employee: {e}", exc_info=True)
                error_message = str(e)
                
                # Check for database integrity errors (unique constraints)
                if 'UNIQUE constraint' in error_message or 'duplicate key' in error_message.lower():
                    if 'email' in error_message.lower():
                        return Response({
                            'error': 'An employee with this email already exists. Please use a different email address.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    elif 'username' in error_message.lower() or 'user' in error_message.lower():
                        return Response({
                            'error': 'This username is already taken. Please choose a different username.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    'error': f'Failed to create employee: {error_message}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyEmployeeView(APIView):
    """Get current user's own employee details"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user's employee record"""
        try:
            employee = HREmployee.objects.get(user=request.user)
            serializer = HREmployeeSerializer(employee, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee record not found'}, status=status.HTTP_404_NOT_FOUND)


class HREmployeeDetailView(APIView):
    """Retrieve, update, or delete HR employee"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get employee details"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access permissions
        has_access, is_admin, is_finance = check_employee_access(request.user, employee)
        if not has_access:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = HREmployeeSerializer(employee, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Update employee"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access permissions
        has_access, is_admin, is_finance = check_employee_access(request.user, employee)
        if not has_access:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Only admin can update certain fields
        serializer = HREmployeeSerializer(employee, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            try:
                # Log what image data we're receiving
                image_data = request.data.get('image', '')
                logger.info(f"Updating employee {pk}: image data type = {type(image_data)}, length = {len(str(image_data)) if image_data else 0}, starts with = {str(image_data)[:50] if image_data else 'empty'}")
                
                serializer.save()
                
                # Log what image URL we're returning
                returned_image = serializer.data.get('image', '')
                logger.info(f"Updated employee {pk}: returning image URL = {returned_image}")
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to update employee: {e}", exc_info=True)
                return Response({
                    'error': f'Failed to update employee: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete employee - Admin only"""
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            employee = HREmployee.objects.get(pk=pk)
            
            # Store user reference before deleting employee
            user_to_delete = employee.user
            
            with transaction.atomic():
                # Delete the employee record first
                employee.delete()
                
                # Delete the associated User account if it exists
                if user_to_delete:
                    # Invalidate all active sessions for this user before deletion
                    try:
                        sessions = Session.objects.filter(expire_date__gte=timezone.now())
                        for session in sessions:
                            try:
                                session_data = session.get_decoded()
                                if session_data.get('_auth_user_id') == str(user_to_delete.id):
                                    session.delete()
                            except Exception:
                                # Skip sessions that can't be decoded
                                continue
                    except Exception as e:
                        # Log but don't fail the deletion if session invalidation fails
                        logger.warning(f"Failed to invalidate sessions for user {user_to_delete.id}: {e}")
                    
                    # Delete the user account
                    user_to_delete.delete()
                    logger.info(f"Deleted User account {user_to_delete.id} along with employee {pk}")
            
            message = 'Employee and associated user account deleted successfully' if user_to_delete else 'Employee deleted successfully'
            return Response({'message': message}, status=status.HTTP_200_OK)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to delete employee: {e}", exc_info=True)
            return Response({
                'error': f'Failed to delete employee: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class LegacyHREmployeesListView(APIView):
    """Legacy endpoint for monitoring.Employee model"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employees = Employee.objects.all()
        serializer = LegacyHREmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalarySlipCreateView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'finance']
    
    def post(self, request):
        serializer = SalarySlipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPhoneOTPView(APIView):
    """Send OTP to employee email for verification"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Send OTP to employee's email"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can verify own phone, admins can verify any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        if not email:
            email = employee.email
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email address is required. Please provide an email address.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = send_otp(employee, email)
            # Check if OTP sending was successful
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                # OTP sending failed - return error with appropriate status
                error_msg = result.get('error', 'Failed to send OTP')
                return Response({
                    'success': False,
                    'error': error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error sending OTP: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Failed to send OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPhoneOTPView(APIView):
    """Verify OTP code for email verification"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Verify OTP code"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can verify own phone, admins can verify any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        otp_code = request.data.get('otp_code')
        if not otp_code:
            return Response({'error': 'OTP code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = verify_otp(employee, otp_code)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}", exc_info=True)
            return Response({
                'error': f'Failed to verify OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendReferenceOTPView(APIView):
    """Send OTP to reference for verification"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, ref_id):
        """Send OTP to reference email"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can verify own references, admins can verify any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            reference = EmployeeReference.objects.get(pk=ref_id, employee=employee)
        except EmployeeReference.DoesNotExist:
            return Response({'error': 'Reference not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not reference.email:
            return Response({
                'success': False,
                'error': 'Reference email not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = send_otp(employee, reference.email, purpose='reference_verification')
            # Check if OTP sending was successful
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                # OTP sending failed - return error with appropriate status
                error_msg = result.get('error', 'Failed to send OTP')
                return Response({
                    'success': False,
                    'error': error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error sending reference OTP: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Failed to send OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyReferenceOTPView(APIView):
    """Verify OTP code for reference verification"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, ref_id):
        """Verify reference OTP code"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can verify own references, admins can verify any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            reference = EmployeeReference.objects.get(pk=ref_id, employee=employee)
        except EmployeeReference.DoesNotExist:
            return Response({'error': 'Reference not found'}, status=status.HTTP_404_NOT_FOUND)
        
        otp_code = request.data.get('otp_code')
        if not otp_code:
            return Response({'error': 'OTP code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = verify_otp(employee, otp_code, purpose='reference_verification')
            if result.get('success'):
                # Update reference verification status
                reference.otp_verified = True
                reference.save()
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error verifying reference OTP: {e}", exc_info=True)
            return Response({
                'error': f'Failed to verify OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerificationWizardView(APIView):
    """Get current verification wizard state"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get verification wizard data"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can see own, admins see all
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import (
            EmployeePersonalDetails, EmployeeFamilyMember, EmployeeEmergencyContact,
            EmployeeReference, EmployeeBankDetails, EmployeeDocument, EmployeeVerificationDraft
        )
        
        # Get all verification data
        personal = None
        try:
            personal = EmployeePersonalDetails.objects.get(employee=employee)
        except EmployeePersonalDetails.DoesNotExist:
            pass
        
        family = list(EmployeeFamilyMember.objects.filter(employee=employee).values())
        emergency_contacts = list(EmployeeEmergencyContact.objects.filter(employee=employee).values())
        references = list(EmployeeReference.objects.filter(employee=employee).values())
        
        bank = None
        try:
            bank = EmployeeBankDetails.objects.get(employee=employee)
        except EmployeeBankDetails.DoesNotExist:
            pass
        
        documents = {}
        passport = EmployeeDocument.objects.filter(employee=employee, document_type='passport').first()
        visa = EmployeeDocument.objects.filter(employee=employee, document_type='visa').first()
        emirates_id = EmployeeDocument.objects.filter(employee=employee, document_type='emirates_id').first()
        address_proof = EmployeeDocument.objects.filter(employee=employee, document_type='address_proof').first()
        
        if passport:
            documents['passport'] = {
                'id': passport.id,
                'file_url': passport.file.url if passport.file else None,
                'expiry_date': passport.expiry_date.isoformat() if passport.expiry_date else None,
                'verified': passport.status == 'verified',
                'status': passport.status
            }
        if visa:
            documents['visa'] = {
                'id': visa.id,
                'file_url': visa.file.url if visa.file else None,
                'expiry_date': visa.expiry_date.isoformat() if visa.expiry_date else None,
                'verified': visa.status == 'verified',
                'status': visa.status
            }
        if emirates_id:
            documents['emirates_id'] = {
                'id': emirates_id.id,
                'file_url': emirates_id.file.url if emirates_id.file else None,
                'expiry_date': emirates_id.expiry_date.isoformat() if emirates_id.expiry_date else None,
                'verified': emirates_id.status == 'verified',
                'status': emirates_id.status
            }
        if address_proof:
            documents['address_proof'] = {
                'id': address_proof.id,
                'file_url': address_proof.file.url if address_proof.file else None,
                'expiry_date': address_proof.expiry_date.isoformat() if address_proof.expiry_date else None,
                'address_proof_type': address_proof.address_proof_type,
                'verified': address_proof.status == 'verified',
                'status': address_proof.status
            }
        
        # Get drafts
        drafts = {}
        draft_objects = EmployeeVerificationDraft.objects.filter(employee=employee)
        for draft in draft_objects:
            drafts[draft.step] = draft.draft_data
        
        return Response({
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'email': employee.email,
            },
            'personal': {
                'id': personal.id,
                'gender': personal.gender,
                'date_of_birth': personal.date_of_birth.isoformat() if personal.date_of_birth else None,
                'nationality': personal.nationality,
                'marital_status': personal.marital_status,
                'blood_group': personal.blood_group,
                'present_address': personal.present_address,
                'permanent_address': personal.permanent_address,
            } if personal else None,
            'family': family,
            'emergency_contacts': emergency_contacts,
            'references': references,
            'bank': {
                'id': bank.id,
                'bank_name': bank.bank_name,
                'account_number': bank.account_number,
                'iban': bank.iban,
                'swift_code': bank.swift_code,
                'branch_name': bank.branch_name,
                'account_holder_name': bank.account_holder_name,
                'status': bank.status,
            } if bank else None,
            'documents': documents,
            'drafts': drafts
        }, status=status.HTTP_200_OK)


class SaveVerificationDraftView(APIView):
    """Save verification wizard draft"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Save draft data for a step"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can save own drafts, admins can save any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        step = request.data.get('step')
        draft_data = request.data.get('draft_data')
        
        if not step:
            return Response({'error': 'Step is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from .models import EmployeeVerificationDraft
        
        draft, created = EmployeeVerificationDraft.objects.update_or_create(
            employee=employee,
            step=step,
            defaults={'draft_data': draft_data}
        )
        
        return Response({'message': 'Draft saved successfully'}, status=status.HTTP_200_OK)


class SubmitVerificationStepView(APIView):
    """Submit verification wizard step data"""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def post(self, request, pk, step):
        """Submit step data"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can submit own, admins can submit any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import (
            EmployeePersonalDetails, EmployeeFamilyMember, EmployeeEmergencyContact,
            EmployeeReference, EmployeeBankDetails, EmployeeDocument
        )
        
        try:
            with transaction.atomic():
                if step == 'personal':
                    personal_data = {
                        'gender': request.data.get('gender'),
                        'date_of_birth': request.data.get('date_of_birth'),
                        'nationality': request.data.get('nationality'),
                        'marital_status': request.data.get('marital_status'),
                        'blood_group': request.data.get('blood_group'),
                        'present_address': request.data.get('present_address'),
                        'permanent_address': request.data.get('permanent_address'),
                    }
                    personal, created = EmployeePersonalDetails.objects.update_or_create(
                        employee=employee,
                        defaults=personal_data
                    )
                    return Response({'message': 'Personal details saved'}, status=status.HTTP_200_OK)
                
                elif step == 'family':
                    # Handle family members (array)
                    # Accept both 'family' and 'members' keys for compatibility
                    family_data = request.data.get('family') or request.data.get('members', [])
                    if isinstance(family_data, str):
                        import json
                        family_data = json.loads(family_data)
                    
                    # Delete existing family members
                    EmployeeFamilyMember.objects.filter(employee=employee).delete()
                    
                    # Create new family members
                    for member_data in family_data:
                        EmployeeFamilyMember.objects.create(
                            employee=employee,
                            name=member_data.get('name'),
                            relationship=member_data.get('relationship'),
                            phone=member_data.get('phone', ''),
                            email=member_data.get('email', ''),
                            occupation=member_data.get('occupation', ''),
                            address=member_data.get('address', ''),
                        )
                    return Response({'message': 'Family members saved'}, status=status.HTTP_200_OK)
                
                elif step == 'emergency_contacts' or step == 'contact':
                    # Handle emergency contacts (array)
                    contacts_data = request.data.get('emergency_contacts', [])
                    if isinstance(contacts_data, str):
                        import json
                        contacts_data = json.loads(contacts_data)
                    
                    # Delete existing contacts
                    EmployeeEmergencyContact.objects.filter(employee=employee).delete()
                    
                    # Create new contacts
                    for contact_data in contacts_data:
                        EmployeeEmergencyContact.objects.create(
                            employee=employee,
                            name=contact_data.get('name'),
                            relationship=contact_data.get('relationship'),
                            phone=contact_data.get('phone'),
                            email=contact_data.get('email'),
                            address=contact_data.get('address'),
                        )
                    return Response({'message': 'Emergency contacts saved'}, status=status.HTTP_200_OK)
                
                elif step == 'references':
                    # Handle references (array)
                    references_data = request.data.get('references', [])
                    if isinstance(references_data, str):
                        import json
                        references_data = json.loads(references_data)
                    
                    # Delete existing references
                    EmployeeReference.objects.filter(employee=employee).delete()
                    
                    # Create new references
                    for ref_data in references_data:
                        EmployeeReference.objects.create(
                            employee=employee,
                            name=ref_data.get('name'),
                            company=ref_data.get('company'),
                            position=ref_data.get('position'),
                            phone=ref_data.get('phone'),
                            email=ref_data.get('email'),
                            relationship=ref_data.get('relationship'),
                        )
                    return Response({'message': 'References saved'}, status=status.HTTP_200_OK)
                
                elif step == 'bank':
                    bank_data = {
                        'bank_name': request.data.get('bank_name'),
                        'account_number': request.data.get('account_number'),
                        'iban': request.data.get('iban'),
                        'swift_code': request.data.get('swift_code'),
                        'branch_name': request.data.get('branch_name'),
                        'account_holder_name': request.data.get('account_holder_name'),
                    }
                    bank, created = EmployeeBankDetails.objects.update_or_create(
                        employee=employee,
                        defaults=bank_data
                    )
                    return Response({'message': 'Bank details saved'}, status=status.HTTP_200_OK)
                
                elif step in ['passport', 'visa', 'emirates_id', 'address_proof', 'address']:
                    # Handle document upload
                    # Accept both 'address' and 'address_proof' step names
                    document_type = 'address_proof' if step == 'address' else step
                    file = request.FILES.get('file')
                    if not file:
                        return Response({'error': 'File is required'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    expiry_date = request.data.get('expiry_date')
                    address_proof_type = request.data.get('address_proof_type') if document_type == 'address_proof' else None
                    
                    defaults = {
                        'file': file,
                        'expiry_date': expiry_date if expiry_date else None,
                    }
                    if address_proof_type:
                        defaults['address_proof_type'] = address_proof_type
                    
                    document, created = EmployeeDocument.objects.update_or_create(
                        employee=employee,
                        document_type=document_type,
                        defaults=defaults
                    )
                    return Response({'message': f'{document_type} document saved'}, status=status.HTTP_200_OK)
                
                else:
                    return Response({'error': 'Invalid step'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error submitting verification step: {e}", exc_info=True)
            return Response({
                'error': f'Failed to save step: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerificationProgressView(APIView):
    """Get verification progress percentage"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get verification progress"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can see own, admins see all
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import (
            EmployeePersonalDetails, EmployeeFamilyMember, EmployeeEmergencyContact,
            EmployeeReference, EmployeeBankDetails, EmployeeDocument, EmployeeVerification
        )
        
        # Calculate progress
        total_steps = 7
        completed_steps = 0
        
        if EmployeePersonalDetails.objects.filter(employee=employee).exists():
            completed_steps += 1
        if EmployeeFamilyMember.objects.filter(employee=employee).exists():
            completed_steps += 1
        if EmployeeEmergencyContact.objects.filter(employee=employee).exists():
            completed_steps += 1
        if EmployeeReference.objects.filter(employee=employee).exists():
            completed_steps += 1
        if EmployeeBankDetails.objects.filter(employee=employee).exists():
            completed_steps += 1
        if EmployeeDocument.objects.filter(employee=employee, document_type='passport').exists():
            completed_steps += 1
        if EmployeeDocument.objects.filter(employee=employee, document_type__in=['visa', 'emirates_id', 'address_proof']).exists():
            completed_steps += 1
        
        progress = int((completed_steps / total_steps) * 100)
        
        verification_obj = EmployeeVerification.objects.filter(employee=employee).first()
        bank_details = getattr(employee, 'bank_details', None)
        
        return Response({
            'verification_percentage': progress,
            'phone_verified': employee.phone_verified,
            'phone_verified_at': employee.phone_verified_at.isoformat() if employee.phone_verified_at else None,
            'email_verified': verification_obj.email_verified if verification_obj else False,
            'reference_verified': EmployeeReference.objects.filter(employee=employee, otp_verified=True).exists(),
            'bank_verified': check_bank_verification_status(employee) if bank_details else False,
            'bank_verified_at': bank_details.verified_at.isoformat() if bank_details and bank_details.verified_at else None,
            'address_proof_verified': EmployeeDocument.objects.filter(employee=employee, document_type='address_proof', status='verified').exists(),
        }, status=status.HTTP_200_OK)


class RequestBankVerificationView(APIView):
    """Request bank verification - Employee only"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Request bank verification"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Only employee can request verification for their own account
        if not employee.user or employee.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            result = request_bank_verification(employee)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error requesting bank verification: {e}", exc_info=True)
            return Response({
                'error': f'Failed to request verification: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankVerificationView(APIView):
    """Verify bank details - Admin only"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk):
        """Verify bank details"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            result = verify_bank_details(employee)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error verifying bank details: {e}", exc_info=True)
            return Response({
                'error': f'Failed to verify bank details: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectBankVerificationView(APIView):
    """Reject bank verification request - Admin only"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk):
        """Reject bank verification"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        reason = request.data.get('rejection_reason', '')
        
        try:
            result = reject_bank_verification(employee, reason)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error rejecting bank verification: {e}", exc_info=True)
            return Response({
                'error': f'Failed to reject verification: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetPendingBankVerificationsView(APIView):
    """Get list of pending bank verification requests - Admin only"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def get(self, request):
        """Get pending bank verifications"""
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import EmployeeBankDetails
        
        pending = EmployeeBankDetails.objects.filter(verification_status='pending')
        result = []
        for bank in pending:
            result.append({
                'employee_id': bank.employee.id,
                'employee_name': bank.employee.name,
                'bank_name': bank.bank_name,
                'account_number': bank.account_number,
                'requested_at': bank.updated_at.isoformat() if bank.updated_at else None,
            })
        
        return Response(result, status=status.HTTP_200_OK)


class BankExemptionView(APIView):
    """Grant bank exemption - Admin only"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk):
        """Grant bank exemption"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        reason = request.data.get('reason', '')
        
        try:
            result = grant_bank_exemption(employee, reason)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error granting bank exemption: {e}", exc_info=True)
            return Response({
                'error': f'Failed to grant exemption: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankStatusView(APIView):
    """Get bank verification status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get bank verification status"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can see own, admins see all
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            result = check_bank_verification_status(employee)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error checking bank status: {e}", exc_info=True)
            return Response({
                'error': f'Failed to check status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentUploadView(APIView):
    """Upload employee document"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, pk):
        """Upload document"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can upload own, admins can upload any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        document_type = request.data.get('document_type')
        file = request.FILES.get('file')
        expiry_date = request.data.get('expiry_date')
        
        if not document_type or not file:
            return Response({'error': 'Document type and file are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from .models import EmployeeDocument
        
        try:
            document = EmployeeDocument.objects.create(
                employee=employee,
                document_type=document_type,
                file=file,
                expiry_date=expiry_date if expiry_date else None,
            )
            serializer = EmployeeDocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error uploading document: {e}", exc_info=True)
            return Response({
                'error': f'Failed to upload document: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentListView(APIView):
    """List all employee documents"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """List documents"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can see own, admins see all
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import EmployeeDocument
        
        documents = EmployeeDocument.objects.filter(employee=employee)
        serializer = EmployeeDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocumentDeleteView(APIView):
    """Delete employee document"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk, doc_id):
        """Delete document"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can delete own, admins can delete any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import EmployeeDocument
        
        try:
            document = EmployeeDocument.objects.get(pk=doc_id, employee=employee)
            document.delete()
            return Response({'message': 'Document deleted successfully'}, status=status.HTTP_200_OK)
        except EmployeeDocument.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting document: {e}", exc_info=True)
            return Response({
                'error': f'Failed to delete document: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentVerifyView(APIView):
    """Verify employee document - Admin only"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk, doc_id):
        """Verify document"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import EmployeeDocument
        
        try:
            document = EmployeeDocument.objects.get(pk=doc_id, employee=employee)
            document.verified = True
            document.verified_at = timezone.now()
            document.verified_by = request.user
            document.save()
            
            serializer = EmployeeDocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EmployeeDocument.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error verifying document: {e}", exc_info=True)
            return Response({
                'error': f'Failed to verify document: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentDownloadView(APIView):
    """Download employee document - Secure file serving"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, doc_id):
        """Download document file"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can download own, admins can download any
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import EmployeeDocument
        
        try:
            document = EmployeeDocument.objects.get(pk=doc_id, employee=employee)
            
            if not document.file:
                return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(document.file.name)
            if not content_type:
                content_type = 'application/octet-stream'
            
            response = FileResponse(
                document.file.open('rb'),
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{document.file.name}"'
            return response
        except EmployeeDocument.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error downloading document: {e}", exc_info=True)
            return Response({
                'error': f'Failed to download document: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailConfigurationDiagnosticView(APIView):
    """Diagnostic endpoint to check email configuration status (Admin only)"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def get(self, request):
        """Get email configuration status"""
        try:
            validation = validate_email_configuration()
            
            # Remove sensitive information
            response_data = {
                'backend': validation['backend'],
                'is_console': validation['is_console'],
                'is_smtp': validation['is_smtp'],
                'debug_mode': validation['debug_mode'],
                'host_configured': validation['host_configured'],
                'user_configured': validation['user_configured'],
                'password_configured': validation['password_configured'],
                'port': validation['port'],
                'use_tls': validation['use_tls'],
                'use_ssl': validation['use_ssl'],
                'valid': validation['valid'],
                'warnings': validation['warnings'],
                'errors': validation['errors'],
            }
            
            # Add host and user (masked) for debugging
            from django.conf import settings
            email_host = getattr(settings, 'EMAIL_HOST', '')
            email_user = getattr(settings, 'EMAIL_HOST_USER', '')
            if email_host:
                response_data['host'] = email_host
            if email_user:
                # Mask email user (show first 3 chars and domain)
                if '@' in email_user:
                    parts = email_user.split('@')
                    response_data['user'] = f"{parts[0][:3]}***@{parts[1]}"
                else:
                    response_data['user'] = f"{email_user[:3]}***"
            
            status_code = status.HTTP_200_OK if validation['valid'] else status.HTTP_503_SERVICE_UNAVAILABLE
            return Response(response_data, status=status_code)
        except Exception as e:
            logger.error(f"Error checking email configuration: {e}", exc_info=True)
            return Response({
                'error': f'Failed to check email configuration: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BehaviorIndexView(APIView):
    """Get or calculate behavior index for employee"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get behavior index"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access: employees can see own, admins see all
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin and (not employee.user or employee.user != request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from .services import calculate_behavior_index
        period = request.query_params.get('period', 'month')
        
        result = calculate_behavior_index(employee, period=period)
        return Response(result, status=status.HTTP_200_OK)


class EmployeeSuspendView(APIView):
    """Suspend an employee with reason, expiry date, and remarks"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk):
        """Suspend employee"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        reason = request.data.get('reason')
        expiry_date_str = request.data.get('expiry_date')
        remarks = request.data.get('remarks', '')
        
        if not reason:
            return Response({'error': 'Reason is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not expiry_date_str:
            return Response({'error': 'Expiry date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            # Try parsing ISO format datetime string
            expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
            # Convert to timezone-aware datetime if not already
            if timezone.is_naive(expiry_date):
                expiry_date = timezone.make_aware(expiry_date)
        except (ValueError, AttributeError):
            return Response({'error': 'Invalid expiry date format. Please use ISO format (YYYY-MM-DDTHH:mm:ss)'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate expiry_date is in the future
        if expiry_date <= timezone.now():
            return Response({'error': 'Expiry date must be in the future'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if employee already has an active suspension
        active_suspension = EmployeeSuspension.objects.filter(employee=employee, is_active=True).first()
        if active_suspension:
            return Response({'error': 'Employee already has an active suspension'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if employee has a linked user account
        if not employee.user:
            return Response({'error': 'Employee does not have a user account linked'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create suspension record
                suspension = EmployeeSuspension.objects.create(
                    employee=employee,
                    reason=reason,
                    expiry_date=expiry_date,
                    remarks=remarks,
                    suspended_by=request.user,
                    is_active=True
                )
                
                # Update employee status
                employee.status = 'Suspended'
                employee.save(update_fields=['status'])
                
                # Deactivate user account
                employee.user.is_active = False
                employee.user.save(update_fields=['is_active'])
                
                # Log activity event
                try:
                    from activity_log.models import ActivityEvent, Verb
                    role = request.user.roles[0] if hasattr(request.user, 'roles') and request.user.roles else 'admin'
                    prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
                    ActivityEvent.objects.create(
                        timestamp=timezone.now(),
                        actor_id=request.user.id,
                        actor_role=role,
                        verb=Verb.STATUS_CHANGE,
                        target_type="HREmployee",
                        target_id=str(employee.id),
                        metadata={
                            'action': 'suspended',
                            'reason': reason,
                            'expiry_date': expiry_date.isoformat(),
                            'suspension_id': suspension.id
                        },
                        prev_hash=prev.hash if prev else None,
                        tenant_id="default"
                    )
                except Exception as e:
                    logger.warning(f"Failed to log suspension activity: {e}")
                
                serializer = EmployeeSuspensionSerializer(suspension, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Failed to suspend employee: {e}", exc_info=True)
            return Response({
                'error': f'Failed to suspend employee: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeEndSuspensionView(APIView):
    """End an active suspension (manually)"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk):
        """End active suspension"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Find active suspension
        active_suspension = EmployeeSuspension.objects.filter(employee=employee, is_active=True).first()
        if not active_suspension:
            return Response({'error': 'No active suspension found for this employee'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Mark suspension as ended
                active_suspension.is_active = False
                active_suspension.ended_at = timezone.now()
                active_suspension.ended_by = request.user
                active_suspension.save(update_fields=['is_active', 'ended_at', 'ended_by'])
                
                # Restore employee status to Active
                employee.status = 'Active'
                employee.save(update_fields=['status'])
                
                # Reactivate user account
                if employee.user:
                    employee.user.is_active = True
                    employee.user.save(update_fields=['is_active'])
                
                # Log activity event
                try:
                    from activity_log.models import ActivityEvent, Verb
                    role = request.user.roles[0] if hasattr(request.user, 'roles') and request.user.roles else 'admin'
                    prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
                    ActivityEvent.objects.create(
                        timestamp=timezone.now(),
                        actor_id=request.user.id,
                        actor_role=role,
                        verb=Verb.STATUS_CHANGE,
                        target_type="HREmployee",
                        target_id=str(employee.id),
                        metadata={
                            'action': 'suspension_ended',
                            'suspension_id': active_suspension.id,
                            'ended_manually': True
                        },
                        prev_hash=prev.hash if prev else None,
                        tenant_id="default"
                    )
                except Exception as e:
                    logger.warning(f"Failed to log suspension end activity: {e}")
                
                serializer = EmployeeSuspensionSerializer(active_suspension, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Failed to end suspension: {e}", exc_info=True)
            return Response({
                'error': f'Failed to end suspension: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeSuspensionHistoryView(APIView):
    """Get suspension history for an employee"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get all suspensions for an employee"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access permissions
        has_access, is_admin, is_finance = check_employee_access(request.user, employee)
        if not has_access:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        suspensions = EmployeeSuspension.objects.filter(employee=employee).order_by('-suspended_at')
        serializer = EmployeeSuspensionSerializer(suspensions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeeGrantExemptionView(APIView):
    """Grant a salary exemption to an employee"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk):
        """Grant exemption"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        exemption_type = request.data.get('exemption_type')
        reason = request.data.get('reason')
        expiry_date_str = request.data.get('expiry_date')
        remarks = request.data.get('remarks', '')
        
        if not exemption_type or exemption_type not in ['Temporary', 'Permanent']:
            return Response({'error': 'Invalid exemption type. Must be Temporary or Permanent'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not reason:
            return Response({'error': 'Reason is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate expiry_date for temporary exemptions
        expiry_date = None
        if exemption_type == 'Temporary':
            if not expiry_date_str:
                return Response({'error': 'Expiry date is required for temporary exemptions'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                from datetime import datetime
                expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
                if timezone.is_naive(expiry_date):
                    expiry_date = timezone.make_aware(expiry_date)
            except (ValueError, AttributeError):
                return Response({'error': 'Invalid expiry date format. Please use ISO format (YYYY-MM-DDTHH:mm:ss)'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate expiry_date is in the future
            if expiry_date <= timezone.now():
                return Response({'error': 'Expiry date must be in the future'}, status=status.HTTP_400_BAD_REQUEST)
        elif exemption_type == 'Permanent' and expiry_date_str:
            return Response({'error': 'Permanent exemptions should not have an expiry date'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if employee already has an active exemption
        active_exemption = EmployeeSalaryExemption.objects.filter(employee=employee, is_active=True).first()
        if active_exemption:
            return Response({'error': 'Employee already has an active exemption'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create exemption record
                exemption = EmployeeSalaryExemption.objects.create(
                    employee=employee,
                    exemption_type=exemption_type,
                    reason=reason,
                    expiry_date=expiry_date,
                    remarks=remarks,
                    granted_by=request.user,
                    is_active=True
                )
                
                # Log activity event
                try:
                    from activity_log.models import ActivityEvent, Verb
                    role = request.user.roles[0] if hasattr(request.user, 'roles') and request.user.roles else 'admin'
                    prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
                    ActivityEvent.objects.create(
                        timestamp=timezone.now(),
                        actor_id=request.user.id,
                        actor_role=role,
                        verb=Verb.STATUS_CHANGE,
                        target_type="HREmployee",
                        target_id=str(employee.id),
                        metadata={
                            'action': 'exemption_granted',
                            'exemption_type': exemption_type,
                            'reason': reason,
                            'expiry_date': expiry_date.isoformat() if expiry_date else None,
                            'exemption_id': exemption.id
                        },
                        prev_hash=prev.hash if prev else None,
                        tenant_id="default"
                    )
                except Exception as e:
                    logger.warning(f"Failed to log exemption activity: {e}")
                
                serializer = EmployeeSalaryExemptionSerializer(exemption, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Failed to grant exemption: {e}", exc_info=True)
            return Response({
                'error': f'Failed to grant exemption: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeEndExemptionView(APIView):
    """End an active salary exemption (manually)"""
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']
    
    def post(self, request, pk):
        """End active exemption"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_admin = request.user.has_role('admin') if hasattr(request.user, 'has_role') else request.user.is_staff
        if not is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Find active exemption
        active_exemption = EmployeeSalaryExemption.objects.filter(employee=employee, is_active=True).first()
        if not active_exemption:
            return Response({'error': 'No active exemption found for this employee'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Mark exemption as ended
                active_exemption.is_active = False
                active_exemption.ended_at = timezone.now()
                active_exemption.ended_by = request.user
                active_exemption.save(update_fields=['is_active', 'ended_at', 'ended_by'])
                
                # Log activity event
                try:
                    from activity_log.models import ActivityEvent, Verb
                    role = request.user.roles[0] if hasattr(request.user, 'roles') and request.user.roles else 'admin'
                    prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
                    ActivityEvent.objects.create(
                        timestamp=timezone.now(),
                        actor_id=request.user.id,
                        actor_role=role,
                        verb=Verb.STATUS_CHANGE,
                        target_type="HREmployee",
                        target_id=str(employee.id),
                        metadata={
                            'action': 'exemption_ended',
                            'exemption_id': active_exemption.id,
                            'exemption_type': active_exemption.exemption_type,
                            'ended_manually': True
                        },
                        prev_hash=prev.hash if prev else None,
                        tenant_id="default"
                    )
                except Exception as e:
                    logger.warning(f"Failed to log exemption end activity: {e}")
                
                serializer = EmployeeSalaryExemptionSerializer(active_exemption, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Failed to end exemption: {e}", exc_info=True)
            return Response({
                'error': f'Failed to end exemption: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeExemptionHistoryView(APIView):
    """Get exemption history for an employee"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get all salary exemptions for an employee"""
        try:
            employee = HREmployee.objects.get(pk=pk)
        except HREmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check access permissions
        has_access, is_admin, is_finance = check_employee_access(request.user, employee)
        if not has_access:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        exemptions = EmployeeSalaryExemption.objects.filter(employee=employee).order_by('-granted_at')
        serializer = EmployeeSalaryExemptionSerializer(exemptions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# Create your views here.

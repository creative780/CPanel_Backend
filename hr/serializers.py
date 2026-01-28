from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from pathlib import Path
import base64
import re
import uuid
import logging
from monitoring.models import Employee
from .models import (
    SalarySlip, HREmployee, EmployeePersonalDetails, EmployeeFamilyMember,
    EmployeeEmergencyContact, EmployeeReference, EmployeeBankDetails,
    EmployeeDocument, EmployeeVerification, EmployeeExemption, EmployeeSuspension,
    EmployeeSalaryExemption
)

User = get_user_model()
logger = logging.getLogger(__name__)


class ImageField(serializers.CharField):
    """Custom field that converts data URLs to file URLs before validation and returns full URLs when reading"""
    
    def to_internal_value(self, data):
        """Convert data URLs to file URLs before any validation"""
        if not data or (isinstance(data, str) and data.strip() == ""):
            return super().to_internal_value(data)
        
        if isinstance(data, str):
            data = data.strip()
            
            # If it's a data URL, convert it to a file URL first
            if data.startswith('data:image/'):
                try:
                    return self._convert_data_url_to_file(data)
                except Exception as e:
                    raise serializers.ValidationError(f"Failed to process image: {str(e)}")
        
        return super().to_internal_value(data)
    
    def to_representation(self, value):
        """Convert relative URLs to full URLs when reading"""
        if not value:
            return value
        
        # If it's already a full URL (http:// or https://), return as is
        if isinstance(value, str) and (value.startswith('http://') or value.startswith('https://')):
            return value
        
        # If it's a relative URL (starts with /), convert to full URL
        if isinstance(value, str) and value.startswith('/'):
            # Get the request from parent serializer's context
            parent = self.parent
            request = None
            if parent and hasattr(parent, 'context') and parent.context:
                request = parent.context.get('request')
            
            if request:
                try:
                    return request.build_absolute_uri(value)
                except Exception as e:
                    # Log the error but don't fail - fall through to fallback
                    logger.warning(f"Failed to build absolute URI: {e}")
            
            # Fallback: construct URL from settings
            # In development, use localhost:8000
            if settings.DEBUG:
                return f"http://127.0.0.1:8000{value}"
            else:
                # In production, try to get from ALLOWED_HOSTS or use default
                try:
                    from django.contrib.sites.models import Site
                    current_site = Site.objects.get_current()
                    protocol = 'https'
                    return f"{protocol}://{current_site.domain}{value}"
                except Exception as e:
                    # Log the error for debugging
                    logger.warning(f"Failed to get Site model: {e}")
                    # Final fallback: use first allowed host or default
                    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
                    if allowed_hosts and allowed_hosts[0] != '*':
                        return f"https://{allowed_hosts[0]}{value}"
                    # Last resort: return relative URL as-is to avoid breaking the response
                    logger.error(f"Could not build absolute URL for {value}, returning relative URL")
                    return value
        
        return value
    
    def _convert_data_url_to_file(self, data_url):
        """Convert data URL to file and return file URL"""
        # Validate data URL format: data:image/<type>;base64,<data>
        if ';base64,' not in data_url:
            raise ValueError("Invalid data URL format")
        
        # Match pattern: data:image/<type>;base64,<data>
        data_url_pattern = re.compile(r'^data:image/(?P<mime>[^;]+);base64,(?P<data>.+)$')
        match = data_url_pattern.match(data_url)
        if not match:
            raise ValueError("Invalid data URL format")
        
        mime = match.group('mime')
        data_b64 = match.group('data')
        
        # Decode base64
        try:
            raw = base64.b64decode(data_b64)
        except Exception:
            raise ValueError("Invalid base64 data in image")
        
        # Check file size (max 5MB)
        if len(raw) > 5 * 1024 * 1024:
            raise ValueError("Image file too large (max 5MB)")
        
        # Determine file extension
        ext_map = {
            'jpeg': 'jpg',
            'jpg': 'jpg',
            'png': 'png',
            'gif': 'gif',
            'webp': 'webp'
        }
        ext = ext_map.get(mime.lower(), 'jpg')
        
        # Generate unique filename
        fname = f"employee_image_{uuid.uuid4().hex}.{ext}"
        
        # Ensure media root exists
        upload_dir = Path(settings.MEDIA_ROOT)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        full_path = upload_dir / fname
        try:
            with open(full_path, 'wb') as f:
                f.write(raw)
            logger.info(f"Successfully saved employee image to: {full_path} (size: {len(raw)} bytes)")
            
            # Verify file was actually written
            if not full_path.exists():
                logger.error(f"File was not created at {full_path} even though write succeeded!")
            else:
                file_size = full_path.stat().st_size
                logger.info(f"File exists at {full_path}, size: {file_size} bytes")
        except Exception as e:
            logger.error(f"Failed to save employee image to {full_path}: {e}", exc_info=True)
            raise ValueError(f"Failed to save image file: {str(e)}")
        
        # Return the file URL instead of data URL
        file_url = f"{settings.MEDIA_URL}{fname}"
        logger.info(f"Returning file URL: {file_url} (MEDIA_URL={settings.MEDIA_URL}, MEDIA_ROOT={settings.MEDIA_ROOT})")
        return file_url


class HREmployeeSerializer(serializers.ModelSerializer):
    """Serializer for HR Employee model"""
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    user_id = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    current_suspension = serializers.SerializerMethodField()
    current_salary_exemption = serializers.SerializerMethodField()
    
    # Add explicit validation for role to match model choices
    role = serializers.ChoiceField(choices=HREmployee.ROLE_CHOICES, required=True)
    status = serializers.ChoiceField(choices=HREmployee.STATUS_CHOICES, required=False)
    branch = serializers.ChoiceField(choices=HREmployee.BRANCH_CHOICES, required=False)
    salary_status = serializers.ChoiceField(choices=HREmployee.SALARY_STATUS_CHOICES, required=False)
    
    # Add explicit email validation
    email = serializers.EmailField(required=True)
    
    # Image field - accepts both URLs and data URLs (base64 encoded images)
    # Custom field converts data URLs to file URLs before validation
    image = ImageField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = HREmployee
        fields = [
            'id', 'name', 'email', 'phone', 'image', 'salary', 'designation', 
            'status', 'branch', 'role', 'department', 'manager', 'phone_verified',
            'phone_verified_at', 'salary_status', 'verification_status',
            'user_id', 'is_active', 'username', 'password', 'current_suspension', 'current_salary_exemption',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_id', 'is_active', 'phone_verified_at', 'current_suspension', 'current_salary_exemption']
    
    def get_user_id(self, obj):
        """Safely get user ID, returning None if user doesn't exist"""
        return obj.user.id if obj.user else None
    
    def get_is_active(self, obj):
        """Safely get user is_active status, returning None if user doesn't exist"""
        return obj.user.is_active if obj.user else None
    
    def get_current_suspension(self, obj):
        """Get active suspension if exists"""
        try:
            active_suspension = obj.suspensions.filter(is_active=True).first()
            if active_suspension:
                return EmployeeSuspensionSerializer(active_suspension, context=self.context).data
        except Exception:
            pass
        return None
    
    def get_current_salary_exemption(self, obj):
        """Get active salary exemption if exists"""
        try:
            active_exemption = obj.salary_exemptions.filter(is_active=True).first()
            if active_exemption:
                return EmployeeSalaryExemptionSerializer(active_exemption, context=self.context).data
        except Exception:
            pass
        return None
    
    def validate_image(self, value):
        """Validate image field - data URLs are already converted to file URLs by ImageField.to_internal_value"""
        if not value or value.strip() == "":
            return value
        
        value = value.strip()
        
        # At this point, data URLs have already been converted to file URLs by ImageField.to_internal_value
        # So we only need to validate regular URLs
        if value.startswith('http://') or value.startswith('https://'):
            try:
                from django.core.validators import URLValidator
                validator = URLValidator()
                validator(value)
                return value
            except Exception:
                raise serializers.ValidationError("Enter a valid URL")
        
        # File URLs (from data URL conversion) or relative paths are valid
        # They should already be short enough for the model's max_length=500
        return value
    
    def to_representation(self, instance):
        """Override to convert relative image URLs to full URLs"""
        try:
            data = super().to_representation(instance)
            
            # Convert relative image URL to full URL if needed
            if data.get('image') and isinstance(data['image'], str):
                image_url = data['image']
                # If it's already a full URL, keep it
                if image_url.startswith('http://') or image_url.startswith('https://'):
                    return data
                
                # If it's a relative URL, convert to full URL
                if image_url.startswith('/'):
                    request = self.context.get('request') if self.context else None
                    if request:
                        try:
                            data['image'] = request.build_absolute_uri(image_url)
                        except Exception as e:
                            logger.warning(f"Failed to build absolute URI for image: {e}")
                            # Fall through to fallback
                            pass
                    
                    # Fallback if request is None or build_absolute_uri failed
                    if not request or not data['image'].startswith('http'):
                        if settings.DEBUG:
                            data['image'] = f"http://127.0.0.1:8000{image_url}"
                        else:
                            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
                            if allowed_hosts and allowed_hosts[0] != '*':
                                data['image'] = f"https://{allowed_hosts[0]}{image_url}"
                            else:
                                # Keep relative URL if all else fails
                                logger.warning(f"Could not build absolute URL for image: {image_url}")
            
            return data
        except Exception as e:
            # Log the error but return a minimal representation to prevent complete failure
            logger.error(f"Failed to serialize employee {instance.id} ({instance.name}): {e}", exc_info=True)
            # Return minimal data to prevent breaking the entire response
            return {
                'id': instance.id,
                'name': instance.name,
                'email': instance.email,
                'error': 'Serialization error - some fields may be missing'
            }
    
    def validate_username(self, value):
        """Validate that username is unique if provided"""
        if value:
            # Normalize username: trim whitespace and convert to lowercase for case-insensitive check
            normalized_username = value.strip()
            
            # Validate username format (alphanumeric, underscore, hyphen, dot, @, plus)
            # Django's username validator allows: letters, digits and @/./+/-/_ only
            from django.contrib.auth.validators import UnicodeUsernameValidator
            validator = UnicodeUsernameValidator()
            try:
                validator(normalized_username)
            except Exception:
                raise serializers.ValidationError(
                    "Username can only contain letters, numbers, and @/./+/-/_ characters."
                )
            
            # Check length (Django username max_length is 150)
            if len(normalized_username) > 150:
                raise serializers.ValidationError("Username must be 150 characters or fewer.")
            
            if len(normalized_username) < 1:
                raise serializers.ValidationError("Username cannot be empty.")
            
            # Case-insensitive uniqueness check
            # Exclude current employee's user if updating
            existing_user = User.objects.filter(username__iexact=normalized_username).first()
            if existing_user:
                # If updating, exclude the current employee's user
                if self.instance and self.instance.user:
                    if existing_user.id != self.instance.user.id:
                        raise serializers.ValidationError("Username already exists. Please choose a different username.")
                else:
                    # Creating new employee, username must be unique
                    raise serializers.ValidationError("Username already exists. Please choose a different username.")
            
            # Also check exact match (in case database is case-sensitive)
            if User.objects.filter(username=normalized_username).exists():
                if self.instance and self.instance.user:
                    if User.objects.filter(username=normalized_username).exclude(id=self.instance.user.id).exists():
                        raise serializers.ValidationError("Username already exists. Please choose a different username.")
                else:
                    raise serializers.ValidationError("Username already exists. Please choose a different username.")
            
            # Return normalized username
            return normalized_username
        return value
    
    def validate_email(self, value):
        """Validate that email is unique if provided"""
        if value:
            # Normalize email: trim whitespace and convert to lowercase
            normalized_email = value.strip().lower()
            
            # Check if email already exists in HREmployee (case-insensitive)
            if self.instance is None:  # Creating new employee
                if HREmployee.objects.filter(email__iexact=normalized_email).exists():
                    raise serializers.ValidationError("An employee with this email already exists.")
                # Also check User model since we'll create a User with this email
                if User.objects.filter(email__iexact=normalized_email).exists():
                    raise serializers.ValidationError("A user with this email already exists.")
            else:  # Updating existing employee
                if HREmployee.objects.filter(email__iexact=normalized_email).exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError("An employee with this email already exists.")
                # Check User model, but exclude the current employee's user if it exists
                existing_user = self.instance.user
                if existing_user:
                    if User.objects.filter(email__iexact=normalized_email).exclude(pk=existing_user.pk).exists():
                        raise serializers.ValidationError("A user with this email already exists.")
                else:
                    if User.objects.filter(email__iexact=normalized_email).exists():
                        raise serializers.ValidationError("A user with this email already exists.")
            
            # Return normalized email
            return normalized_email
        return value
    
    def create(self, validated_data):
        """Create HREmployee and associated User"""
        from django.db import transaction
        
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        
        # Ensure default values for new fields
        if 'department' not in validated_data:
            validated_data['department'] = ''
        if 'salary_status' not in validated_data:
            validated_data['salary_status'] = 'ON_HOLD'
        if 'verification_status' not in validated_data:
            validated_data['verification_status'] = 'not_started'
        
        # Use atomic transaction to ensure both user and employee are created together
        # or both are rolled back if either fails
        with transaction.atomic():
            user = None
            
            # Create User if username and password provided
            if username and password:
                # Username is already normalized in validate_username
                # Email is already normalized in validate_email
                # Safe name splitting - handle empty, single word, and multi-word names
                name = validated_data.get('name', '').strip()
                name_parts = name.split() if name else []
                first_name = name_parts[0] if len(name_parts) > 0 else ''
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                user = User.objects.create_user(
                    username=username,  # Already normalized
                    email=validated_data['email'],  # Already normalized
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    roles=[validated_data.get('role', 'sales')]  # Set the role
                )
            
            # Create HREmployee
            # If this fails, the transaction will automatically rollback the user creation
            hr_employee = HREmployee.objects.create(
                user=user,
                **validated_data
            )
            
            return hr_employee
    
    def update(self, instance, validated_data):
        """Update HREmployee and associated User"""
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        new_role = validated_data.get('role', None)  # Extract role if provided
        
        # Use atomic transaction to ensure all updates happen together
        with transaction.atomic():
            # Update or create User if credentials provided
            if username or password:
                user_updated = False
                
                # Get or create user
                if not instance.user:
                    # Create new user if doesn't exist
                    if username and password:
                        # Normalize username
                        normalized_username = username.strip()
                        # Safe name splitting
                        name = validated_data.get('name', instance.name or '').strip()
                        name_parts = name.split() if name else []
                        first_name = name_parts[0] if len(name_parts) > 0 else ''
                        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                        
                        instance.user = User.objects.create_user(
                            username=normalized_username,
                            email=validated_data.get('email', instance.email),
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                            roles=[validated_data.get('role', instance.role or 'sales')]
                        )
                        user_updated = True
                else:
                    # Update existing user
                    # Update username if provided
                    if username:
                        # Normalize username (same as in validate_username)
                        normalized_username = username.strip()
                        if instance.user.username != normalized_username:
                            instance.user.username = normalized_username
                            user_updated = True
                    
                    # Update password if provided
                    if password:
                        # set_password() properly hashes the password and replaces the old hash
                        # This makes the old password invalid immediately
                        instance.user.set_password(password)
                        user_updated = True
                    
                    # Save user if any changes were made
                    if user_updated:
                        instance.user.save()
                        
                        # Invalidate all existing sessions for this user
                        # This ensures old sessions with old credentials won't work
                        try:
                            # Delete all sessions for this user
                            # Django sessions store user_id in session_data
                            sessions = Session.objects.filter(expire_date__gte=timezone.now())
                            for session in sessions:
                                try:
                                    session_data = session.get_decoded()
                                    if session_data.get('_auth_user_id') == str(instance.user.id):
                                        session.delete()
                                except Exception:
                                    # Skip sessions that can't be decoded
                                    continue
                        except Exception as e:
                            # Log but don't fail the update if session deletion fails
                            logger.warning(f"Failed to invalidate sessions for user {instance.user.id}: {e}")
            
            # Update HREmployee
            old_role = instance.role  # Store old role before update
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Update User's roles if employee role changed
            if new_role and instance.user and old_role != new_role:
                # Update User's roles field to match the new employee role
                instance.user.roles = [new_role]
                instance.user.save(update_fields=['roles'])
                logger.info(f"Updated User {instance.user.id} roles to [{new_role}] to match employee role change from {old_role}")
        
        return instance


class LegacyHREmployeeSerializer(serializers.ModelSerializer):
    """Legacy serializer for monitoring.Employee model"""
    class Meta:
        model = Employee
        fields = ['id', 'name', 'salary', 'designation', 'email', 'phone', 'image']


class SalarySlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalarySlip
        fields = ['id', 'employee', 'period', 'gross', 'net', 'meta', 'created_at']


class EmployeeFamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFamilyMember
        fields = ['id', 'relationship', 'name', 'phone', 'email', 'occupation', 'address']


class EmployeeEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEmergencyContact
        fields = ['id', 'name', 'relationship', 'phone', 'email', 'address', 'is_primary']


class EmployeeReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeReference
        fields = ['id', 'name', 'company', 'position', 'phone', 'email', 'relationship', 'otp_verified']


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'document_type', 'address_proof_type', 'file', 'file_url', 'expiry_date',
            'days_until_expiry', 'is_expiring_soon', 'status',
            'uploaded_at', 'verified_at', 'verified_by'
        ]
        read_only_fields = ['uploaded_at', 'verified_at']
    
    def get_file_url(self, obj):
        """Return secure download endpoint URL instead of direct media URL"""
        if not obj.file or not obj.id or not obj.employee_id:
            return None
        
        try:
            # Return secure download endpoint URL
            request = self.context.get('request')
            if request:
                try:
                    # Build the secure download endpoint URL
                    secure_url = f'/api/hr/employees/{obj.employee_id}/documents/{obj.id}/download'
                    return request.build_absolute_uri(secure_url)
                except Exception as uri_error:
                    # If building absolute URI fails, return relative URL
                    return f'/api/hr/employees/{obj.employee_id}/documents/{obj.id}/download'
            else:
                # If no request context, return relative URL
                return f'/api/hr/employees/{obj.employee_id}/documents/{obj.id}/download'
        except Exception as e:
            # Catch any unexpected errors and return None instead of crashing
            return None
    
    def get_days_until_expiry(self, obj):
        if obj.expiry_date:
            from django.utils import timezone
            delta = obj.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    def get_is_expiring_soon(self, obj):
        days = self.get_days_until_expiry(obj)
        if days is not None:
            return days <= 60
        return False


class EmployeeBankDetailsSerializer(serializers.ModelSerializer):
    iban_masked = serializers.SerializerMethodField()
    account_holder_masked = serializers.SerializerMethodField()
    proof_document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeBankDetails
        fields = [
            'id', 'bank_name', 'account_holder_name', 'account_holder_masked',
            'account_number', 'iban', 'iban_masked', 'swift_code', 'branch_name',
            'proof_document', 'proof_document_url',
            'status', 'verified_at', 'verified_by', 'verification_requested_at',
            'rejection_reason', 'rejected_by', 'rejected_at',
            'exemption_reason', 'exemption_granted_at', 'exemption_granted_by'
        ]
        read_only_fields = [
            'verified_at', 'verified_by', 'verification_requested_at',
            'rejected_by', 'rejected_at', 'exemption_granted_at', 'exemption_granted_by'
        ]
    
    def get_iban_masked(self, obj):
        """Mask IBAN for security - show only last 4 digits"""
        if obj.iban and len(obj.iban) > 4:
            return '*' * (len(obj.iban) - 4) + obj.iban[-4:]
        return obj.iban
    
    def get_account_holder_masked(self, obj):
        """Mask account holder name - show only first and last letter"""
        if obj.account_holder_name:
            name_parts = obj.account_holder_name.split()
            if len(name_parts) > 1:
                return f"{name_parts[0][0]}{'*' * (len(name_parts[0]) - 2)}{name_parts[0][-1]} {name_parts[-1][0]}{'*' * (len(name_parts[-1]) - 2)}{name_parts[-1][-1]}"
            elif len(obj.account_holder_name) > 2:
                return f"{obj.account_holder_name[0]}{'*' * (len(obj.account_holder_name) - 2)}{obj.account_holder_name[-1]}"
        return obj.account_holder_name
    
    def get_proof_document_url(self, obj):
        """Return secure URL for proof document"""
        if obj.proof_document and obj.employee_id:
            try:
                request = self.context.get('request')
                if request:
                    # Return secure download URL if available, otherwise direct URL
                    return request.build_absolute_uri(obj.proof_document.url)
                return obj.proof_document.url
            except Exception:
                return obj.proof_document.url if obj.proof_document else None
        return None


class EmployeePersonalDetailsSerializer(serializers.ModelSerializer):
    family_members = EmployeeFamilyMemberSerializer(many=True, read_only=True)
    emergency_contacts = EmployeeEmergencyContactSerializer(many=True, read_only=True)
    
    class Meta:
        model = EmployeePersonalDetails
        fields = [
            'gender', 'date_of_birth', 'nationality', 'marital_status',
            'blood_group', 'present_address', 'permanent_address',
            'family_members', 'emergency_contacts'
        ]


class EmployeeVerificationSerializer(serializers.ModelSerializer):
    verification_percentage = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = EmployeeVerification
        fields = [
            'phone_verified', 'email_verified', 'reference_verified',
            'bank_verified', 'address_proof_verified', 'verification_percentage',
            'last_updated'
        ]


class EmployeeQuickInfoSerializer(serializers.ModelSerializer):
    """Quick info tab serializer"""
    verification = EmployeeVerificationSerializer(read_only=True)
    manager_name = serializers.CharField(source='manager.name', read_only=True)
    manager_id = serializers.IntegerField(source='manager.id', read_only=True)
    exemption = serializers.SerializerMethodField()
    
    class Meta:
        model = HREmployee
        fields = [
            'id', 'name', 'image', 'email', 'phone', 'phone_verified',
            'department', 'branch', 'designation', 'role', 'status',
            'salary_status', 'verification_status', 'verification',
            'manager_name', 'manager_id', 'exemption', 'created_at'
        ]
    
    def get_exemption(self, obj):
        try:
            exemption = obj.exemption
            if exemption.bank_exempted:
                return {
                    'bank_exempted': True,
                    'bank_exemption_reason': exemption.bank_exemption_reason,
                    'bank_exempted_at': exemption.bank_exempted_at.isoformat() if exemption.bank_exempted_at else None,
                    'bank_exempted_by': exemption.bank_exempted_by.username if exemption.bank_exempted_by else None,
                }
        except EmployeeExemption.DoesNotExist:
            pass
        return {'bank_exempted': False}


class EmployeePayrollSerializer(serializers.ModelSerializer):
    """Payroll tab serializer with masked bank details"""
    bank_details = EmployeeBankDetailsSerializer(read_only=True)
    gross_salary = serializers.DecimalField(source='salary', max_digits=12, decimal_places=2, read_only=True)
    hourly_rate = serializers.SerializerMethodField()
    salary_status_logs = serializers.SerializerMethodField()
    
    class Meta:
        model = HREmployee
        fields = [
            'id', 'name', 'salary', 'gross_salary', 'hourly_rate',
            'salary_status', 'bank_details', 'salary_status_logs'
        ]
    
    def get_hourly_rate(self, obj):
        """Calculate hourly rate (assuming 8 hours/day, 22 working days/month)"""
        if obj.salary:
            monthly_hours = 8 * 22  # 176 hours per month
            return float(obj.salary) / monthly_hours
        return 0
    
    def get_salary_status_logs(self, obj):
        """Get salary status change logs"""
        from .models import SalaryStatusLog
        logs = SalaryStatusLog.objects.filter(employee=obj).order_by('-changed_at')[:10]
        return [
            {
                'old_status': log.old_status,
                'new_status': log.new_status,
                'reason': log.reason,
                'changed_by': log.changed_by.username if log.changed_by else None,
                'changed_at': log.changed_at.isoformat()
            }
            for log in logs
        ]


class EmployeeDocumentsSerializer(serializers.ModelSerializer):
    """Documents tab serializer"""
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    expiring_documents = serializers.SerializerMethodField()
    
    class Meta:
        model = HREmployee
        fields = ['id', 'name', 'documents', 'expiring_documents']
    
    def get_expiring_documents(self, obj):
        """Get documents expiring within 60 days"""
        from django.utils import timezone
        from datetime import timedelta
        threshold = timezone.now().date() + timedelta(days=60)
        expiring = obj.documents.filter(
            expiry_date__lte=threshold,
            expiry_date__gte=timezone.now().date(),
            status__in=['uploaded', 'verified']
        )
        return EmployeeDocumentSerializer(expiring, many=True).data


class EmployeeSuspensionSerializer(serializers.ModelSerializer):
    """Serializer for Employee Suspension records"""
    suspended_by_username = serializers.CharField(source='suspended_by.username', read_only=True)
    ended_by_username = serializers.CharField(source='ended_by.username', read_only=True, allow_null=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = EmployeeSuspension
        fields = [
            'id', 'employee', 'employee_name', 'reason', 'expiry_date', 'remarks',
            'suspended_by', 'suspended_by_username', 'suspended_at',
            'ended_at', 'ended_by', 'ended_by_username', 'is_active'
        ]
        read_only_fields = ['id', 'suspended_at', 'suspended_by_username', 'ended_by_username', 'employee_name']


class EmployeeSalaryExemptionSerializer(serializers.ModelSerializer):
    """Serializer for Employee Salary Exemption records"""
    granted_by_username = serializers.CharField(source='granted_by.username', read_only=True)
    ended_by_username = serializers.CharField(source='ended_by.username', read_only=True, allow_null=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    exemption_type = serializers.ChoiceField(choices=EmployeeSalaryExemption.EXEMPTION_TYPE_CHOICES)
    
    class Meta:
        model = EmployeeSalaryExemption
        fields = [
            'id', 'employee', 'employee_name', 'exemption_type', 'reason', 'expiry_date', 'remarks',
            'granted_by', 'granted_by_username', 'granted_at',
            'ended_at', 'ended_by', 'ended_by_username', 'is_active'
        ]
        read_only_fields = ['id', 'granted_at', 'granted_by_username', 'ended_by_username', 'employee_name']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Complete profile serializer with all nested data"""
    personal_details = EmployeePersonalDetailsSerializer(read_only=True)
    bank_details = EmployeeBankDetailsSerializer(read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    verification = EmployeeVerificationSerializer(read_only=True)
    references = EmployeeReferenceSerializer(many=True, read_only=True)
    
    class Meta:
        model = HREmployee
        fields = [
            'id', 'name', 'email', 'phone', 'image', 'salary', 'designation',
            'status', 'branch', 'role', 'department', 'manager',
            'phone_verified', 'salary_status', 'verification_status',
            'personal_details', 'bank_details', 'documents', 'verification',
            'references', 'created_at', 'updated_at'
        ]




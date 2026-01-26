from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    USER = 'user', 'User'
    SALES = 'sales', 'Sales'
    DESIGNER = 'designer', 'Designer'
    PRODUCTION = 'production', 'Production'
    DELIVERY = 'delivery', 'Delivery'
    FINANCE = 'finance', 'Finance'


class User(AbstractUser):
    roles = models.JSONField(default=list, blank=True)
    mfa_phone = models.CharField(max_length=32, blank=True, null=True)
    mfa_email_otp_enabled = models.BooleanField(default=False)
    org_id = models.CharField(max_length=25, null=True, blank=True)  # Reference to monitoring.Org
    
    # Matrix integration fields
    matrix_user_id = models.CharField(max_length=255, blank=True, null=True, help_text="Matrix user ID (e.g. @username:chat.local)")
    matrix_access_token = models.TextField(blank=True, null=True, help_text="Matrix access token (encrypted in production)")
    matrix_synced = models.BooleanField(default=False, help_text="Whether this user has been synced to Matrix")

    def has_role(self, role: str) -> bool:
        return role in (self.roles or [])
    
    def is_admin(self) -> bool:
        return self.has_role('admin')
    
    def get_matrix_user_id(self, server_name: str = "chat.local") -> str:
        """Generate Matrix user ID from username"""
        if self.matrix_user_id:
            return self.matrix_user_id
        # Matrix user IDs are case-insensitive, but we'll use lowercase
        return f"@{self.username.lower()}:{server_name}"

# Create your models here.

import os
import django
from django.conf import settings
from django.utils import timezone
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

from monitoring.models import Device, DeviceToken
from accounts.models import User
from monitoring.auth_utils import create_device_token

def fix_device_auth():
    print("Fixing device authentication issues...")
    
    # Ensure all devices have a token
    devices = Device.objects.all()
    print(f"Found {devices.count()} devices")
    
    for device in devices:
        print(f"Processing device: {device.id} - {device.hostname}")
        
        # Ensure device has a token
        if not DeviceToken.objects.filter(device=device).exists():
            try:
                token = create_device_token(device)
                print(f"  Created new token for device {device.id}: {token.token}")
            except Exception as e:
                print(f"  Failed to create token for device {device.id}: {e}")
        else:
            print(f"  Device {device.id} already has a token.")
        
        # Ensure device is bound to a user
        if not device.current_user:
            # Try to find an active user to bind to
            user = User.objects.filter(is_active=True).first()
            if user:
                device.current_user = user
                device.current_user_name = user.get_full_name() or user.username
                user_roles = getattr(user, 'roles', [])
                primary_role = user_roles[0] if user_roles else 'sales'
                device.current_user_role = primary_role
                device.last_user_bind_at = timezone.now()
                device.save(update_fields=['current_user', 'current_user_name', 'current_user_role', 'last_user_bind_at'])
                print(f"  Bound device {device.id} to user {user.username}")
            else:
                print(f"  No active user found to bind device {device.id} to.")
        else:
            print(f"  Device {device.id} is already bound to user {device.current_user.username}.")
    
    print("Device authentication fix script completed.")

if __name__ == '__main__':
    fix_device_auth()
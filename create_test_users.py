#!/usr/bin/env python
"""Create test users for order assignment testing"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_user(username, email, password, roles):
    """Create or update test user"""
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'roles': roles}
    )
    user.set_password(password)
    user.is_active = True
    user.roles = roles
    user.save()
    status = "created" if created else "exists"
    print(f"  ✓ {username}: {status}")
    return user

print("Creating test users...\n")

create_test_user('admin_test', 'admin@test.com', 'admin123', ['admin'])
create_test_user('designer1', 'designer1@test.com', 'designer123', ['designer'])
create_test_user('designer2', 'designer2@test.com', 'designer123', ['designer'])
create_test_user('production1', 'production1@test.com', 'production123', ['production'])
create_test_user('production2', 'production2@test.com', 'production123', ['production'])

print("\n✓ All test users ready!")

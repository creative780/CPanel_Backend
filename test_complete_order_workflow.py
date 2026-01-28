#!/usr/bin/env python
"""
Complete Order Lifecycle Workflow Test Script

This script tests the complete order workflow from sales creation through delivery.

Usage:
    python test_complete_order_workflow.py

Prerequisites:
    - Django backend running on http://127.0.0.1:8000
    - Test users created (run: python manage.py setup_test_users)
"""

import os
import sys
import django
import requests
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem, DesignApproval, ProductMachineAssignment
from django.utils import timezone

User = get_user_model()

# Try to import Device model for test device
try:
    from monitoring.models import Device
    DEVICE_MODEL_AVAILABLE = True
except ImportError:
    DEVICE_MODEL_AVAILABLE = False
    Device = None

# Test configuration
BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
API_URL = f'{BASE_URL}/api'

# Test users - use email as username to match setup_test_users command
TEST_USERS = {
    'sales': {'username': 'sales@test.com', 'password': 'sales123', 'email': 'sales@test.com'},
    'designer': {'username': 'designer@test.com', 'password': 'designer123', 'email': 'designer@test.com'},
    'production': {'username': 'production@test.com', 'password': 'production123', 'email': 'production@test.com'},
    'delivery': {'username': 'delivery@test.com', 'password': 'delivery123', 'email': 'delivery@test.com'},
}

# Test data
TEST_CLIENT = {
    'clientName': "John's Printing Shop",
    'companyName': "John's Printing LLC",
    'phone': "+971501234567",
    'email': 'john@printing.com',
    'address': '123 Business Street, Dubai, UAE',
    'specifications': 'High-quality business cards with gold foil stamping',
    'urgency': 'Normal'
}

TEST_PRODUCTS = [
    {
        'product_id': 'BC-GOLD-001',
        'name': 'Business Card Gold',
        'quantity': 100,
        'attributes': {
            'paper': '300gsm Premium',
            'lamination': 'Matte',
            'printing_sides': 'Double-sided'
        },
        'unit_price': 25.00,
        'custom_requirements': 'Add company logo'
    },
    {
        'product_id': 'CANVAS-A3-001',
        'name': 'Canvas Print A3',
        'quantity': 5,
        'attributes': {
            'paper': 'Canvas',
            'lamination': 'Glossy',
            'printing_sides': 'Single-sided'
        },
        'unit_price': 50.00,
        'custom_requirements': 'High resolution print'
    }
]

class TestOrderWorkflow:
    def __init__(self):
        self.tokens = {}
        self.order_id = None
        self.approval_id = None
        self.assignment_ids = []
        self.errors = []
        self.device_id = None
        
    def log(self, message, level='INFO'):
        """Log message with timestamp"""
        import sys
        # Set UTF-8 encoding for Windows console
        if sys.platform == 'win32':
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '[OK]',
            'ERROR': '[ERROR]',
            'WARNING': '[WARN]',
            'STEP': '>>>'
        }.get(level, '[*]')
        print(f'[{timestamp}] {prefix} {message}')
        
    def error(self, message):
        """Log error and add to errors list"""
        self.log(message, 'ERROR')
        self.errors.append(message)
        
    def step(self, message):
        """Log test step"""
        self.log(message, 'STEP')
        
    def create_test_device(self):
        """Create a test device with heartbeat for API authentication"""
        if not DEVICE_MODEL_AVAILABLE:
            # Use a hardcoded test device ID if Device model not available
            self.device_id = 'test-device-id-for-api-testing'
            self.log(f"Using test device ID: {self.device_id}")
            return
            
        try:
            from monitoring.models import Heartbeat
            
            # Try to create device without Org first (Org is nullable)
            device_id = 'test-device-for-workflow-test'
            
            try:
                device = Device.objects.get(id=device_id)
                self.log(f"Found existing device: {device_id}")
            except Device.DoesNotExist:
                # Create device without Org to avoid schema issues
                device = Device.objects.create(
                    id=device_id,
                    hostname='TEST-MACHINE',
                    ip='127.0.0.1',
                    os='Windows',
                    status='ONLINE',
                    org=None,  # Skip Org to avoid schema issues
                    last_heartbeat=timezone.now()
                )
                self.log(f"Created test device: {device_id}")
            
            # Always ensure device has recent heartbeat (within 2 minutes)
            device.last_heartbeat = timezone.now()
            device.status = 'ONLINE'
            device.save(update_fields=['last_heartbeat', 'status'])
            
            # Also create a Heartbeat record for completeness
            try:
                Heartbeat.objects.create(
                    device=device,
                    cpu_percent=10.0,
                    mem_percent=20.0,
                    active_window='test',
                    is_locked=False
                )
            except Exception as hb_error:
                self.log(f"Could not create heartbeat record (this is OK): {hb_error}", 'WARNING')
            
            self.device_id = device.id
            self.log(f"Device {self.device_id} ready with recent heartbeat: {device.last_heartbeat}")
        except Exception as e:
            # Fallback to hardcoded device ID
            self.device_id = 'test-device-id-for-api-testing'
            self.log(f"Could not create device model ({str(e)}), using fallback: {self.device_id}", 'WARNING')
                
    def create_test_users(self):
        """Create test users if they don't exist"""
        self.step("Creating test users...")
        
        for role, user_data in TEST_USERS.items():
            username = user_data['username']
            password = user_data['password']
            email = user_data['email']
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'roles': [role],
                    'is_active': True
                }
            )
            
            if created or not user.check_password(password):
                user.set_password(password)
                user.roles = [role]
                user.save()
                self.log(f"Created user: {username} (role: {role})")
            else:
                self.log(f"User already exists: {username} (role: {role})")
                
    def login(self, role):
        """Login as user with specified role and get token. Role is determined automatically from user's database roles."""
        user_data = TEST_USERS[role]
        username = user_data['username']
        password = user_data['password']
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Add device ID header if available
        if self.device_id:
            headers['X-Device-ID'] = self.device_id
        
        body = {
            'username': username,
            'password': password
        }
        
        # Also add device_id to body if available
        if self.device_id:
            body['device_id'] = self.device_id
        
        response = requests.post(
            f'{API_URL}/auth/login',
            json=body,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            self.tokens[role] = token
            self.log(f"Logged in as {username} ({role})")
            return token
        else:
            self.error(f"Failed to login as {username}: {response.status_code} - {response.text}")
            return None
            
    def get_headers(self, role):
        """Get authentication headers for role"""
        token = self.tokens.get(role)
        if not token:
            token = self.login(role)
        return {'Authorization': f'Bearer {token}'} if token else {}
        
    def test_step_1_create_order(self):
        """Step 1: Sales creates custom order"""
        self.step("STEP 1: Sales creates custom order")
        
        headers = self.get_headers('sales')
        if not headers:
            return False
            
        # Prepare order items
        items = []
        for product in TEST_PRODUCTS:
            items.append({
                'product_id': product['product_id'],
                'name': product['name'],
                'quantity': product['quantity'],
                'attributes': product['attributes'],
                'sku': f"{product['product_id']}-001",
                'unit_price': str(product['unit_price']),
                'line_total': str(product['quantity'] * product['unit_price']),
                'custom_requirements': product['custom_requirements'],
                'design_ready': False,
                'design_need_custom': True,
                'design_files_manifest': []
            })
        
        # Create order
        order_data = {
            'clientName': TEST_CLIENT['clientName'],
            'companyName': TEST_CLIENT['companyName'],
            'phone': TEST_CLIENT['phone'],
            'email': TEST_CLIENT['email'],
            'address': TEST_CLIENT['address'],
            'specs': TEST_CLIENT['specifications'],
            'urgency': TEST_CLIENT['urgency'],
            'items': items
        }
        
        response = requests.post(
            f'{API_URL}/orders/',
            json=order_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            # Handle different response formats
            if isinstance(data, dict) and 'data' in data:
                order = data['data']
            else:
                order = data
                
            self.order_id = order['id']
            self.log(f"Order created: {order.get('order_code', 'N/A')} (ID: {self.order_id})")
            
            # Verify order status
            if order.get('status') == 'draft' or order.get('status') == 'sent_to_sales':
                self.log(f"Order status: {order.get('status')} (expected)")
            else:
                self.log(f"Order status: {order.get('status')} (unexpected, but continuing)", 'WARNING')
                
            return True
        else:
            self.error(f"Failed to create order: {response.status_code} - {response.text}")
            return False
            
    def test_step_2_send_to_designer(self):
        """Step 2: Sales sends order to designer"""
        self.step("STEP 2: Sales sends order to designer")
        
        if not self.order_id:
            self.error("No order ID available")
            return False
            
        headers = self.get_headers('sales')
        
        response = requests.post(
            f'{API_URL}/orders/{self.order_id}/send-to-designer/',
            json={'designer': TEST_USERS['designer']['username']},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            order = data.get('data', data)
            self.log(f"Order sent to designer: {order.get('status')} / {order.get('stage')}")
            
            # Verify status
            if order.get('status') == 'sent_to_designer' and order.get('stage') == 'design':
                self.log("✓ Order status verified: sent_to_designer / design")
            else:
                self.error(f"Unexpected status: {order.get('status')} / {order.get('stage')}")
                return False
                
            return True
        else:
            self.error(f"Failed to send to designer: {response.status_code} - {response.text}")
            return False
            
    def test_step_3_designer_upload_files_and_request_approval(self):
        """Step 3: Designer uploads files and requests approval"""
        self.step("STEP 3: Designer uploads files and requests approval")
        
        if not self.order_id:
            self.error("No order ID available")
            return False
            
        headers = self.get_headers('designer')
        
        # Note: In a real test, we would upload actual files here
        # For API testing, we'll simulate with design_files_manifest
        design_files_manifest = [
            {
                'name': 'business_card_front.pdf',
                'size': 102400,
                'type': 'application/pdf',
                'url': '/uploads/test/business_card_front.pdf'
            },
            {
                'name': 'business_card_back.pdf',
                'size': 102400,
                'type': 'application/pdf',
                'url': '/uploads/test/business_card_back.pdf'
            }
        ]
        
        approval_data = {
            'designer': TEST_USERS['designer']['username'],
            'sales_person': TEST_USERS['sales']['username'],
            'design_files_manifest': design_files_manifest,
            'approval_notes': 'Design files ready for review. Please check colors and layout.'
        }
        
        response = requests.post(
            f'{API_URL}/orders/{self.order_id}/request-approval/',
            json=approval_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            approval = data.get('data', data) if isinstance(data, dict) else data
            
            # Handle different response formats
            if isinstance(approval, list) and len(approval) > 0:
                approval = approval[0]
            elif isinstance(approval, dict):
                pass
            else:
                self.log(f"Checking approval response format: {type(approval)}", 'WARNING')
                # Try to get approval ID from response
                if isinstance(data, dict):
                    approval_id = data.get('approval_id') or data.get('id')
                else:
                    approval_id = None
                if approval_id:
                    self.approval_id = approval_id
                    self.log(f"Got approval ID from response: {approval_id}")
                    return True
                else:
                    self.error(f"Unexpected approval response format: {type(approval)}")
                    return False
                
            self.approval_id = approval.get('id')
            self.log(f"Approval requested: ID {self.approval_id}, Status: {approval.get('approval_status')}")
            
            # Verify status
            if approval.get('approval_status') == 'pending':
                self.log("✓ Approval status verified: pending")
            else:
                self.error(f"Unexpected approval status: {approval.get('approval_status')}")
                return False
                
            # Check order status
            order_response = requests.get(
                f'{API_URL}/orders/{self.order_id}/',
                headers=headers
            )
            if order_response.status_code == 200:
                order_data = order_response.json()
                order = order_data.get('data', order_data) if isinstance(order_data, dict) else order_data
                if order.get('status') == 'sent_for_approval':
                    self.log("✓ Order status verified: sent_for_approval")
                else:
                    self.log(f"Order status: {order.get('status')} (may need refresh)", 'WARNING')
                    
            return True
        else:
            self.error(f"Failed to request approval: {response.status_code} - {response.text}")
            return False
            
    def test_step_4_sales_approve_design(self):
        """Step 4: Sales approves design"""
        self.step("STEP 4: Sales approves design")
        
        if not self.approval_id:
            self.error("No approval ID available")
            return False
            
        headers = self.get_headers('sales')
        
        decision_data = {
            'action': 'approve'
        }
        
        response = requests.post(
            f'{API_URL}/approvals/{self.approval_id}/decision/',
            json=decision_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            approval = data.get('data', data) if isinstance(data, dict) else data
            self.log(f"Design approved: Status: {approval.get('approval_status')}")
            
            # Verify status
            if approval.get('approval_status') == 'approved':
                self.log("✓ Approval status verified: approved")
            else:
                self.error(f"Unexpected approval status: {approval.get('approval_status')}")
                return False
                
            # Check if order status automatically updated (via signal)
            time.sleep(1)  # Give signal time to process
            order_response = requests.get(
                f'{API_URL}/orders/{self.order_id}/',
                headers=headers
            )
            if order_response.status_code == 200:
                order_data = order_response.json()
                order = order_data.get('data', order_data) if isinstance(order_data, dict) else order_data
                status = order.get('status')
                if status == 'sent_to_production':
                    self.log("✓ Order automatically transitioned to sent_to_production (via signal)")
                else:
                    self.log(f"Order status: {status} (automatic transition may need trigger)", 'WARNING')
                    
            return True
        else:
            self.error(f"Failed to approve design: {response.status_code} - {response.text}")
            return False
            
    def test_step_5_designer_send_to_production(self):
        """Step 5: Designer sends approved design to production"""
        self.step("STEP 5: Designer sends approved design to production")
        
        if not self.order_id:
            self.error("No order ID available")
            return False
            
        headers = self.get_headers('designer')
        
        # First, ensure order status is correct
        order_response = requests.get(f'{API_URL}/orders/{self.order_id}/', headers=headers)
        if order_response.status_code == 200:
            order_data = order_response.json()
            order = order_data.get('data', order_data) if isinstance(order_data, dict) else order_data
            current_status = order.get('status')
            self.log(f"Current order status before send: {current_status}")
        
        response = requests.post(
            f'{API_URL}/orders/{self.order_id}/send-to-production/',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            order = data.get('data', data) if isinstance(data, dict) else data
            self.log(f"Order sent to production: {order.get('status')} / {order.get('stage')}")
            
            # Verify status
            if order.get('status') == 'sent_to_production' and order.get('stage') == 'printing':
                self.log("✓ Order status verified: sent_to_production / printing")
            else:
                self.log(f"Order status: {order.get('status')} / {order.get('stage')} (checking if correct)", 'WARNING')
                
            return True
        else:
            self.error(f"Failed to send to production: {response.status_code} - {response.text}")
            return False
            
    def test_step_6_production_assign_machines(self):
        """Step 6: Production assigns machines and estimated time"""
        self.step("STEP 6: Production assigns machines and estimated time")
        
        if not self.order_id:
            self.error("No order ID available")
            return False
            
        headers = self.get_headers('production')
        
        # Get order to see products
        order_response = requests.get(f'{API_URL}/orders/{self.order_id}/', headers=headers)
        if order_response.status_code != 200:
            self.error("Failed to fetch order details")
            return False
            
        order_data = order_response.json()
        order = order_data.get('data', order_data) if isinstance(order_data, dict) else order_data
        items = order.get('items', [])
        
        if not items:
            self.error("No items found in order")
            return False
            
        # Create machine assignments
        assignments = []
        machines = [
            {'id': 'hp-indigo-1', 'name': 'HP Indigo Press 1'},
            {'id': 'roland-eco-1', 'name': 'Roland Eco-Solvent Printer'}
        ]
        
        for idx, item in enumerate(items):
            machine = machines[idx % len(machines)]
            estimated_time = 60 if idx == 0 else 120
            
            assignments.append({
                'product_name': item.get('name', TEST_PRODUCTS[idx]['name']),
                'product_sku': item.get('sku', f"SKU-{idx}"),
                'product_quantity': item.get('quantity', TEST_PRODUCTS[idx]['quantity']),
                'machine_id': machine['id'],
                'machine_name': machine['name'],
                'estimated_time_minutes': estimated_time,
                'assigned_by': TEST_USERS['production']['username'],
                'notes': f'Assignment for {item.get("name", "product")}'
            })
            
        response = requests.post(
            f'{API_URL}/orders/{self.order_id}/assign-machines/',
            json=assignments,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            if isinstance(data, list):
                assignments_data = data
            elif isinstance(data, dict) and 'data' in data:
                assignments_data = data['data']
            else:
                assignments_data = [data]
                
            self.assignment_ids = [a.get('id') for a in assignments_data if a.get('id')]
            self.log(f"Created {len(assignments_data)} machine assignments")
            
            for assignment in assignments_data:
                self.log(f"  - {assignment.get('product_name')} → {assignment.get('machine_name')} "
                        f"({assignment.get('estimated_time_minutes')} min)")
            
            # Verify order status
            order_response = requests.get(f'{API_URL}/orders/{self.order_id}/', headers=headers)
            if order_response.status_code == 200:
                order_data = order_response.json()
                order = order_data.get('data', order_data) if isinstance(order_data, dict) else order_data
                if order.get('status') == 'getting_ready':
                    self.log("✓ Order status verified: getting_ready")
                else:
                    self.log(f"Order status: {order.get('status')} (expected getting_ready)", 'WARNING')
                    
            return True
        else:
            self.error(f"Failed to assign machines: {response.status_code} - {response.text}")
            return False
            
    def test_step_7_mark_assignments_complete(self):
        """Step 7: Mark machine assignments as complete (triggers auto-transition)"""
        self.step("STEP 7: Mark machine assignments as complete")
        
        if not self.assignment_ids:
            self.error("No assignment IDs available")
            return False
            
        headers = self.get_headers('production')
        
        completed_count = 0
        for assignment_id in self.assignment_ids:
            response = requests.patch(
                f'{API_URL}/machine-assignments/{assignment_id}/status/',
                json={
                    'status': 'completed'
                },
                headers=headers
            )
            
            if response.status_code == 200:
                completed_count += 1
                data = response.json()
                assignment = data.get('data', data) if isinstance(data, dict) else data
                self.log(f"Assignment {assignment_id} marked complete: {assignment.get('status')}")
            else:
                self.error(f"Failed to mark assignment {assignment_id} complete: {response.status_code} - {response.text}")
                
        if completed_count != len(self.assignment_ids):
            self.error(f"Only {completed_count}/{len(self.assignment_ids)} assignments marked complete")
            return False
            
        # Wait for signal to process
        time.sleep(2)
        
        # Verify order automatically transitioned to sent_for_delivery
        order_response = requests.get(
            f'{API_URL}/orders/{self.order_id}/',
            headers=headers
        )
        
        if order_response.status_code == 200:
            order_data = order_response.json()
            order = order_data.get('data', order_data) if isinstance(order_data, dict) else order_data
            status = order.get('status')
            
            if status == 'sent_for_delivery':
                self.log("✓ Order automatically transitioned to sent_for_delivery (via signal)")
                return True
            else:
                self.error(f"Order status is {status}, expected sent_for_delivery")
                # Check if assignments are actually completed
                self.log("Checking assignment status...", 'WARNING')
                return False
        else:
            self.error(f"Failed to fetch order status: {order_response.status_code}")
            return False
            
    def test_step_8_delivery_upload_photo_and_complete(self):
        """Step 8: Delivery uploads photo and marks order delivered"""
        self.step("STEP 8: Delivery uploads photo and completes order")
        
        if not self.order_id:
            self.error("No order ID available")
            return False
            
        headers = self.get_headers('delivery')
        
        # Generate delivery code (6 random digits)
        delivery_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        response = requests.post(
            f'{API_URL}/send-delivery-code',
            json={
                'code': delivery_code,
                'phone': TEST_CLIENT['phone']
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            self.log(f"Delivery code generated: {delivery_code}")
        else:
            self.log(f"Delivery code generation returned: {response.status_code} (continuing)", 'WARNING')
            
        # Note: Photo upload would require actual file, skipping for API test
        # In real test, you would upload a photo file here
        
        # Mark order as delivered
        response = requests.patch(
            f'{API_URL}/orders/{self.order_id}/',
            json={'status': 'delivered'},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            order = data.get('data', data) if isinstance(data, dict) else data
            self.log(f"Order marked as delivered: {order.get('status')}")
            
            if order.get('status') == 'delivered':
                self.log("✓ Order status verified: delivered")
                return True
            else:
                self.error(f"Unexpected order status: {order.get('status')}")
                return False
        else:
            self.error(f"Failed to mark order as delivered: {response.status_code} - {response.text}")
            return False
            
    def run_all_tests(self):
        """Run all test steps"""
        print("\n" + "="*70)
        print("COMPLETE ORDER LIFECYCLE WORKFLOW TEST")
        print("="*70 + "\n")
        
        # Setup
        self.create_test_device()
        self.create_test_users()
        print()
        
        # Login all users
        for role in ['sales', 'designer', 'production', 'delivery']:
            self.login(role)
        print()
        
        # Run workflow tests
        steps = [
            ('Create Order', self.test_step_1_create_order),
            ('Send to Designer', self.test_step_2_send_to_designer),
            ('Designer Requests Approval', self.test_step_3_designer_upload_files_and_request_approval),
            ('Sales Approves Design', self.test_step_4_sales_approve_design),
            ('Designer Sends to Production', self.test_step_5_designer_send_to_production),
            ('Production Assigns Machines', self.test_step_6_production_assign_machines),
            ('Mark Assignments Complete', self.test_step_7_mark_assignments_complete),
            ('Delivery Completes Order', self.test_step_8_delivery_upload_photo_and_complete),
        ]
        
        results = []
        for step_name, test_func in steps:
            try:
                result = test_func()
                results.append((step_name, result))
                print()
            except Exception as e:
                self.error(f"Exception in {step_name}: {str(e)}")
                results.append((step_name, False))
                print()
                
        # Summary
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for step_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {step_name}")
            
        print()
        print(f"Total: {passed}/{total} steps passed")
        
        if self.errors:
            print(f"\nErrors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
                
        print("\n" + "="*70)
        
        return passed == total


if __name__ == '__main__':
    tester = TestOrderWorkflow()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


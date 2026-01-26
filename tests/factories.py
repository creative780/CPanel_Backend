"""
Factory Boy factories for all Django models.

This module provides factories for creating test data easily.
"""
import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from accounts.models import Role
from orders.models import Order, OrderItem, Quotation, DesignStage, PrintingStage, ApprovalStage, DeliveryStage, DesignApproval, ProductMachineAssignment
from clients.models import Organization, Contact, Lead, Client
from chat.models import Conversation, Participant, Message, Prompt
from activity_log.models import ActivityEvent, ActorRole, Verb, Source
from monitoring.models import Device, Org, Employee as MonitoringEmployee
from hr.models import HREmployee, SalarySlip
from inventory.models import InventoryItem, InventoryMovement
from attendance.models import Attendance, AttendanceRule, LeaveRequest, Holiday, AttendanceBreak
from notifications.models import Notification
from delivery.models import DeliveryCode

User = get_user_model()


# ============================================================================
# Accounts Factories
# ============================================================================

class UserFactory(factory.django.DjangoModelFactory):
    """Factory for User model."""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    roles = [Role.USER]
    is_active = True


class AdminUserFactory(UserFactory):
    """Factory for admin users."""
    username = factory.Sequence(lambda n: f'admin{n}')
    roles = [Role.ADMIN]
    is_staff = True
    is_superuser = True


class SalesUserFactory(UserFactory):
    """Factory for sales users."""
    username = factory.Sequence(lambda n: f'sales{n}')
    roles = [Role.SALES]


class DesignerUserFactory(UserFactory):
    """Factory for designer users."""
    username = factory.Sequence(lambda n: f'designer{n}')
    roles = [Role.DESIGNER]


class ProductionUserFactory(UserFactory):
    """Factory for production users."""
    username = factory.Sequence(lambda n: f'production{n}')
    roles = [Role.PRODUCTION]


class DeliveryUserFactory(UserFactory):
    """Factory for delivery users."""
    username = factory.Sequence(lambda n: f'delivery{n}')
    roles = [Role.DELIVERY]


class FinanceUserFactory(UserFactory):
    """Factory for finance users."""
    username = factory.Sequence(lambda n: f'finance{n}')
    roles = [Role.FINANCE]


# ============================================================================
# Monitoring Factories
# ============================================================================

class OrgFactory(factory.django.DjangoModelFactory):
    """Factory for Org model."""
    
    class Meta:
        model = Org
        django_get_or_create = ('id',)
    
    id = factory.Sequence(lambda n: f'org_{n}')
    name = factory.Faker('company')
    retention_days = 30


class DeviceFactory(factory.django.DjangoModelFactory):
    """Factory for Device model."""
    
    class Meta:
        model = Device
        django_get_or_create = ('id',)
    
    id = factory.Sequence(lambda n: f'device-{n}')
    org = factory.SubFactory(OrgFactory)
    hostname = factory.Faker('hostname')
    os = fuzzy.FuzzyChoice(['Windows', 'Linux', 'macOS'])
    status = fuzzy.FuzzyChoice(['ONLINE', 'OFFLINE', 'IDLE'])
    last_heartbeat = factory.LazyFunction(timezone.now)


class MonitoringEmployeeFactory(factory.django.DjangoModelFactory):
    """Factory for Monitoring Employee model."""
    
    class Meta:
        model = MonitoringEmployee
    
    email = factory.Faker('email')
    name = factory.Faker('name')
    department = fuzzy.FuzzyChoice(['Sales', 'Design', 'Production', 'Delivery'])
    status = fuzzy.FuzzyChoice(['active', 'inactive'])


# ============================================================================
# Orders Factories
# ============================================================================

class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for Order model."""
    
    class Meta:
        model = Order
    
    order_code = factory.Sequence(lambda n: f'ORD-{n:06d}')
    client_name = factory.Faker('name')
    company_name = factory.Faker('company')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    address = factory.Faker('address')
    specs = factory.Faker('text', max_nb_chars=200)
    urgency = fuzzy.FuzzyChoice(['Urgent', 'High', 'Normal', 'Low'])
    status = 'draft'
    stage = 'order_intake'
    pricing_status = 'Not Priced'
    created_by = factory.SubFactory(UserFactory)
    channel = fuzzy.FuzzyChoice(['b2b_customers', 'b2c_customers', 'walk_in_orders', 'online_store', 'salesperson_generated'])


class OrderItemFactory(factory.django.DjangoModelFactory):
    """Factory for OrderItem model."""
    
    class Meta:
        model = OrderItem
    
    order = factory.SubFactory(OrderFactory)
    product_id = factory.Sequence(lambda n: f'prod_{n}')
    name = factory.Faker('word')
    sku = factory.Sequence(lambda n: f'SKU-{n}')
    attributes = factory.LazyFunction(dict)
    quantity = fuzzy.FuzzyInteger(1, 100)
    unit_price = fuzzy.FuzzyDecimal(10.00, 1000.00, precision=2)
    custom_requirements = factory.Faker('text', max_nb_chars=100)
    design_ready = False
    design_need_custom = False


class QuotationFactory(factory.django.DjangoModelFactory):
    """Factory for Quotation model."""
    
    class Meta:
        model = Quotation
    
    order = factory.SubFactory(OrderFactory)
    labour_cost = fuzzy.FuzzyDecimal(0, 500, precision=2)
    finishing_cost = fuzzy.FuzzyDecimal(0, 300, precision=2)
    paper_cost = fuzzy.FuzzyDecimal(0, 1000, precision=2)
    machine_cost = fuzzy.FuzzyDecimal(0, 800, precision=2)
    design_cost = fuzzy.FuzzyDecimal(0, 500, precision=2)
    delivery_cost = fuzzy.FuzzyDecimal(0, 200, precision=2)
    other_charges = fuzzy.FuzzyDecimal(0, 100, precision=2)
    discount = fuzzy.FuzzyDecimal(0, 100, precision=2)
    advance_paid = fuzzy.FuzzyDecimal(0, 500, precision=2)
    quotation_notes = factory.Faker('text', max_nb_chars=200)
    sales_person = factory.Faker('name')


class DesignStageFactory(factory.django.DjangoModelFactory):
    """Factory for DesignStage model."""
    
    class Meta:
        model = DesignStage
    
    order = factory.SubFactory(OrderFactory)
    assigned_designer = factory.Faker('name')
    requirements_files_manifest = factory.LazyFunction(list)
    design_status = fuzzy.FuzzyChoice(['pending', 'in_progress', 'completed', 'needs_revision'])


class PrintingStageFactory(factory.django.DjangoModelFactory):
    """Factory for PrintingStage model."""
    
    class Meta:
        model = PrintingStage
    
    order = factory.SubFactory(OrderFactory)
    print_operator = factory.Faker('name')
    print_time = factory.LazyFunction(timezone.now)
    batch_info = factory.Faker('word')
    print_status = fuzzy.FuzzyChoice(['Pending', 'Printing', 'Printed'])
    qa_checklist = factory.Faker('text', max_nb_chars=200)


class ApprovalStageFactory(factory.django.DjangoModelFactory):
    """Factory for ApprovalStage model."""
    
    class Meta:
        model = ApprovalStage
    
    order = factory.SubFactory(OrderFactory)
    client_approval_files = factory.LazyFunction(list)
    approved_at = factory.LazyFunction(timezone.now)


class DeliveryStageFactory(factory.django.DjangoModelFactory):
    """Factory for DeliveryStage model."""
    
    class Meta:
        model = DeliveryStage
    
    order = factory.SubFactory(OrderFactory)
    rider_photo_path = factory.Faker('file_path')
    delivered_at = factory.LazyFunction(timezone.now)


class DesignApprovalFactory(factory.django.DjangoModelFactory):
    """Factory for DesignApproval model."""
    
    class Meta:
        model = DesignApproval
    
    order = factory.SubFactory(OrderFactory)
    designer = factory.Faker('name')
    sales_person = factory.Faker('name')
    approval_status = fuzzy.FuzzyChoice(['pending', 'approved', 'rejected'])
    design_files_manifest = factory.LazyFunction(list)
    approval_notes = factory.Faker('text', max_nb_chars=200)
    rejection_reason = factory.Faker('text', max_nb_chars=200)


class ProductMachineAssignmentFactory(factory.django.DjangoModelFactory):
    """Factory for ProductMachineAssignment model."""
    
    class Meta:
        model = ProductMachineAssignment
    
    order = factory.SubFactory(OrderFactory)
    product_name = factory.Faker('word')
    product_sku = factory.Sequence(lambda n: f'SKU-{n}')
    product_quantity = fuzzy.FuzzyInteger(1, 100)
    machine_id = factory.Sequence(lambda n: f'machine-{n}')
    machine_name = factory.Faker('word')
    estimated_time_minutes = fuzzy.FuzzyInteger(30, 480)
    status = fuzzy.FuzzyChoice(['queued', 'in_progress', 'completed', 'on_hold'])
    assigned_by = factory.Faker('name')
    notes = factory.Faker('text', max_nb_chars=100)


# ============================================================================
# Clients Factories
# ============================================================================

class OrganizationFactory(factory.django.DjangoModelFactory):
    """Factory for Organization model."""
    
    class Meta:
        model = Organization
    
    name = factory.Faker('company')
    industry = factory.Faker('word')
    website = factory.Faker('url')
    notes = factory.Faker('text', max_nb_chars=200)


class ContactFactory(factory.django.DjangoModelFactory):
    """Factory for Contact model."""
    
    class Meta:
        model = Contact
    
    org = factory.SubFactory(OrganizationFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    title = factory.Faker('job')


class LeadFactory(factory.django.DjangoModelFactory):
    """Factory for Lead model."""
    
    class Meta:
        model = Lead
    
    org = factory.SubFactory(OrganizationFactory)
    contact = factory.SubFactory(ContactFactory)
    title = factory.Faker('sentence', nb_words=4)
    source = fuzzy.FuzzyChoice(['website', 'referral', 'cold_call', 'email'])
    stage = fuzzy.FuzzyChoice(['new', 'contacted', 'proposal', 'negotiation', 'won', 'lost'])
    owner = factory.SubFactory(UserFactory)
    value = fuzzy.FuzzyDecimal(1000, 100000, precision=2)
    probability = fuzzy.FuzzyInteger(0, 100)
    notes = factory.Faker('text', max_nb_chars=300)
    created_by = factory.SubFactory(UserFactory)


class ClientFactory(factory.django.DjangoModelFactory):
    """Factory for Client model."""
    
    class Meta:
        model = Client
    
    org = factory.SubFactory(OrganizationFactory)
    primary_contact = factory.SubFactory(ContactFactory)
    account_owner = factory.SubFactory(UserFactory)
    status = fuzzy.FuzzyChoice(['active', 'inactive', 'prospect'])


# ============================================================================
# Chat Factories
# ============================================================================

class ConversationFactory(factory.django.DjangoModelFactory):
    """Factory for Conversation model."""
    
    class Meta:
        model = Conversation
    
    created_by = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=3)
    is_archived = False


class ParticipantFactory(factory.django.DjangoModelFactory):
    """Factory for Participant model."""
    
    class Meta:
        model = Participant
    
    conversation = factory.SubFactory(ConversationFactory)
    user = factory.SubFactory(UserFactory)
    role = fuzzy.FuzzyChoice(['owner', 'member', 'agent'])


class MessageFactory(factory.django.DjangoModelFactory):
    """Factory for Message model."""
    
    class Meta:
        model = Message
    
    conversation = factory.SubFactory(ConversationFactory)
    sender = factory.SubFactory(UserFactory)
    type = fuzzy.FuzzyChoice(['user', 'bot', 'system'])
    text = factory.Faker('text', max_nb_chars=200)
    status = fuzzy.FuzzyChoice(['sent', 'delivered', 'read'])


class PromptFactory(factory.django.DjangoModelFactory):
    """Factory for Prompt model."""
    
    class Meta:
        model = Prompt
    
    title = factory.Faker('sentence', nb_words=3)
    text = factory.Faker('text', max_nb_chars=100)
    is_active = True
    order = factory.Sequence(lambda n: n)


# ============================================================================
# Activity Log Factories
# ============================================================================

class ActivityEventFactory(factory.django.DjangoModelFactory):
    """Factory for ActivityEvent model."""
    
    class Meta:
        model = ActivityEvent
    
    timestamp = factory.LazyFunction(timezone.now)
    actor = factory.SubFactory(UserFactory)
    actor_role = fuzzy.FuzzyChoice([choice[0] for choice in ActorRole.choices])
    verb = fuzzy.FuzzyChoice([choice[0] for choice in Verb.choices])
    target_type = factory.Faker('word')
    target_id = factory.Sequence(lambda n: str(n))
    context = factory.LazyFunction(dict)
    source = fuzzy.FuzzyChoice([choice[0] for choice in Source.choices])
    request_id = factory.Sequence(lambda n: f'req_{n}')
    tenant_id = factory.Sequence(lambda n: f'tenant_{n}')
    hash = factory.Sequence(lambda n: f'{n:064x}')
    prev_hash = factory.LazyAttribute(lambda obj: None)
    is_reviewed = False


# ============================================================================
# HR Factories
# ============================================================================

class HREmployeeFactory(factory.django.DjangoModelFactory):
    """Factory for HREmployee model."""
    
    class Meta:
        model = HREmployee
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    department = fuzzy.FuzzyChoice(['Sales', 'Design', 'Production', 'Delivery', 'Admin'])
    position = factory.Faker('job')
    salary = fuzzy.FuzzyDecimal(2000, 10000, precision=2)
    hire_date = factory.Faker('date_object')
    status = fuzzy.FuzzyChoice(['active', 'inactive', 'terminated'])


class SalarySlipFactory(factory.django.DjangoModelFactory):
    """Factory for SalarySlip model."""
    
    class Meta:
        model = SalarySlip
    
    employee = factory.SubFactory(HREmployeeFactory)
    month = fuzzy.FuzzyInteger(1, 12)
    year = fuzzy.FuzzyInteger(2020, 2025)
    basic_salary = fuzzy.FuzzyDecimal(2000, 10000, precision=2)
    allowances = factory.LazyFunction(dict)
    deductions = factory.LazyFunction(dict)
    net_salary = fuzzy.FuzzyDecimal(2000, 10000, precision=2)


# ============================================================================
# Inventory Factories
# ============================================================================

class InventoryItemFactory(factory.django.DjangoModelFactory):
    """Factory for InventoryItem model."""
    
    class Meta:
        model = InventoryItem
        django_get_or_create = ('sku',)
    
    sku = factory.Sequence(lambda n: f'SKU-{n}')
    name = factory.Faker('word')
    quantity = fuzzy.FuzzyInteger(0, 1000)
    unit = fuzzy.FuzzyChoice(['unit', 'pcs', 'kg', 'l', 'm'])


class InventoryMovementFactory(factory.django.DjangoModelFactory):
    """Factory for InventoryMovement model."""
    
    class Meta:
        model = InventoryMovement
    
    order_id = factory.SubFactory(OrderFactory)
    sku = factory.Sequence(lambda n: f'SKU-{n}')
    delta = fuzzy.FuzzyInteger(-100, 100)
    reason = factory.Faker('word')


# ============================================================================
# Attendance Factories
# ============================================================================

class AttendanceRuleFactory(factory.django.DjangoModelFactory):
    """Factory for AttendanceRule model."""
    
    class Meta:
        model = AttendanceRule
    
    work_start = factory.LazyFunction(lambda: timezone.now().replace(hour=9, minute=0, second=0, microsecond=0).time())
    work_end = factory.LazyFunction(lambda: timezone.now().replace(hour=17, minute=30, second=0, microsecond=0).time())
    grace_minutes = 5
    standard_work_minutes = 510
    overtime_after_minutes = 510
    late_penalty_per_minute = fuzzy.FuzzyDecimal(0, 1, precision=2)
    per_day_deduction = fuzzy.FuzzyDecimal(0, 50, precision=2)
    overtime_rate_per_minute = fuzzy.FuzzyDecimal(0, 2, precision=2)
    weekend_days = [5, 6]
    grace_violation_deduction = fuzzy.FuzzyDecimal(0, 20, precision=2)
    early_checkout_threshold_minutes = 20
    early_checkout_deduction = fuzzy.FuzzyDecimal(0, 20, precision=2)


class AttendanceFactory(factory.django.DjangoModelFactory):
    """Factory for Attendance model."""
    
    class Meta:
        model = Attendance
    
    employee = factory.SubFactory(UserFactory)
    check_in = factory.LazyFunction(timezone.now)
    check_out = factory.LazyAttribute(lambda obj: obj.check_in + timezone.timedelta(hours=8) if obj.check_in else None)
    date = factory.LazyAttribute(lambda obj: timezone.localdate(obj.check_in) if obj.check_in else timezone.localdate())
    status = fuzzy.FuzzyChoice(['present', 'late', 'absent'])
    device_id = factory.Sequence(lambda n: f'device-{n}')
    overtime_verified = False


class LeaveRequestFactory(factory.django.DjangoModelFactory):
    """Factory for LeaveRequest model."""
    
    class Meta:
        model = LeaveRequest
    
    employee = factory.SubFactory(UserFactory)
    leave_type = fuzzy.FuzzyChoice(['full_day', 'partial_day', 'multiple_days'])
    start_date = factory.Faker('date_object')
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + timezone.timedelta(days=1) if obj.leave_type == 'multiple_days' else None)
    start_time = factory.LazyAttribute(lambda obj: timezone.now().time() if obj.leave_type == 'partial_day' else None)
    end_time = factory.LazyAttribute(lambda obj: (timezone.now() + timezone.timedelta(hours=4)).time() if obj.leave_type == 'partial_day' else None)
    hours = factory.LazyAttribute(lambda obj: fuzzy.FuzzyDecimal(1, 8, precision=2).fuzz() if obj.leave_type == 'partial_day' else None)
    reason = factory.Faker('text', max_nb_chars=200)
    status = fuzzy.FuzzyChoice(['pending', 'approved', 'rejected'])
    is_paid = False
    approved_by = factory.LazyAttribute(lambda obj: factory.SubFactory(UserFactory) if obj.status == 'approved' else None)
    approved_at = factory.LazyAttribute(lambda obj: timezone.now() if obj.status == 'approved' else None)


# ============================================================================
# Notifications Factories
# ============================================================================

class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for Notification model."""
    
    class Meta:
        model = Notification
    
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=3)
    message = factory.Faker('text', max_nb_chars=200)
    type = fuzzy.FuzzyChoice([
        'order_created', 'order_assigned', 'design_submitted',
        'design_approved', 'design_rejected', 'leave_requested',
        'leave_approved', 'leave_rejected', 'delivery_photo_uploaded',
        'delivery_status_updated', 'delivery_code_sent',
        'monitoring_device_idle', 'monitoring_pollution_threshold',
        'monitoring_sensor_offline'
    ])
    is_read = False
    actor = None
    tag_trigger = factory.Faker('word')
    related_object_type = None
    related_object_id = None
    metadata = factory.LazyFunction(dict)


# ============================================================================
# Delivery Factories
# ============================================================================

class DeliveryCodeFactory(factory.django.DjangoModelFactory):
    """Factory for DeliveryCode model."""
    
    class Meta:
        model = DeliveryCode
    
    code = factory.Sequence(lambda n: f'DEL{n:04d}')
    order = factory.SubFactory(OrderFactory)
    expires_at = factory.LazyAttribute(lambda obj: timezone.now() + timezone.timedelta(days=1))


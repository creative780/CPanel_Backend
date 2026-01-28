"""
Script to create test leads for dashboard testing
Run with: python manage.py shell < create_test_leads.py
Or: python manage.py shell, then paste this code
"""
from clients.models import Lead, Organization, Contact
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

# Get or create a test organization
org, _ = Organization.objects.get_or_create(
    name="Test Company",
    defaults={'industry': 'Technology', 'website': 'https://test.com'}
)

# Get or create a test contact
contact, _ = Contact.objects.get_or_create(
    org=org,
    first_name="Test",
    last_name="Contact",
    defaults={'email': 'test@example.com', 'phone': '+1234567890'}
)

# Get admin user (or first user)
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.first()

if not admin_user:
    print("ERROR: No users found. Please create a user first.")
    exit(1)

# Define test leads data
test_leads = [
    # Google Ads leads
    {'source': 'Google Ads', 'stage': 'new', 'value': 10000, 'probability': 30},
    {'source': 'Google Ads', 'stage': 'contacted', 'value': 15000, 'probability': 50},
    {'source': 'Google Ads', 'stage': 'proposal', 'value': 20000, 'probability': 70},
    {'source': 'Google Ads', 'stage': 'negotiation', 'value': 25000, 'probability': 85},
    {'source': 'Google Ads', 'stage': 'won', 'value': 30000, 'probability': 100},
    {'source': 'Google Ads', 'stage': 'won', 'value': 35000, 'probability': 100},
    
    # Organic leads
    {'source': 'Organic', 'stage': 'new', 'value': 8000, 'probability': 25},
    {'source': 'Organic', 'stage': 'contacted', 'value': 12000, 'probability': 45},
    {'source': 'Organic', 'stage': 'proposal', 'value': 18000, 'probability': 65},
    {'source': 'Organic', 'stage': 'won', 'value': 22000, 'probability': 100},
    
    # Referrals
    {'source': 'Referrals', 'stage': 'new', 'value': 5000, 'probability': 40},
    {'source': 'Referrals', 'stage': 'contacted', 'value': 10000, 'probability': 60},
    {'source': 'Referrals', 'stage': 'proposal', 'value': 15000, 'probability': 75},
    {'source': 'Referrals', 'stage': 'won', 'value': 20000, 'probability': 100},
    
    # Social
    {'source': 'Social', 'stage': 'new', 'value': 3000, 'probability': 20},
    {'source': 'Social', 'stage': 'contacted', 'value': 6000, 'probability': 40},
    {'source': 'Social', 'stage': 'proposal', 'value': 9000, 'probability': 60},
    
    # Email
    {'source': 'Email', 'stage': 'new', 'value': 2000, 'probability': 15},
    {'source': 'Email', 'stage': 'contacted', 'value': 4000, 'probability': 35},
    {'source': 'Email', 'stage': 'won', 'value': 8000, 'probability': 100},
]

# Create leads
created_count = 0
for lead_data in test_leads:
    lead, created = Lead.objects.get_or_create(
        org=org,
        contact=contact,
        source=lead_data['source'],
        stage=lead_data['stage'],
        defaults={
            'title': f"{lead_data['source']} - {lead_data['stage']} Lead",
            'value': Decimal(str(lead_data['value'])),
            'probability': lead_data['probability'],
            'owner': admin_user,
            'created_by': admin_user,
            'notes': f"Test lead for dashboard testing"
        }
    )
    if created:
        created_count += 1
        print(f"✓ Created: {lead.title}")
    else:
        print(f"⚠ Already exists: {lead.title}")

print(f"\n{'='*60}")
print(f"Created {created_count} new test leads")
print(f"Total leads in database: {Lead.objects.count()}")
print(f"{'='*60}")

# Print summary by source
print("\nSummary by Source:")
for source in ['Google Ads', 'Organic', 'Referrals', 'Social', 'Email']:
    count = Lead.objects.filter(source=source).count()
    print(f"  {source}: {count} leads")

# Print summary by stage
print("\nSummary by Stage:")
for stage in ['new', 'contacted', 'proposal', 'negotiation', 'won']:
    count = Lead.objects.filter(stage=stage).count()
    print(f"  {stage}: {count} leads")

























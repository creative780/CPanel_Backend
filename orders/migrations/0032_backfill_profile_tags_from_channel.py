# Generated manually for profile tagging system - Data migration

from django.db import migrations


def backfill_profile_tags_from_channel(apps, schema_editor):
    """
    Backfill profile tags from existing channel data and attempt to link orders to clients.
    This is a best-effort migration that:
    1. Maps channel values to profile tags
    2. Attempts to match orders to existing clients by name/phone/company
    3. Creates clients with profile tags if no match is found
    """
    Order = apps.get_model('orders', 'Order')
    Client = apps.get_model('clients', 'Client')
    Organization = apps.get_model('clients', 'Organization')
    Contact = apps.get_model('clients', 'Contact')
    
    # Channel to profile tag mapping
    channel_to_tag = {
        'b2b_customers': 'b2b',
        'b2c_customers': 'b2c',
        'walk_in_orders': 'walk_in',
        'online_store': 'online',
        'salesperson_generated': None,  # No direct mapping
    }
    
    orders_updated = 0
    clients_created = 0
    
    for order in Order.objects.filter(client__isnull=True).iterator():
        # Determine profile tag from channel
        profile_tag = channel_to_tag.get(order.channel)
        
        if not profile_tag:
            # Skip orders without a mappable channel
            continue
        
        # Try to find existing client
        client = None
        
        # Try by phone through contact
        if order.phone:
            contacts = Contact.objects.filter(phone=order.phone).select_related('org')
            if contacts.exists():
                org = contacts.first().org
                client = Client.objects.filter(org=org).first()
        
        # Try by organization name
        if not client and order.company_name:
            orgs = Organization.objects.filter(name__icontains=order.company_name)
            if orgs.exists():
                client = Client.objects.filter(org=orgs.first()).first()
        
        # Try by client name as organization name
        if not client and order.client_name:
            orgs = Organization.objects.filter(name__icontains=order.client_name)
            if orgs.exists():
                client = Client.objects.filter(org=orgs.first()).first()
        
        # Create client if not found
        if not client:
            org_name = order.company_name if order.company_name else order.client_name
            if not org_name:
                org_name = f"Client {order.client_name}" if order.client_name else "Unknown Client"
            
            org, _ = Organization.objects.get_or_create(
                name=org_name,
                defaults={'notes': f'Auto-created from order {order.order_code}'}
            )
            
            contact = None
            if order.phone or order.email:
                contact, _ = Contact.objects.get_or_create(
                    org=org,
                    phone=order.phone or '',
                    defaults={
                        'first_name': order.client_name.split()[0] if order.client_name else '',
                        'last_name': ' '.join(order.client_name.split()[1:]) if len(order.client_name.split()) > 1 else '',
                        'email': order.email or '',
                    }
                )
            
            client = Client.objects.create(
                org=org,
                primary_contact=contact,
                account_owner=order.created_by,
                profile_tag=profile_tag
            )
            clients_created += 1
        else:
            # Update existing client's profile tag if not set
            if not client.profile_tag:
                client.profile_tag = profile_tag
                client.save(update_fields=['profile_tag'])
        
        # Link order to client
        order.client = client
        order.save(update_fields=['client'])
        orders_updated += 1
    
    print(f"Migration completed: {orders_updated} orders linked, {clients_created} clients created")


def reverse_migration(apps, schema_editor):
    """Reverse migration - unlink orders from clients"""
    Order = apps.get_model('orders', 'Order')
    Order.objects.update(client=None)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0031_add_client_foreignkey'),
        ('clients', '0002_add_profile_tag_field'),
    ]

    operations = [
        migrations.RunPython(backfill_profile_tags_from_channel, reverse_migration),
    ]


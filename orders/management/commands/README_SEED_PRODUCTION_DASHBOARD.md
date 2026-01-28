# Production Dashboard Seed Script

## Usage

To seed the database with comprehensive test data for production dashboard metrics:

```bash
cd CRM_BACKEND
# Activate your virtual environment first
python manage.py seed_production_dashboard_data
```

To clear existing test data before seeding:

```bash
python manage.py seed_production_dashboard_data --clear
```

## What It Creates

The script creates test data for all 8 production dashboard metrics:

1. **WIP Orders** (5-8 orders)
   - Orders with `status='sent_to_production'` or `status='getting_ready'`
   - Mix of orders created today and yesterday

2. **Completed Orders** (10-15 orders)
   - Orders with `delivered_at` in last 7 days
   - Varying turnaround times (1-5 days)

3. **Machine Assignments** (10+ assignments)
   - Assignments for different machines (HP Latex, Mimaki, Epson, etc.)
   - Mix of statuses: `queued`, `in_progress`, `completed`
   - Varying start times and estimated durations

4. **Reprint Orders** (5 orders)
   - 3 reprints this week
   - 2 reprints last week
   - Linked to original orders

5. **Inventory Movements** (20 movements)
   - Consumption records for materials (Vinyl, Fabric, Paper, Ink, Lamination)
   - Created within last 7 days

6. **Delivery Ready Orders** (5 orders)
   - Orders with `status='sent_for_delivery'`
   - Some with delivery codes

## Test Data Prefixes

All test data uses prefixes:
- Orders: `TEST-WIP-`, `TEST-READY-`, `TEST-DEL-`, `TEST-REPRINT-`, etc.
- Inventory movements: Reason contains "test"

## After Seeding

After running the seed script, you can:
1. Test all production dashboard endpoints
2. Verify calculations match expected values
3. Use browser to test UI with real data
4. Test user workflows end-to-end




























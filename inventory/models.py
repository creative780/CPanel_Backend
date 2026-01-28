from django.db import models


class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('raw_materials', 'Raw Materials'),
        ('finished_goods', 'Finished Goods'),
        ('supplies', 'Supplies'),
        ('consumables', 'Consumables'),
        ('equipment', 'Equipment'),
    ]
    
    WAREHOUSE_CHOICES = [
        ('main', 'Main Warehouse'),
        ('secondary', 'Secondary'),
        ('offsite', 'Offsite'),
    ]
    
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='raw_materials')
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=32, default='pcs')
    
    # Stock fields
    quantity = models.IntegerField(default=0, help_text='Current stock quantity')
    reserved = models.IntegerField(default=0, help_text='Reserved quantity (not available)')
    minimum_stock = models.IntegerField(default=0, help_text='Minimum stock level (reorder point)')
    reorder_quantity = models.IntegerField(default=0, help_text='Quantity to reorder when below minimum')
    lead_time_days = models.IntegerField(default=7, help_text='Lead time in days for restocking')
    
    # Pricing fields
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Cost price per unit in AED')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Selling price per unit in AED')
    
    # Location fields
    warehouse = models.CharField(max_length=50, choices=WAREHOUSE_CHOICES, default='main')
    location = models.CharField(max_length=100, blank=True, null=True, help_text='Location/Bin (e.g., A1-R2-S3)')
    supplier_id = models.CharField(max_length=100, blank=True, null=True, help_text='Preferred supplier ID or name')
    
    # Additional fields
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['sku']
        indexes = [
            models.Index(fields=['sku'], name='inventory_item_sku_idx'),
            models.Index(fields=['category'], name='inventory_item_category_idx'),
            models.Index(fields=['warehouse'], name='inventory_item_warehouse_idx'),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    @property
    def available_stock(self):
        """Calculate available stock (quantity - reserved)"""
        return max(0, self.quantity - self.reserved)
    
    @property
    def total_value(self):
        """Calculate total inventory value (cost_price * quantity)"""
        return float(self.cost_price) * self.quantity


class InventoryMovement(models.Model):
    order_id = models.IntegerField(null=True, blank=True)
    sku = models.CharField(max_length=64)
    delta = models.IntegerField()
    reason = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)


class Machine(models.Model):
    TYPE_CHOICES = [
        ('digital_printer', 'Digital Printer'),
        ('offset_printer', 'Offset Printer'),
        ('uv_printer', 'UV Printer'),
        ('dtf_printer', 'DTF Printer'),
        ('screen_printer', 'Screen Printer'),
        ('laser_cutter', 'Laser Cutter'),
        ('laminator', 'Laminator'),
        ('creasing_machine', 'Creasing Machine'),
        ('binding_machine', 'Binding Machine'),
        ('embroidery_machine', 'Embroidery Machine'),
        ('heat_press', 'Heat Press'),
    ]
    
    LOCATION_CHOICES = [
        ('dubai', 'Dubai'),
        ('pakistan', 'Pakistan'),
    ]
    
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Needs Repair'),
        ('offline', 'Offline'),
    ]
    
    machine_code = models.CharField(max_length=50, unique=True, help_text='Auto-generated machine code')
    name = models.CharField(max_length=255, help_text='Machine name (e.g., Epson SureColor S60600)')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, help_text='Machine type')
    brand = models.CharField(max_length=100, blank=True, null=True, help_text='Brand name (e.g., Epson)')
    model = models.CharField(max_length=100, blank=True, null=True, help_text='Model number (e.g., S60600)')
    serial_number = models.CharField(max_length=100, blank=True, null=True, help_text='Serial number')
    purchase_date = models.DateField(blank=True, null=True, help_text='Purchase date')
    warranty_expiry = models.DateField(blank=True, null=True, help_text='Warranty expiry date')
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='dubai', help_text='Machine location')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='operational', help_text='Current status')
    running_hours = models.FloatField(default=0.0, help_text='Current running hours')
    service_interval_hours = models.IntegerField(default=500, help_text='Service interval in hours')
    next_service_due = models.DateField(blank=True, null=True, help_text='Next service due date')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        ordering = ['machine_code']
        indexes = [
            models.Index(fields=['machine_code'], name='machine_code_idx'),
            models.Index(fields=['type'], name='machine_type_idx'),
            models.Index(fields=['location'], name='machine_location_idx'),
            models.Index(fields=['status'], name='machine_status_idx'),
        ]
    
    def __str__(self):
        return f"{self.machine_code} - {self.name}"

# Create your models here.

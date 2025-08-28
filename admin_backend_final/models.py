from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # for AUTH_USER_MODEL-safe FKs
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

# === USER AND ADMIN ===
class User(AbstractUser):
    user_id = models.CharField(primary_key=True, max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username or self.email or self.user_id

class Admin(models.Model):
    admin_id = models.CharField(primary_key=True, max_length=100)
    admin_name = models.CharField(max_length=100, db_index=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin_name

class AdminRole(models.Model):
    role_id = models.CharField(primary_key=True, max_length=100)
    role_name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    access_pages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name

class AdminRoleMap(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    role = models.ForeignKey(AdminRole, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["admin"]),
            models.Index(fields=["role"]),
        ]

class Image(models.Model):
    image_id = models.CharField(primary_key=True, max_length=100)
    image_file = models.ImageField(upload_to='uploads/', null=True, blank=True)
    alt_text = models.CharField(max_length=255, blank=True, default="")
    width = models.IntegerField()
    height = models.IntegerField()
    tags = models.JSONField(default=list)
    image_type = models.CharField(max_length=50, blank=True, default="")
    linked_table = models.CharField(max_length=100, blank=True, default="")
    linked_id = models.CharField(max_length=100, blank=True, default="", db_index=True)
    linked_page = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        try:
            return self.image_file.url
        except ValueError:
            return None

    def __str__(self):
        return self.image_id
    

class Category(models.Model):
    category_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, choices=[("hidden", "Hidden"), ("visible", "Visible")], db_index=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class CategoryImage(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class SubCategory(models.Model):
    subcategory_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, choices=[("hidden", "Hidden"), ("visible", "Visible")], db_index=True)
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class SubCategoryImage(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CategorySubCategoryMap(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["subcategory"]),
        ]
        unique_together = ("category", "subcategory")

# === PRODUCT SYSTEM ===
class Product(models.Model):
    product_id = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    brand = models.CharField(max_length=255, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.FloatField()
    price_calculator = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, db_index=True)
    created_by = models.CharField(max_length=100)
    created_by_type = models.CharField(
        max_length=10, choices=[('admin', 'Admin'), ('user', 'User')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)

    # New rating system
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Allowed values: 0, 0.5, 1, ... , 5"
    )
    rating_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def set_rating(self, new_rating):
        allowed_values = [x * 0.5 for x in range(11)] 
        if new_rating not in allowed_values:
            raise ValueError
        self.rating = new_rating
        self.save()

class ProductInventory(models.Model):
    inventory_id = models.CharField(primary_key=True, max_length=100)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField()
    low_stock_alert = models.IntegerField()
    stock_status = models.CharField(max_length=50, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductVariant(models.Model):
    variant_id = models.CharField(primary_key=True, max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, blank=True, default="")
    color = models.CharField(max_length=50, blank=True, default="")
    material_type = models.CharField(max_length=50, blank=True, default="")
    fabric_finish = models.CharField(max_length=50, blank=True, default="")
    printing_methods = models.JSONField(default=list)
    add_on_options = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

class VariantCombination(models.Model):
    combo_id = models.CharField(primary_key=True, max_length=100)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    description = models.TextField()
    price_override = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class ShippingInfo(models.Model):
    shipping_id = models.CharField(primary_key=True, max_length=100)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    shipping_class = models.CharField(max_length=100)
    processing_time = models.CharField(max_length=100)
    entered_by_id = models.CharField(max_length=100)
    entered_by_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductSEO(models.Model):
    seo_id = models.CharField(primary_key=True, max_length=100)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    image_alt_text = models.CharField(max_length=255, blank=True, default="")
    meta_title = models.CharField(max_length=255, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    meta_keywords = models.JSONField(null=False, blank=True, default=list)
    open_graph_title = models.CharField(max_length=255, blank=True, default="")
    open_graph_desc = models.TextField(blank=True, default="")
    open_graph_image_url = models.URLField(blank=True, default="")
    canonical_url = models.URLField(blank=True, default="")
    json_ld = models.TextField(blank=True, default="")
    slug = models.SlugField(unique=True, db_index=True)
    custom_tags = models.JSONField(null=False, blank=True, default=list)
    grouped_filters = models.JSONField(null=False, blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductSubCategoryMap(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["subcategory"]),
        ]
        unique_together = ("product", "subcategory")

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)
    
class Attribute(models.Model):
    attr_id = models.CharField(primary_key=True, max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attributes", db_index=True)
    # self-referencing for options
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="options",
        db_index=True,
    )
    # attribute-level field
    name = models.CharField(max_length=255, blank=True, default="")   # used only when parent is NULL
    # option-level fields
    label = models.CharField(max_length=255, blank=True, default="")  # used only when parent is not NULL
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True, related_name="attribute_images")
    price_delta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    # housekeeping
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=["product", "parent", "order"]),
        ]
        ordering = ["order", "name", "label"]
    def is_attribute(self):
        return self.parent_id is None
    def is_option(self):
        return self.parent_id is not None
    def __str__(self):
        if self.is_attribute():
            return f"[Attribute] {self.name} :: {self.product.title}"
        return f"[Option] {self.label} -> {self.parent.name}"
    
class Orders(models.Model):
    order_id = models.CharField(primary_key=True, max_length=100)
    user_name = models.CharField(max_length=255, blank=True)
    order_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ], db_index=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    item_id = models.CharField(primary_key=True, max_length=100)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    selected_size = models.CharField(max_length=50, blank=True, null=True)
    selected_attributes = models.JSONField(default=dict, blank=True)
    selected_attributes_human = models.JSONField(default=list, blank=True)
    variant_signature = models.CharField(max_length=255, blank=True, null=True)
    attributes_price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_breakdown = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderDelivery(models.Model):
    delivery_id = models.CharField(primary_key=True, max_length=100)
    order = models.OneToOneField(Orders, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)  # ← allow missing/NA
    phone = models.CharField(max_length=20)
    street_address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    zip_code = models.CharField(max_length=20, db_index=True)
    instructions = models.JSONField(default=list, blank=True)  # ← always list
    created_at = models.DateTimeField(auto_now_add=True)
    
class Cart(models.Model):
    cart_id = models.CharField(primary_key=True, max_length=100)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    device_uuid = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    item_id = models.CharField(primary_key=True, max_length=100)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    selected_size = models.CharField(max_length=50, blank=True, null=True)
    selected_attributes = models.JSONField(default=dict, blank=True)
    variant_signature = models.CharField(max_length=255, blank=True, default="", db_index=True)
    attributes_price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    
class Blog(models.Model):
    blog_id = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    blog_image = models.URLField()
    schedule_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[("draft", "Draft"), ("published", "Published")], db_index=True)
    author_id = models.CharField(max_length=100)
    author_type = models.CharField(max_length=10, choices=[("admin", "Admin"), ("user", "User")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BlogCategory(models.Model):
    category_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BlogCategoryMap(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("blog", "category")

class BlogSEO(models.Model):
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE, related_name='seo')
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    og_title = models.CharField(max_length=255, blank=True)
    og_image = models.URLField(blank=True)
    tags = models.CharField(max_length=255, blank=True)  # Comma-separated tags
    schema_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"SEO for {self.blog.title}"

class Notification(models.Model):
    notification_id = models.CharField(primary_key=True, max_length=100)
    type = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    recipient_id = models.CharField(max_length=100, db_index=True)
    recipient_type = models.CharField(max_length=10, choices=[("user", "User"), ("admin", "Admin")], db_index=True)
    source_table = models.CharField(max_length=100)
    source_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[("unread", "Unread"), ("read", "Read")], db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CallbackRequest(models.Model):
    callback_id = models.CharField(primary_key=True, max_length=100)
    sender_id = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class HeroBanner(models.Model):
    hero_id = models.CharField(primary_key=True, max_length=100)
    alt_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class HeroBannerImage(models.Model):
    banner = models.ForeignKey(HeroBanner, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey('Image', on_delete=models.CASCADE)
    device_type = models.CharField(max_length=20, choices=[('desktop', 'Desktop'), ('mobile', 'Mobile')], db_index=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class DeletedItemsCache(models.Model):
    cache_id = models.CharField(primary_key=True, max_length=100)
    table_name = models.CharField(max_length=100, db_index=True)
    record_data = models.JSONField()
    deleted_at = models.DateTimeField()
    deleted_reason = models.TextField()
    restored = models.BooleanField(default=False)
    restored_at = models.DateTimeField(null=True, blank=True)

class SiteSettings(models.Model):
    setting_id = models.CharField(primary_key=True, max_length=100)
    site_title = models.CharField(max_length=100)
    logo_url = models.URLField()
    language = models.CharField(max_length=20)
    currency = models.CharField(max_length=10)
    timezone = models.CharField(max_length=50)
    tax_rate = models.FloatField()
    payment_modes = models.JSONField()
    shipping_zones = models.JSONField()
    social_links = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

class DashboardSnapshot(models.Model):
    dashboard_id = models.CharField(primary_key=True, max_length=100)
    snapshot_type = models.CharField(
        max_length=50,
        choices=[("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("yearly", "Yearly")]
    )
    snapshot_date = models.DateField()

    new_users = models.IntegerField()
    orders_placed = models.IntegerField()
    orders_cancelled = models.IntegerField()
    orders_delivered = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    active_users = models.IntegerField()

    order_growth_rate = models.FloatField()
    user_growth_rate = models.FloatField()
    active_user_growth_rate = models.FloatField()

    top_visited_pages = models.JSONField(default=list)
    top_companies = models.JSONField(default=list)
    countries_ordered_from = models.JSONField(default=list)

    data_source = models.CharField(max_length=100)  # e.g. 'live_data', 'backup', etc.
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

class FirstCarousel(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
    
class FirstCarouselImage(models.Model):
    carousel = models.ForeignKey(
        FirstCarousel, 
        on_delete=models.CASCADE, 
        related_name="images"
    )
    image = models.ForeignKey('Image', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="", blank=True)

    # Now linked to SubCategory instead of Category
    subcategory = models.ForeignKey(
        'SubCategory',
        to_field='subcategory_id',        # use the Char PK
        db_column='subcategory_id',       # column literally named subcategory_id
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='first_carousel_images',
    )

    caption = models.CharField(max_length=255, default="", blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class SecondCarousel(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title

class SecondCarouselImage(models.Model):
    carousel = models.ForeignKey(
        SecondCarousel, 
        on_delete=models.CASCADE, 
        related_name="images"
    )
    image = models.ForeignKey('Image', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="", blank=True)

    # Now linked to SubCategory instead of Category
    subcategory = models.ForeignKey(
        'SubCategory',
        to_field='subcategory_id',
        db_column='subcategory_id',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='second_carousel_images',
    )

    caption = models.CharField(max_length=255, default="", blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

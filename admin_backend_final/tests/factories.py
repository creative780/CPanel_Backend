"""
Test data factories using factory-boy for all models.
"""
import uuid
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from admin_backend_final.models import (
    User, Admin, AdminRole, AdminRoleMap,
    Image, Category, SubCategory, CategorySubCategoryMap,
    Product, ProductImage, ProductInventory, ProductVariant,
    ProductSEO, ProductCards, Attribute, AttributeSubCategory,
    Cart, CartItem, Orders, OrderItem, OrderDelivery,
    BlogPost, BlogImage, BlogComment,
    Favorite, Testimonial, ProductTestimonial,
    FirstCarousel, FirstCarouselImage, SecondCarousel, SecondCarouselImage,
    HeroBanner, HeroBannerImage,
    SiteBranding, SiteSettings,
    Notification, CallbackRequest,
)

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    user_id = factory.Sequence(lambda n: f"user_{n:04d}")
    username = factory.Sequence(lambda n: f"user{n}@example.com")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpassword123')
    is_active = True
    is_verified = True


class AdminFactory(DjangoModelFactory):
    class Meta:
        model = Admin
        django_get_or_create = ('admin_id',)

    admin_id = factory.Sequence(lambda n: f"admin_{n:04d}")
    admin_name = factory.Faker('name')
    password_hash = factory.Faker('sha256')


class AdminRoleFactory(DjangoModelFactory):
    class Meta:
        model = AdminRole

    role_id = factory.Sequence(lambda n: f"role_{n:04d}")
    role_name = factory.Faker('job')
    description = factory.Faker('text', max_nb_chars=200)
    access_pages = factory.List([factory.Faker('word') for _ in range(3)])


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = Image

    image_id = factory.Sequence(lambda n: f"img_{n:04d}")
    alt_text = factory.Faker('sentence', nb_words=4)
    width = fuzzy.FuzzyInteger(100, 2000)
    height = fuzzy.FuzzyInteger(100, 2000)
    tags = factory.List([factory.Faker('word') for _ in range(2)])
    image_type = fuzzy.FuzzyChoice(['product', 'category', 'blog', 'banner'])
    linked_table = factory.Faker('word')
    linked_id = factory.Sequence(lambda n: f"linked_{n:04d}")


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    category_id = factory.Sequence(lambda n: f"cat_{n:04d}")
    name = factory.Faker('word')
    status = fuzzy.FuzzyChoice(['visible', 'hidden'])
    caption = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=500)
    created_by = factory.Sequence(lambda n: f"admin_{n:04d}")
    order = factory.Sequence(lambda n: n)


class SubCategoryFactory(DjangoModelFactory):
    class Meta:
        model = SubCategory

    subcategory_id = factory.Sequence(lambda n: f"subcat_{n:04d}")
    name = factory.Faker('word')
    status = fuzzy.FuzzyChoice(['visible', 'hidden'])
    created_by = factory.Sequence(lambda n: f"admin_{n:04d}")
    caption = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=500)
    order = factory.Sequence(lambda n: n)


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    product_id = factory.Sequence(lambda n: f"prod_{n:04d}")
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=1000)
    long_description = factory.Faker('text', max_nb_chars=2000)
    brand = factory.Faker('company')
    price = fuzzy.FuzzyDecimal(10.0, 1000.0, precision=2)
    discounted_price = fuzzy.FuzzyDecimal(5.0, 500.0, precision=2)
    tax_rate = fuzzy.FuzzyFloat(0.0, 0.2)
    price_calculator = factory.Faker('text', max_nb_chars=500)
    status = fuzzy.FuzzyChoice(['active', 'inactive', 'draft'])
    created_by = factory.Sequence(lambda n: f"admin_{n:04d}")
    created_by_type = fuzzy.FuzzyChoice(['admin', 'user'])
    order = factory.Sequence(lambda n: n)
    rating = fuzzy.FuzzyFloat(0.0, 5.0)
    rating_count = fuzzy.FuzzyInteger(0, 100)


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart

    cart_id = factory.Sequence(lambda n: f"cart_{n:04d}")
    device_uuid = factory.Faker('uuid4')


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem

    item_id = factory.Sequence(lambda n: f"cartitem_{n:04d}")
    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 10)
    price_per_unit = fuzzy.FuzzyDecimal(10.0, 100.0, precision=2)
    subtotal = factory.LazyAttribute(lambda obj: obj.price_per_unit * obj.quantity)
    selected_size = fuzzy.FuzzyChoice(['S', 'M', 'L', 'XL', None])
    selected_attributes = factory.Dict({})
    variant_signature = factory.Faker('word')
    attributes_price_delta = Decimal('0.00')


class OrdersFactory(DjangoModelFactory):
    class Meta:
        model = Orders

    order_id = factory.Sequence(lambda n: f"order_{n:04d}")
    device_uuid = factory.Faker('uuid4')
    user_name = factory.Faker('name')
    order_date = factory.LazyFunction(timezone.now)
    status = fuzzy.FuzzyChoice(['pending', 'shipped', 'completed', 'cancelled'])
    total_price = fuzzy.FuzzyDecimal(50.0, 1000.0, precision=2)
    notes = factory.Faker('text', max_nb_chars=200)


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    item_id = factory.Sequence(lambda n: f"orderitem_{n:04d}")
    order = factory.SubFactory(OrdersFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 5)
    unit_price = fuzzy.FuzzyDecimal(10.0, 100.0, precision=2)
    total_price = factory.LazyAttribute(lambda obj: obj.unit_price * obj.quantity)
    selected_size = fuzzy.FuzzyChoice(['S', 'M', 'L', 'XL', None])
    selected_attributes = factory.Dict({})
    selected_attributes_human = factory.List([])
    variant_signature = factory.Faker('word')
    attributes_price_delta = Decimal('0.00')
    price_breakdown = factory.Dict({})


class OrderDeliveryFactory(DjangoModelFactory):
    class Meta:
        model = OrderDelivery

    delivery_id = factory.Sequence(lambda n: f"delivery_{n:04d}")
    order = factory.SubFactory(OrdersFactory)
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    street_address = factory.Faker('street_address')
    city = factory.Faker('city')
    zip_code = factory.Faker('zipcode')
    instructions = factory.List([])


class BlogPostFactory(DjangoModelFactory):
    class Meta:
        model = BlogPost

    blog_id = factory.Sequence(lambda n: f"blog_{n:04d}")
    title = factory.Faker('sentence', nb_words=6)
    slug = factory.LazyAttribute(lambda obj: f"blog-{obj.blog_id}")
    content_html = factory.Faker('text', max_nb_chars=5000)
    author = factory.Faker('name')
    meta_title = factory.Faker('sentence', nb_words=5)
    meta_description = factory.Faker('text', max_nb_chars=200)
    og_title = factory.Faker('sentence', nb_words=4)
    og_image_url = factory.Faker('image_url')
    tags = factory.Faker('words', nb=3, ext_word_list=None)
    schema_enabled = False
    publish_date = factory.LazyFunction(timezone.now)
    draft = False
    status = fuzzy.FuzzyChoice(['draft', 'scheduled', 'published'])


class BlogCommentFactory(DjangoModelFactory):
    class Meta:
        model = BlogComment

    comment_id = factory.LazyFunction(uuid.uuid4)  # UUID field
    blog = factory.SubFactory(BlogPostFactory)
    name = factory.Faker('name')
    email = factory.Faker('email')
    website = factory.Faker('url')
    comment = factory.Faker('text', max_nb_chars=500)


class FavoriteFactory(DjangoModelFactory):
    class Meta:
        model = Favorite

    favorite_id = factory.LazyFunction(uuid.uuid4)  # UUID field
    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    device_uuid = factory.Faker('uuid4')


class TestimonialFactory(DjangoModelFactory):
    class Meta:
        model = Testimonial

    testimonial_id = factory.Sequence(lambda n: f"testimonial_{n:04d}")
    name = factory.Faker('name')
    role = factory.Faker('job')
    content = factory.Faker('text', max_nb_chars=500)
    image_url = factory.Faker('image_url')
    rating = fuzzy.FuzzyInteger(1, 5)
    status = fuzzy.FuzzyChoice(['draft', 'published'])
    created_by = factory.Sequence(lambda n: f"admin_{n:04d}")
    created_by_type = fuzzy.FuzzyChoice(['admin', 'user'])
    order = factory.Sequence(lambda n: n)


class AttributeSubCategoryFactory(DjangoModelFactory):
    class Meta:
        model = AttributeSubCategory

    attribute_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: f"attr-{obj.name.lower()}")
    type = fuzzy.FuzzyChoice(['size', 'color', 'material', 'custom'])
    status = fuzzy.FuzzyChoice(['visible', 'hidden'])
    description = factory.Faker('text', max_nb_chars=200)
    values = factory.List([])
    subcategory_ids = factory.List([])


class FirstCarouselFactory(DjangoModelFactory):
    class Meta:
        model = FirstCarousel

    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=300)


class SecondCarouselFactory(DjangoModelFactory):
    class Meta:
        model = SecondCarousel

    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=300)


class HeroBannerFactory(DjangoModelFactory):
    class Meta:
        model = HeroBanner

    hero_id = factory.Sequence(lambda n: f"hero_{n:04d}")
    alt_text = factory.Faker('sentence', nb_words=4)


class SiteBrandingFactory(DjangoModelFactory):
    class Meta:
        model = SiteBranding

    branding_id = factory.Sequence(lambda n: f"branding_{n:04d}")
    site_title = factory.Faker('company')
    singleton_lock = 'X'


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    notification_id = factory.Sequence(lambda n: f"notif_{n:04d}")
    type = fuzzy.FuzzyChoice(['order', 'product', 'user', 'system'])
    title = factory.Faker('sentence', nb_words=4)
    message = factory.Faker('text', max_nb_chars=200)
    recipient_id = factory.Sequence(lambda n: f"user_{n:04d}")
    recipient_type = fuzzy.FuzzyChoice(['user', 'admin'])
    source_table = factory.Faker('word')
    source_id = factory.Sequence(lambda n: f"source_{n:04d}")
    status = fuzzy.FuzzyChoice(['unread', 'read'])


from django.contrib import admin
from .models import (
    User, Admin, AdminRole, AdminRoleMap,
    Image, Product, ProductInventory, ProductVariant, VariantCombination,
    ShippingInfo, ProductSEO, Category, CategoryImage,
    SubCategory, SubCategoryImage, CategorySubCategoryMap, ProductSubCategoryMap,
    Orders, OrderItem, OrderDelivery, Cart, CartItem,
    Blog, BlogCategory, BlogCategoryMap,
    Notification, CallbackRequest,
    HeroBanner, HeroBannerImage,
    DeletedItemsCache, SiteSettings, DashboardSnapshot,
    ProductImage
)

admin.site.register(User)
admin.site.register(Admin)
admin.site.register(AdminRole)
admin.site.register(AdminRoleMap)

admin.site.register(Image)
admin.site.register(Product)
admin.site.register(ProductInventory)
admin.site.register(ProductVariant)
admin.site.register(VariantCombination)

admin.site.register(ShippingInfo)
admin.site.register(ProductSEO)

admin.site.register(Category)
admin.site.register(CategoryImage)
admin.site.register(SubCategory)
admin.site.register(SubCategoryImage)
admin.site.register(CategorySubCategoryMap)
admin.site.register(ProductSubCategoryMap)

admin.site.register(Orders)
admin.site.register(OrderItem)
admin.site.register(OrderDelivery)

admin.site.register(Cart)
admin.site.register(CartItem)

admin.site.register(Blog)
admin.site.register(BlogCategory)
admin.site.register(BlogCategoryMap)

admin.site.register(Notification)
admin.site.register(CallbackRequest)

admin.site.register(HeroBanner)
admin.site.register(HeroBannerImage)

admin.site.register(DeletedItemsCache)
admin.site.register(SiteSettings)
admin.site.register(DashboardSnapshot)

admin.site.register(ProductImage)

from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4
    fields = ("sort", "image", "image_url")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name","slug")
    list_display = ("name", "slug", "icon", "order")
    list_editable = ("icon", "order")
    fields = ("name", "slug", "icon", "image", "order")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ("title", "category", "price", "is_active", "in_stock", "is_hit", "is_new")
    list_filter = ("category", "is_active", "in_stock", "is_hit", "is_new")
    search_fields = ("title","slug")
    prepopulated_fields = {"slug": ("title",)}
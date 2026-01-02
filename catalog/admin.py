from django.contrib import admin

from .models import Category, Product, ProductReview, ProductSize


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_editable = ('stock', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSizeInline]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'rating', 'name', 'user', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'rating', 'created_at')
    search_fields = ('product__name', 'name', 'comment', 'user__username')

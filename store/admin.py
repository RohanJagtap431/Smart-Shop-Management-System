
from django.contrib import admin
from .models import (
    ShopProfile,
    Category,
    Product,
    Bill,
    BillItem,
    StockMovement,
)
from .models import Payment

from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "gstin", "is_active", "created_at")
    search_fields = ("name", "phone", "gstin")
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)

admin.site.register(Payment)


@admin.register(ShopProfile)
class ShopProfileAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "owner_name", "phone", "gstin")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "selling_price",
        "stock_quantity",
        "unit",
        "gst_rate",
        "is_active",
    )
    list_filter = ("category", "is_active", "gst_rate")
    search_fields = ("name", "barcode")


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer_name",
        "grand_total",
        "payment_method",
        "created_at",
    )
    search_fields = ("invoice_number", "customer_name", "customer_phone")
    list_filter = ("payment_method", "created_at")
    inlines = [BillItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "movement_type",
        "quantity",
        "reference",
        "created_at",
    )
    list_filter = ("movement_type", "created_at")

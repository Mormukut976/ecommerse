from django.contrib import admin

from .models import Payment, PaymentMethod


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'method_type', 'is_active', 'sort_order', 'updated_at')
    list_editable = ('is_active', 'sort_order')
    list_filter = ('method_type', 'is_active')
    search_fields = ('name', 'upi_id', 'account_number', 'bank_name')
    ordering = ('sort_order', 'name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'amount', 'manual_reference', 'provider_order_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_code', 'order__id', 'manual_reference', 'provider_order_id', 'provider_payment_id')

    actions = ['mark_verified', 'mark_failed']

    def mark_verified(self, request, queryset):
        for payment in queryset:
            payment.status = Payment.Status.VERIFIED
            payment.save()

    def mark_failed(self, request, queryset):
        for payment in queryset:
            payment.status = Payment.Status.FAILED
            payment.save()

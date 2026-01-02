from django.contrib import admin, messages

from .models import Order, OrderItem

from payments.models import Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'size_label', 'unit_price', 'quantity', 'line_total')


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False
    fields = (
        'provider',
        'status',
        'amount',
        'manual_reference',
        'manual_proof',
        'provider_order_id',
        'provider_payment_id',
        'provider_signature',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'provider',
        'amount',
        'manual_reference',
        'manual_proof',
        'provider_order_id',
        'provider_payment_id',
        'provider_signature',
        'created_at',
        'updated_at',
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'full_name', 'phone', 'payment_method', 'manual_payment_method', 'status', 'total', 'created_at')
    list_display_links = ('order_code',)
    list_editable = ('status',)
    list_filter = ('status', 'payment_method', 'manual_payment_method', 'created_at')
    search_fields = ('order_code', 'id', 'full_name', 'phone')
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ('order_code',)
    actions = [
        'mark_payment_verified',
        'mark_payment_failed',
        'mark_ready_to_go',
        'mark_shipped',
        'mark_out_for_delivery',
        'mark_arrived',
        'mark_delivered',
        'mark_cancelled',
    ]

    def _set_status(self, request, queryset, *, status, allowed_from=None):
        updated = 0
        skipped = 0
        for order in queryset:
            if allowed_from is not None and order.status not in allowed_from:
                skipped += 1
                continue
            order.status = status
            order.save()
            updated += 1

        self.message_user(
            request,
            f"Updated status to {Order.Status(status).label} for {updated} order(s). Skipped {skipped} order(s).",
            level=messages.SUCCESS,
        )

    def mark_payment_verified(self, request, queryset):
        updated = 0
        skipped = 0
        for order in queryset:
            try:
                payment = order.payment
            except Payment.DoesNotExist:
                skipped += 1
                continue
            payment.status = Payment.Status.VERIFIED
            payment.save()
            updated += 1
        self.message_user(
            request,
            f"Verified payment for {updated} order(s). Skipped {skipped} order(s) without a payment record.",
            level=messages.SUCCESS,
        )

    def mark_payment_failed(self, request, queryset):
        updated = 0
        skipped = 0
        for order in queryset:
            try:
                payment = order.payment
            except Payment.DoesNotExist:
                skipped += 1
                continue
            payment.status = Payment.Status.FAILED
            payment.save()
            updated += 1
        self.message_user(
            request,
            f"Marked payment failed for {updated} order(s). Skipped {skipped} order(s) without a payment record.",
            level=messages.SUCCESS,
        )

    @admin.action(description='Mark as Ready to Go')
    def mark_ready_to_go(self, request, queryset):
        self._set_status(request, queryset, status=Order.Status.READY_TO_GO, allowed_from={Order.Status.PAID})

    @admin.action(description='Mark as Shipped')
    def mark_shipped(self, request, queryset):
        self._set_status(
            request,
            queryset,
            status=Order.Status.SHIPPED,
            allowed_from={Order.Status.PAID, Order.Status.READY_TO_GO},
        )

    @admin.action(description='Mark as Out for Delivery')
    def mark_out_for_delivery(self, request, queryset):
        self._set_status(request, queryset, status=Order.Status.OUT_FOR_DELIVERY, allowed_from={Order.Status.SHIPPED})

    @admin.action(description='Mark as Arrived')
    def mark_arrived(self, request, queryset):
        self._set_status(
            request,
            queryset,
            status=Order.Status.ARRIVED,
            allowed_from={Order.Status.OUT_FOR_DELIVERY},
        )

    @admin.action(description='Mark as Delivered')
    def mark_delivered(self, request, queryset):
        self._set_status(
            request,
            queryset,
            status=Order.Status.DELIVERED,
            allowed_from={Order.Status.OUT_FOR_DELIVERY, Order.Status.ARRIVED},
        )

    @admin.action(description='Cancel order')
    def mark_cancelled(self, request, queryset):
        self._set_status(
            request,
            queryset,
            status=Order.Status.CANCELLED,
            allowed_from={
                Order.Status.PENDING_PAYMENT,
                Order.Status.PAYMENT_SUBMITTED,
                Order.Status.PLACED,
                Order.Status.PAID,
                Order.Status.READY_TO_GO,
                Order.Status.SHIPPED,
                Order.Status.OUT_FOR_DELIVERY,
                Order.Status.ARRIVED,
            },
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'size_label', 'quantity', 'unit_price', 'line_total')
    list_filter = ('order',)
    search_fields = ('product_name',)

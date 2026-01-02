import secrets

from django.conf import settings
from django.db import models


class Order(models.Model):
    class PaymentMethod(models.TextChoices):
        MANUAL = 'MANUAL', 'UPI/Bank (Manual)'

    class Status(models.TextChoices):
        PENDING_PAYMENT = 'PENDING_PAYMENT', 'Pending Payment'
        PAYMENT_SUBMITTED = 'PAYMENT_SUBMITTED', 'Payment Submitted'
        PLACED = 'PLACED', 'Placed'
        PAID = 'PAID', 'Confirmed'
        READY_TO_GO = 'READY_TO_GO', 'Ready to Go'
        SHIPPED = 'SHIPPED', 'Shipped'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
        ARRIVED = 'ARRIVED', 'Arrived'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    @staticmethod
    def _random_order_code() -> str:
        return f"{secrets.randbelow(10**12):012d}"

    @classmethod
    def _generate_unique_order_code(cls) -> str:
        for _ in range(50):
            code = cls._random_order_code()
            if not cls.objects.filter(order_code=code).exists():
                return code
        raise RuntimeError('Unable to generate unique order code')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    order_code = models.CharField(max_length=12, unique=True, editable=False)

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    pincode = models.CharField(max_length=12)

    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.MANUAL)
    manual_payment_method = models.ForeignKey(
        'payments.PaymentMethod',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='orders',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self._generate_unique_order_code()
            update_fields = kwargs.get('update_fields')
            if update_fields is not None:
                kwargs['update_fields'] = set(update_fields) | {'order_code'}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_code}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT)

    size_label = models.CharField(max_length=50, blank=True, default='')
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

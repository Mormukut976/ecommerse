from django.db import models


class PaymentMethod(models.Model):
    class Type(models.TextChoices):
        UPI = 'UPI', 'UPI'
        BANK = 'BANK', 'Bank Transfer'
        QR = 'QR', 'QR Code'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=120)
    method_type = models.CharField(max_length=20, choices=Type.choices, default=Type.UPI)

    upi_id = models.CharField(blank=True, max_length=120)

    account_name = models.CharField(blank=True, max_length=120)
    account_number = models.CharField(blank=True, max_length=50)
    ifsc_code = models.CharField(blank=True, max_length=20)
    bank_name = models.CharField(blank=True, max_length=120)

    qr_image = models.ImageField(upload_to='payment_methods/', blank=True, null=True)

    instructions = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Payment(models.Model):
    class Provider(models.TextChoices):
        MANUAL = 'MANUAL', 'Manual'

    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        CAPTURED = 'CAPTURED', 'Captured'
        VERIFIED = 'VERIFIED', 'Verified'
        FAILED = 'FAILED', 'Failed'

    order = models.OneToOneField('orders.Order', related_name='payment', on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.MANUAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    manual_reference = models.CharField(blank=True, max_length=120, default='')
    manual_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)

    provider_order_id = models.CharField(max_length=120, blank=True)
    provider_payment_id = models.CharField(max_length=120, blank=True)
    provider_signature = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order #{self.order_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from orders.models import Order

        if self.status in {self.Status.CAPTURED, self.Status.VERIFIED} and self.order.status in {
            Order.Status.PENDING_PAYMENT,
            Order.Status.PAYMENT_SUBMITTED,
        }:
            self.order.status = Order.Status.PAID
            self.order.save()

        if self.status == self.Status.FAILED and self.order.status in {Order.Status.PAYMENT_SUBMITTED, Order.Status.PAID}:
            self.order.status = Order.Status.PENDING_PAYMENT
            self.order.save()

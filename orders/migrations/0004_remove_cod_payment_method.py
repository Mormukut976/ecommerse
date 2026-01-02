from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_manual_payment_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('RAZORPAY', 'Razorpay'),
                    ('MANUAL', 'UPI/Bank (Manual)'),
                ],
                default='MANUAL',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('PENDING_PAYMENT', 'Pending Payment'),
                    ('PAYMENT_SUBMITTED', 'Payment Submitted'),
                    ('PLACED', 'Placed'),
                    ('PAID', 'Confirmed'),
                    ('SHIPPED', 'Shipped'),
                    ('DELIVERED', 'Delivered'),
                    ('CANCELLED', 'Cancelled'),
                ],
                default='PENDING_PAYMENT',
            ),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING_PAYMENT', 'Pending Payment'),
                    ('PAYMENT_SUBMITTED', 'Payment Submitted'),
                    ('PLACED', 'Placed'),
                    ('PAID', 'Confirmed'),
                    ('READY_TO_GO', 'Ready to Go'),
                    ('SHIPPED', 'Shipped'),
                    ('OUT_FOR_DELIVERY', 'Out for Delivery'),
                    ('ARRIVED', 'Arrived'),
                    ('DELIVERED', 'Delivered'),
                    ('CANCELLED', 'Cancelled'),
                ],
                default='PENDING_PAYMENT',
                max_length=20,
            ),
        ),
    ]

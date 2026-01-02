import secrets

from django.db import migrations, models


def _random_order_code() -> str:
    return f"{secrets.randbelow(10**12):012d}"


def _generate_unique_order_code(Order) -> str:
    for _ in range(50):
        code = _random_order_code()
        if not Order.objects.filter(order_code=code).exists():
            return code
    raise RuntimeError('Unable to generate unique order code')


def populate_order_codes(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')

    for order in Order.objects.filter(order_code__isnull=True).iterator():
        order.order_code = _generate_unique_order_code(Order)
        order.save(update_fields=['order_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_status_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_code',
            field=models.CharField(editable=False, max_length=12, null=True, unique=True),
        ),
        migrations.RunPython(populate_order_codes, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='order',
            name='order_code',
            field=models.CharField(editable=False, max_length=12, unique=True),
        ),
    ]

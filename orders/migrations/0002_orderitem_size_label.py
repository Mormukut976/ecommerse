from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='size_label',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]

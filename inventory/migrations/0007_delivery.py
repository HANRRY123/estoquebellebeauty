from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_financeentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_address', models.CharField(blank=True, max_length=220)),
                ('departure_date', models.DateField()),
                ('expected_date', models.DateField()),
                ('status', models.CharField(choices=[('in_transit', 'Em transporte'), ('delivered', 'Entregue'), ('cancelled', 'Cancelada'), ('not_delivered', 'Não entregue')], default='in_transit', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=models.PROTECT, related_name='deliveries', to='inventory.client')),
                ('sale', models.ForeignKey(on_delete=models.PROTECT, related_name='deliveries', to='inventory.sale')),
            ],
            options={
                'ordering': ['-departure_date', '-created_at'],
            },
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_product_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('customer', models.CharField(blank=True, max_length=120)),
                ('color', models.CharField(blank=True, max_length=40)),
                ('payment_type', models.CharField(choices=[('cash', 'Dinheiro'), ('credit_card', 'Cartão de Crédito'), ('debit_card', 'Cartão de Débito'), ('pix', 'Pix'), ('boleto', 'Boleto')], default='cash', max_length=20)),
                ('sale_date', models.DateField()),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sales', to='inventory.product')),
            ],
            options={
                'ordering': ['-sale_date', '-created_at'],
            },
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_sale_quantity_alter_sale_unit_cost_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('instagram', models.CharField(blank=True, max_length=120)),
                ('phone', models.CharField(blank=True, max_length=40)),
                ('address', models.CharField(blank=True, max_length=220)),
                ('cpf_cnpj', models.CharField(blank=True, max_length=30)),
                ('complement', models.CharField(blank=True, max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at', 'name'],
            },
        ),
    ]

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinanceEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_type', models.CharField(choices=[('entry', 'Entrada'), ('exit', 'Saída')], default='entry', max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ('category', models.CharField(blank=True, max_length=120)),
                ('description', models.TextField(blank=True)),
                ('date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]

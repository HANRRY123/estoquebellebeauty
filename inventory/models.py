from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    sku = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=80, blank=True)
    color = models.CharField(max_length=40, blank=True)
    size = models.CharField(max_length=20, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity = models.IntegerField(default=0)
    image1 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-quantity', 'name']

    def __str__(self):
        return self.name

    @property
    def stock_value(self):
        return self.cost_price * self.quantity

    @property
    def profit(self):
        return (self.sale_price - self.cost_price) * self.quantity

    @property
    def profit_percentage(self):
        if self.cost_price == 0:
            return Decimal('0.00')
        return ((self.sale_price - self.cost_price) / self.cost_price) * Decimal('100.00')

    @property
    def status(self):
        if self.quantity <= 1:
            return 'Baixo'
        if self.quantity <= 4:
            return 'Médio'
        return 'Saudável'


class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Dinheiro'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'Pix'),
        ('boleto', 'Boleto'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sales')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    customer = models.CharField(max_length=120, blank=True)
    color = models.CharField(max_length=40, blank=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    sale_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sale_date', '-created_at']

    def __str__(self):
        return f'{self.product.name} x{self.quantity} ({self.sale_date})'

    @property
    def total_revenue(self):
        return self.unit_price * self.quantity

    @property
    def total_cost(self):
        cost = self.unit_cost if self.unit_cost is not None else self.product.cost_price
        return cost * self.quantity

    @property
    def total_profit(self):
        return self.total_revenue - self.total_cost


class FinanceEntry(models.Model):
    MOVEMENT_TYPES = [
        ('entry', 'Entrada'),
        ('exit', 'Saída'),
    ]

    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, default='entry')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.get_movement_type_display()} - R$ {self.amount} ({self.date})'


class Client(models.Model):
    name = models.CharField(max_length=120)
    instagram = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=220, blank=True)
    cpf_cnpj = models.CharField(max_length=30, blank=True)
    complement = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('in_transit', 'Em transporte'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelada'),
        ('not_delivered', 'Não entregue'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='deliveries')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='deliveries')
    client_address = models.CharField(max_length=220, blank=True)
    departure_date = models.DateField()
    expected_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_transit')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-departure_date', '-created_at']

    def __str__(self):
        return f'{self.sale.product.name} para {self.client.name} ({self.get_status_display()})'

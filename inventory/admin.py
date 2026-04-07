from django.contrib import admin

from .models import Client, Delivery, FinanceEntry, Product, Sale


@admin.register(FinanceEntry)
class FinanceEntryAdmin(admin.ModelAdmin):
    list_display = ('movement_type', 'amount', 'category', 'date', 'created_at')
    list_filter = ('movement_type', 'date')
    search_fields = ('category', 'description')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('sale', 'client', 'departure_date', 'expected_date', 'status')
    list_filter = ('status', 'departure_date', 'expected_date')
    search_fields = ('sale__product__name', 'client__name', 'client_address')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'instagram', 'phone', 'address', 'cpf_cnpj', 'created_at')
    search_fields = ('name', 'instagram', 'phone', 'cpf_cnpj')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'color', 'size', 'quantity', 'sale_price', 'status')
    list_filter = ('category', 'color', 'size')
    search_fields = ('sku', 'name')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'unit_price', 'unit_cost', 'payment_type', 'sale_date', 'customer')
    list_filter = ('payment_type', 'sale_date')
    search_fields = ('product__name', 'customer', 'product__sku')

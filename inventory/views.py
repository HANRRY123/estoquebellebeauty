from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ClientForm, DeliveryForm, FinanceEntryForm, ProductForm, SaleForm
from .models import Client, Delivery, FinanceEntry, Product, Sale


@login_required(login_url='login')
def dashboard(request):
    products = Product.objects.all()
    sales = Sale.objects.all()

    total_products = products.count()
    stock_value = sum((product.cost_price * product.quantity) for product in products)
    potential_profit = sum(product.profit for product in products)

    gross_sales = sales.aggregate(
        total=Coalesce(Sum(F('unit_price') * F('quantity'), output_field=DecimalField(max_digits=16, decimal_places=2)), Decimal('0.00'))
    )['total']
    net_sales = sales.aggregate(
        total=Coalesce(Sum((F('unit_price') - Coalesce(F('unit_cost'), F('product__cost_price'))) * F('quantity'), output_field=DecimalField(max_digits=16, decimal_places=2)), Decimal('0.00'))
    )['total']

    top_sold = Product.objects.annotate(
        total_sold=Coalesce(Sum('sales__quantity'), 0),
        total_revenue=Coalesce(Sum(F('sales__unit_price') * F('sales__quantity'), output_field=DecimalField(max_digits=16, decimal_places=2)), Decimal('0.00')),
        total_profit=Coalesce(Sum((F('sales__unit_price') - Coalesce(F('sales__unit_cost'), F('cost_price'))) * F('sales__quantity'), output_field=DecimalField(max_digits=16, decimal_places=2)), Decimal('0.00')),
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]

    low_stock = products.filter(quantity__lte=3).order_by('quantity')[:5]

    context = {
        'total_products': total_products,
        'stock_value': stock_value,
        'potential_profit': potential_profit,
        'gross_sales': gross_sales,
        'net_sales': net_sales,
        'top_sold': top_sold,
        'low_stock': low_stock,
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required(login_url='login')
def estoque(request):
    products = Product.objects.all()
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query)

    category = request.GET.get('category', 'Todas')
    if category and category != 'Todas':
        products = products.filter(category=category)

    color = request.GET.get('color', 'Todas')
    if color and color != 'Todas':
        products = products.filter(color=color)

    categories = Product.objects.values_list('category', flat=True).distinct()
    colors = Product.objects.values_list('color', flat=True).distinct()

    context = {
        'products': products,
        'query': query,
        'category': category,
        'color': color,
        'categories': categories,
        'colors': colors,
    }
    return render(request, 'inventory/estoque.html', context)


@login_required(login_url='login')
def sales(request):
    query = request.GET.get('q', '')
    payment = request.GET.get('payment', 'all')
    sales_qs = Sale.objects.select_related('product').all()

    if query:
        sales_qs = sales_qs.filter(customer__icontains=query)

    if payment and payment != 'all':
        sales_qs = sales_qs.filter(payment_type=payment)

    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            if sale.unit_cost is None:
                sale.unit_cost = sale.product.cost_price
            sale.save()
            product = sale.product
            product.quantity -= sale.quantity
            product.save()
            return redirect('dashboard')
    else:
        form = SaleForm()

    context = {
        'form': form,
        'sales': sales_qs.order_by('-sale_date', '-created_at')[:20],
        'query': query,
        'payment': payment,
    }
    return render(request, 'inventory/sales.html', context)


@login_required(login_url='login')
def finance(request):
    if request.method == 'POST':
        form = FinanceEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance')
    else:
        form = FinanceEntryForm()

    finance_qs = FinanceEntry.objects.all()
    sales_qs = Sale.objects.order_by('-sale_date', '-created_at')[:20]

    total_entries = finance_qs.filter(movement_type='entry').aggregate(
        total=Coalesce(Sum('amount', output_field=DecimalField(max_digits=16, decimal_places=2)), Decimal('0.00'))
    )['total']
    total_exits = finance_qs.filter(movement_type='exit').aggregate(
        total=Coalesce(Sum('amount', output_field=DecimalField(max_digits=16, decimal_places=2)), Decimal('0.00'))
    )['total']
    total_sales = sales_qs.aggregate(
        total=Coalesce(Sum(F('unit_price') * F('quantity'), output_field=DecimalField(max_digits=16, decimal_places=2)), Decimal('0.00'))
    )['total']

    bank_balance = total_sales + total_entries - total_exits

    merged_movements = []
    for sale in sales_qs:
        merged_movements.append({
            'date': sale.sale_date,
            'type': 'Venda',
            'amount': sale.total_revenue,
            'category': 'Venda',
            'description': sale.customer or 'Venda registrada',
            'is_sale': True,
        })
    for entry in finance_qs:
        merged_movements.append({
            'date': entry.date,
            'type': entry.get_movement_type_display(),
            'amount': entry.amount,
            'category': entry.category or 'Movimentação',
            'description': entry.description,
            'is_sale': False,
        })
    merged_movements.sort(key=lambda item: item['date'], reverse=True)

    context = {
        'form': form,
        'movements': merged_movements[:20],
        'bank_balance': bank_balance,
        'total_sales': total_sales,
        'total_entries': total_entries,
        'total_exits': total_exits,
    }
    return render(request, 'inventory/financeiro.html', context)


@login_required(login_url='login')
def deliveries(request):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.client_address = delivery.client.address
            delivery.status = 'in_transit'
            delivery.save()
            return redirect('deliveries')
    else:
        form = DeliveryForm()

    deliveries_qs = Delivery.objects.select_related('sale__product', 'client').all()
    context = {
        'form': form,
        'deliveries': deliveries_qs,
        'clients': Client.objects.all(),
        'sales': Sale.objects.select_related('product').all(),
    }
    return render(request, 'inventory/entregas.html', context)


@login_required(login_url='login')
def update_delivery_status(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Delivery.STATUS_CHOICES):
            delivery.status = status
            delivery.save()
    return redirect('deliveries')


@login_required(login_url='login')
def clients(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clients')
    else:
        form = ClientForm()

    clients_qs = Client.objects.all()
    context = {
        'form': form,
        'clients': clients_qs,
    }
    return render(request, 'inventory/clients.html', context)


@login_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('estoque')
    else:
        form = ProductForm()

    return render(request, 'inventory/product_form.html', {'form': form, 'edit_mode': False})


@login_required(login_url='login')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('estoque')
    else:
        form = ProductForm(instance=product)

    return render(request, 'inventory/product_form.html', {'form': form, 'edit_mode': True, 'product': product})


@login_required(login_url='login')
def user_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    users = User.objects.order_by('username')
    return render(request, 'inventory/user_list.html', {'users': users})


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return redirect('estoque')

from decimal import Decimal

from datetime import date

from django import forms
from django.contrib.auth.models import User

from .models import Client, Delivery, FinanceEntry, Product, Sale


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'})
    )

    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            'username': 'Usuário',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Usuário'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Esse usuário já existe.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ProductForm(forms.ModelForm):
    category = forms.CharField(
        label='Categoria',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Categoria'}),
        error_messages={'required': 'A categoria é obrigatória.'},
    )
    cost_price = forms.DecimalField(
        required=False,
        label='Custo',
        widget=forms.TextInput(attrs={'placeholder': 'Custo', 'inputmode': 'decimal'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance or not self.instance.pk:
            self.fields['cost_price'].initial = ''
            self.fields['sale_price'].initial = ''

    class Meta:
        model = Product
        fields = [
            'name',
            'quantity',
            'category',
            'color',
            'size',
            'sku',
            'cost_price',
            'sale_price',
            'image1',
            'image2',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nome do produto'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Quantidade', 'min': '1'}),
            'color': forms.TextInput(attrs={'placeholder': 'Cor'}),
            'size': forms.TextInput(attrs={'placeholder': 'Tam'}),
            'sku': forms.TextInput(attrs={'placeholder': 'SKU'}),
            'sale_price': forms.TextInput(attrs={'placeholder': 'Preço', 'inputmode': 'decimal'}),
            'image1': forms.ClearableFileInput(attrs={'class': 'file-input'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'file-input'}),
        }
        labels = {
            'name': 'Nome',
            'quantity': 'Quantidade',
            'category': 'Categoria',
            'color': 'Cor',
            'size': 'Tamanho',
            'sku': 'SKU',
            'sale_price': 'Preço',
            'image1': 'Imagem 1',
            'image2': 'Imagem 2',
        }
        error_messages = {
            'sku': {
                'unique': 'Essa SKU já está em uso.',
            },
        }

    def clean_cost_price(self):
        value = self.cleaned_data.get('cost_price')
        if value in (None, ''):
            return Decimal('0.00')
        if isinstance(value, str):
            value = value.replace(',', '.')
        return value

    def clean_sale_price(self):
        value = self.cleaned_data.get('sale_price')
        if value is None:
            return value
        if isinstance(value, str):
            value = value.replace(',', '.')
        return value

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            return quantity
        if quantity < 1:
            raise forms.ValidationError('A quantidade deve ser ao menos 1.')
        return quantity


class SaleForm(forms.ModelForm):
    customer = forms.CharField(
        required=False,
        label='Cliente',
        widget=forms.TextInput(attrs={'placeholder': 'Nome do cliente'}),
    )
    color = forms.CharField(
        required=False,
        label='Cor',
        widget=forms.TextInput(attrs={'placeholder': 'Cor'}),
    )
    sale_date = forms.DateField(
        label='Data da Venda',
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today,
    )

    class Meta:
        model = Sale
        fields = [
            'product',
            'quantity',
            'color',
            'customer',
            'payment_type',
            'sale_date',
            'unit_price',
            'unit_cost',
            'notes',
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'select-input'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Quantidade', 'min': '1'}),
            'payment_type': forms.Select(attrs={'class': 'select-input'}),
            'unit_price': forms.TextInput(attrs={'placeholder': 'Preço Personalizado', 'inputmode': 'decimal'}),
            'unit_cost': forms.TextInput(attrs={'placeholder': 'Custo Personalizado (opcional)', 'inputmode': 'decimal'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Observações adicionais', 'rows': 3}),
        }
        labels = {
            'product': 'Produto',
            'quantity': 'Quantidade',
            'payment_type': 'Tipo de Pagamento',
            'unit_price': 'Preço Personalizado',
            'unit_cost': 'Custo Personalizado',
            'notes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(quantity__gt=0)
        self.fields['unit_cost'].required = False
        self.fields['unit_price'].required = True

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')
        if quantity is None:
            return quantity
        if quantity < 1:
            raise forms.ValidationError('A quantidade deve ser ao menos 1.')
        if product and quantity > product.quantity:
            raise forms.ValidationError('Quantidade maior que o estoque disponível.')
        return quantity


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'instagram', 'phone', 'address', 'complement', 'cpf_cnpj']
        labels = {
            'name': 'Nome',
            'instagram': 'Instagram',
            'phone': 'Telefone',
            'address': 'Endereço',
            'complement': 'Complemento',
            'cpf_cnpj': 'CPF/CNPJ',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nome do cliente'}),
            'instagram': forms.TextInput(attrs={'placeholder': 'Instagram'}),
            'phone': forms.TextInput(attrs={'placeholder': '(99) 99999-9999'}),
            'address': forms.TextInput(attrs={'placeholder': 'Bairro, Número, complemento'}),
            'complement': forms.TextInput(attrs={'placeholder': 'Complemento (opcional)'}),
            'cpf_cnpj': forms.TextInput(attrs={'placeholder': 'CPF ou CNPJ'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('O nome é obrigatório.')
        return name


class FinanceEntryForm(forms.ModelForm):
    class Meta:
        model = FinanceEntry
        fields = ['movement_type', 'amount', 'category', 'description', 'date']
        labels = {
            'movement_type': 'Tipo',
            'amount': 'Valor',
            'category': 'Motivo',
            'description': 'Descrição',
            'date': 'Data',
        }
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'select-input'}),
            'amount': forms.TextInput(attrs={'placeholder': 'Valor', 'inputmode': 'decimal'}),
            'category': forms.TextInput(attrs={'placeholder': 'Motivo do gasto'}),
            'description': forms.Textarea(attrs={'placeholder': 'Descrição (opcional)', 'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError('O valor precisa ser maior que zero.')
        return amount


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['sale', 'client', 'departure_date', 'expected_date']
        labels = {
            'sale': 'Venda',
            'client': 'Cliente',
            'departure_date': 'Data de Saída',
            'expected_date': 'Previsão de Entrega',
        }
        widgets = {
            'sale': forms.Select(attrs={'class': 'select-input'}),
            'client': forms.Select(attrs={'class': 'select-input', 'id': 'id_client_select'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('expected_date') and cleaned_data.get('departure_date'):
            if cleaned_data['expected_date'] < cleaned_data['departure_date']:
                raise forms.ValidationError('A previsão não pode ser anterior à data de saída.')
        return cleaned_data

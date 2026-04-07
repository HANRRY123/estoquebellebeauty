from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('estoque/', views.estoque, name='estoque'),
    path('vendas/', views.sales, name='sales'),
    path('clientes/', views.clients, name='clients'),
    path('financeiro/', views.finance, name='finance'),
    path('entregas/', views.deliveries, name='deliveries'),
    path('entregas/<int:pk>/status/', views.update_delivery_status, name='delivery_status'),
    path('produto/novo/', views.add_product, name='product_add'),
    path('produto/<int:pk>/editar/', views.edit_product, name='product_edit'),
    path('produto/<int:pk>/delete/', views.delete_product, name='product_delete'),
    path('login/', auth_views.LoginView.as_view(
        template_name='inventory/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
]

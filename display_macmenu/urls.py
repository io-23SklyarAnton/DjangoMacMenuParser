from django.urls import path
from . import views

app_name = 'display_macmenu'

urlpatterns = [
    path('all_products/', views.all_products, name='all_products'),
    path('products/<str:product_name>/', views.product, name='product'),
    path('products/<str:product_name>/<str:product_field>/', views.product_field, name='product_field')
]

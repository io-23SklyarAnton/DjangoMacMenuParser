from django.shortcuts import render

from display_macmenu.services.display_services import get_products, get_product, get_field


def all_products(request):
    products = get_products()
    return render(request, 'all_products.html', {'products': products})


def product(request, product_name):
    concrete_product = get_product(product_name)
    return render(request, 'concrete_product.html', {'product': concrete_product})


def product_field(request, product_name, product_field):
    field = get_field(product_name, product_field)
    return render(request, 'concrete_product_field.html', {'field_name': product_field, 'field': field})

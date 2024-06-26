from django.http import HttpResponse
from django.shortcuts import render
from .services.selenium_service.macmenu_parse import MacMenu


def home(request):
    return render(request, 'home_page.html')


def collect_menu(request):
    menu = MacMenu()
    success = menu.save_mac_menu_as_json()
    return render(request, 'collect_menu.html', {'success': success})

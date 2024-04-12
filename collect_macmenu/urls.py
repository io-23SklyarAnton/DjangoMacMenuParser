from django.urls import path
from . import views

app_name = 'collect_macmenu'

urlpatterns = [
    path('', views.home, name='home'),
    path('collect_menu/', views.collect_menu, name='collect_menu'),
]

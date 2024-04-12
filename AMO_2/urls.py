from django.contrib import admin
from django.urls import path, include

from collect_macmenu.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('collect_macmenu/', include('collect_macmenu.urls', namespace='collect_macmenu')),
    path('display_macmenu/', include('display_macmenu.urls', namespace='display_macmenu')),
    path('__debug__/', include('debug_toolbar.urls')),
]

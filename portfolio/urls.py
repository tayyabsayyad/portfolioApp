
# portfolio/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login', permanent=False)),  # root → login
    path('admin/', admin.site.urls),
    path('trades/', include('trades.urls')),   # our app routes
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
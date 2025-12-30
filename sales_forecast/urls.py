"""
URL configuration for sales_forecast project.
"""
from django.contrib import admin  # type: ignore
from django.urls import path, include  # type: ignore
from django.conf import settings  # type: ignore
from django.conf.urls.static import static  # type: ignore

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)


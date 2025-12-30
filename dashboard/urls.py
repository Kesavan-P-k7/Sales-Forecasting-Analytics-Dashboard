"""
URL configuration for dashboard app.
"""
from django.urls import path  # type: ignore
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('api/historical-data/', views.get_historical_data, name='historical_data'),
    path('api/forecast/', views.generate_forecast, name='generate_forecast'),
    path('api/product-performance/', views.get_product_performance, name='product_performance'),
]


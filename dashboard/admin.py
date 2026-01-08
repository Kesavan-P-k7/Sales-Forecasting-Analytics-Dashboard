from django.contrib import admin
from .models import SalesData, Forecast, DataUpload

@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'product', 'quantity', 'revenue', 'uploaded_at')
    list_filter = ('date', 'product', 'uploaded_at')
    search_fields = ('product',)
    date_hierarchy = 'date'
    
@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ('forecast_date', 'product', 'predicted_revenue', 'forecast_type', 'created_at')
    list_filter = ('forecast_type', 'forecast_date', 'created_at')
    search_fields = ('product',)
    
@admin.register(DataUpload)
class DataUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'status', 'records_count', 'uploaded_at')
    list_filter = ('status', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


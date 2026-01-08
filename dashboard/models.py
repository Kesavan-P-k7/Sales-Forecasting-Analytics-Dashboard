""" Database models for the Sales Forecasting Dashboard."""
from django.db import models 
from django.core.validators import MinValueValidator  
class SalesData(models.Model):
    
""" Model to store historical sales data uploaded from CSV files. 
    Fields:
    - date: Date of the sale
    - product: Product name
    - quantity: Quantity sold
    - revenue: Revenue generated
    - uploaded_at: Timestamp when data was uploaded """

    date = models.DateField()
    product = models.CharField(max_length=200)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    revenue = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sales_data'
        ordering = ['-date', 'product']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['product']),
            models.Index(fields=['date', 'product']),]
    def __str__(self):
        return f"{self.product} - {self.date} - ${self.revenue}"
class Forecast(models.Model):
    
""" Model to store forecasted sales predictions.
    Fields:
    - forecast_date: Date for which forecast is made
    - product: Product name (null for overall forecast)
    - predicted_revenue: Predicted revenue
    - confidence_lower: Lower bound of confidence interval
    - confidence_upper: Upper bound of confidence interval
    - created_at: Timestamp when forecast was generated
    - forecast_type: Type of forecast (overall, product-wise)"""

    FORECAST_TYPES = [('overall', 'Overall Sales'),('product', 'Product-wise'),] 
    forecast_date = models.DateField()
    product = models.CharField(max_length=200, null=True, blank=True)
    predicted_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    confidence_lower = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    confidence_upper = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPES, default='overall')
    
    class Meta:
        db_table = 'forecasts'
        ordering = ['-forecast_date', 'product']
        indexes = [
            models.Index(fields=['forecast_date']),
            models.Index(fields=['product']),]
    def __str__(self):
        product_str = self.product if self.product else "Overall"
        return f"{product_str} - {self.forecast_date} - ${self.predicted_revenue}"

class DataUpload(models.Model):
    
    """ Model to track CSV file uploads.
    Fields:
    - file_name: Name of the uploaded file
    - uploaded_at: Timestamp when file was uploaded
    - records_count: Number of records imported
    - status: Upload status (success, failed, processing) """
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),]
    
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    records_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'data_uploads'
        ordering = ['-uploaded_at']
    def __str__(self):
        return f"{self.file_name} - {self.status}"


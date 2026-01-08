"""
Views for the Sales Forecasting Dashboard.
"""
import pandas as pd 
import json
from django.shortcuts import render  
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie  
from django.views.decorators.http import require_http_methods 
from .models import SalesData, Forecast, DataUpload
from .utils import clean_and_preprocess_data, generate_arima_forecast, generate_prophet_forecast

@ensure_csrf_cookie
def dashboard(request):
    """Main dashboard view."""
    return render(request, 'dashboard/dashboard.html')

@csrf_exempt
@require_http_methods(["POST"])
def upload_csv(request):
    """
    Handle CSV file upload and import data into database.
    
    Expected CSV format:
    - date: Date in YYYY-MM-DD format
    - product: Product name
    - quantity: Quantity sold (integer)
    - revenue: Revenue amount (decimal)
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        upload_record = DataUpload.objects.create(
            file_name=file_name,
            status='processing' )
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['date', 'product', 'quantity', 'revenue']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            df = clean_and_preprocess_data(df)
            records_created = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    SalesData.objects.create(
                        date=row['date'],
                        product=row['product'],
                        quantity=int(row['quantity']),
                        revenue=float(row['revenue'])
                    )
                    records_created += 1
                except Exception as e:
                    errors.append(f"Row {_ + 2}: {str(e)}")
            
            upload_record.records_count = records_created
            upload_record.status = 'success'
            if errors:
                upload_record.error_message = '; '.join(errors[:10])  # Limit error messages
            upload_record.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully imported {records_created} records',
                'records_count': records_created,
                'errors': errors[:10] if errors else [] })
        except Exception as e:
            upload_record.status = 'failed'
            upload_record.error_message = str(e)
            upload_record.save()
            return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_historical_data(request):
    """
    API endpoint to get historical sales data.
    
    Query parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - product: Filter by product name (optional)
    - group_by: 'day', 'week', 'month' (default: 'day')
    """
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        product = request.GET.get('product')
        group_by = request.GET.get('group_by', 'day')
        
        queryset = SalesData.objects.all()
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if product:
            queryset = queryset.filter(product=product)
                data = list(queryset.values('date', 'product', 'quantity', 'revenue'))
        df = pd.DataFrame(data)
        
        if df.empty:
            return JsonResponse({
                'dates': [],
                'revenue': [],
                'quantity': [],
                'products': []
            })
        
        df['date'] = pd.to_datetime(df['date'])
        if group_by == 'month':
            df['period'] = df['date'].dt.to_period('M').astype(str)
        elif group_by == 'week':
            df['period'] = df['date'].dt.to_period('W').astype(str)
        else:
            df['period'] = df['date'].dt.strftime('%Y-%m-%d')
        
        grouped = df.groupby('period').agg({
            'revenue': 'sum',
            'quantity': 'sum'
        }).reset_index()

        product_data = df.groupby(['period', 'product']).agg({
            'revenue': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        products = df['product'].unique().tolist()
        return JsonResponse({
            'dates': grouped['period'].tolist(),
            'revenue': grouped['revenue'].tolist(),
            'quantity': grouped['quantity'].tolist(),
            'products': products,
            'product_data': product_data.to_dict('records') })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_forecast(request):
    """
    Generate sales forecast using ARIMA or Prophet.
    
    Request body (JSON):
    - method: 'arima' or 'prophet' (default: 'prophet')
    - periods: Number of periods to forecast (default: 30)
    - product: Product name for product-wise forecast (optional)
    - start_date: Start date for training data (optional)
    - end_date: End date for training data (optional)
    """
    try:
        data = json.loads(request.body)
        method = data.get('method', 'prophet')
        periods = int(data.get('periods', 30))
        product = data.get('product', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        
        queryset = SalesData.objects.all()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if product:
            queryset = queryset.filter(product=product)
        
        sales_data = list(queryset.values('date', 'revenue'))
        if not sales_data:
            return JsonResponse({'error': 'No historical data available'}, status=400)
        df = pd.DataFrame(sales_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df = df.groupby('date')['revenue'].sum().reset_index()
        
        if method == 'arima':
            forecast_df = generate_arima_forecast(df, periods)
        else:
            forecast_df = generate_prophet_forecast(df, periods)
        
        forecast_type = 'product' if product else 'overall'
        Forecast.objects.filter(
            forecast_type=forecast_type,
            product=product
        ).delete() 
        
        forecasts = []
        for _, row in forecast_df.iterrows():
            forecast = Forecast.objects.create(
                forecast_date=row['date'].date(),
                product=product,
                predicted_revenue=float(row['forecast']),
                confidence_lower=float(row.get('lower', 0)),
                confidence_upper=float(row.get('upper', 0)),
                forecast_type=forecast_type
            )
            forecasts.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'forecast': float(row['forecast']),
                'lower': float(row.get('lower', 0)),
                'upper': float(row.get('upper', 0))
            })
        
        return JsonResponse({
            'success': True,
            'forecasts': forecasts,
            'method': method
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_product_performance(request):
    """
    Get product-wise performance metrics.
    
    Query parameters:
    - start_date: Start date (optional)
    - end_date: End date (optional)
    """
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        queryset = SalesData.objects.all()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
    
        data = list(queryset.values('product', 'quantity', 'revenue'))
        df = pd.DataFrame(data)
        
        if df.empty:
            return JsonResponse({'products': []})
        
        product_stats = df.groupby('product').agg({
            'revenue': ['sum', 'mean', 'count'],
            'quantity': ['sum', 'mean']
        }).reset_index()
        
        product_stats.columns = ['product', 'total_revenue', 'avg_revenue', 'transactions', 'total_quantity', 'avg_quantity']
        product_stats = product_stats.sort_values('total_revenue', ascending=False)
        products = []
        for _, row in product_stats.iterrows():
            products.append({
                'product': row['product'],
                'total_revenue': float(row['total_revenue']),
                'avg_revenue': float(row['avg_revenue']),
                'transactions': int(row['transactions']),
                'total_quantity': int(row['total_quantity']),
                'avg_quantity': float(row['avg_quantity'])
            })
        
        return JsonResponse({'products': products})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

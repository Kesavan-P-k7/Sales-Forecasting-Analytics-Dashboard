# Sales Forecasting & Analytics Dashboard

A comprehensive web application built with Django, MySQL, HTML, CSS, and JavaScript for sales data analysis and forecasting using time series models (ARIMA and Prophet).

## Features

- **CSV Data Upload**: Upload historical sales data in CSV format
- **Data Cleaning & Preprocessing**: Automatic data cleaning, duplicate removal, and validation
- **Time Series Forecasting**: 
  - ARIMA (AutoRegressive Integrated Moving Average)
  - Facebook Prophet
- **Interactive Dashboard**:
  - Historical sales trends visualization
  - Future sales forecasts with confidence intervals
  - Product-wise performance analysis
  - Filterable data views (by date, product, grouping)
- **Modern UI**: Responsive design with Chart.js visualizations

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js 4.4.0
- **Data Processing**: Pandas, NumPy
- **Forecasting**: Prophet, Statsmodels (ARIMA)

## Project Structure

```
sales_forecast/
├── manage.py
├── requirements.txt
├── README.md
├── sales_forecast/          # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Database and app configuration
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
├── dashboard/               # Main application
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py
│   ├── models.py           # Database models (SalesData, Forecast, DataUpload)
│   ├── views.py            # API endpoints and views
│   ├── urls.py             # App URL routing
│   ├── utils.py            # Forecasting and data processing utilities
│   └── templates/
│       └── dashboard/
│           └── dashboard.html
├── static/                  # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
└── media/                   # Uploaded files (created automatically)
```

## Database Schema

### sales_data Table
- `id`: Primary key
- `date`: Date of sale (DateField)
- `product`: Product name (CharField, max 200)
- `quantity`: Quantity sold (IntegerField)
- `revenue`: Revenue amount (DecimalField)
- `uploaded_at`: Upload timestamp (DateTimeField)

**Indexes**: date, product, (date, product)

### forecasts Table
- `id`: Primary key
- `forecast_date`: Date for forecast (DateField)
- `product`: Product name (nullable for overall forecasts)
- `predicted_revenue`: Predicted revenue (DecimalField)
- `confidence_lower`: Lower confidence bound (DecimalField, nullable)
- `confidence_upper`: Upper confidence bound (DecimalField, nullable)
- `created_at`: Creation timestamp (DateTimeField)
- `forecast_type`: Type ('overall' or 'product')

**Indexes**: forecast_date, product

### data_uploads Table
- `id`: Primary key
- `file_name`: Uploaded file name
- `uploaded_at`: Upload timestamp
- `records_count`: Number of records imported
- `status`: Status ('processing', 'success', 'failed')
- `error_message`: Error details (if failed)

## Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL 5.7+ or MySQL 8.0+
- pip (Python package manager)

### Step 1: Clone/Download the Project

```bash
cd "D:\SALSE forcasting Project"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter issues installing `mysqlclient`:
- **Windows**: Download MySQL client libraries or use `pip install mysqlclient` (may require Visual C++ Build Tools)
- **Linux**: `sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`
- **Mac**: `brew install mysql pkg-config`

### Step 4: Configure MySQL Database

1. Create a MySQL database:
```sql
CREATE DATABASE sales_forecast_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Update database credentials in `sales_forecast/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sales_forecast_db',
        'USER': 'your_mysql_username',  # Change this
        'PASSWORD': 'your_mysql_password',  # Change this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional, for Django Admin)

```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## CSV File Format

The CSV file should have the following columns:

```csv
date,product,quantity,revenue
2024-01-01,Product A,10,500.00
2024-01-02,Product A,15,750.00
2024-01-01,Product B,5,300.00
2024-01-02,Product B,8,480.00
```

**Required Columns**:
- `date`: Date in YYYY-MM-DD format
- `product`: Product name
- `quantity`: Quantity sold (integer)
- `revenue`: Revenue amount (decimal)

A sample CSV file (`sample_sales_data.csv`) is included in the project.

## Usage Guide

### 1. Upload Sales Data

1. Click the "Upload CSV" button
2. Select your CSV file
3. Wait for processing (you'll see a success message with record count)

### 2. View Historical Data

- The dashboard automatically loads historical sales data
- Use filters to:
  - Set date range (start and end dates)
  - Filter by specific product
  - Group data by day, week, or month

### 3. Generate Forecasts

1. Select forecast method (Prophet or ARIMA)
2. Set number of periods to forecast (7-365 days)
3. Click "Generate Forecast"
4. View forecasted values with confidence intervals on the forecast chart

### 4. Analyze Product Performance

- View product-wise revenue and quantity metrics
- See top-performing products in the bar chart
- Review detailed statistics in the product performance table

## API Endpoints

### POST /upload/
Upload CSV file with sales data.

**Request**: Multipart form data with `file` field

**Response**:
```json
{
    "success": true,
    "message": "Successfully imported 100 records",
    "records_count": 100
}
```

### GET /api/historical-data/
Get historical sales data.

**Query Parameters**:
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD
- `product` (optional): Product name
- `group_by` (optional): 'day', 'week', or 'month' (default: 'day')

**Response**:
```json
{
    "dates": ["2024-01-01", "2024-01-02", ...],
    "revenue": [500.00, 750.00, ...],
    "quantity": [10, 15, ...],
    "products": ["Product A", "Product B", ...]
}
```

### POST /api/forecast/
Generate sales forecast.

**Request Body**:
```json
{
    "method": "prophet",  // or "arima"
    "periods": 30,
    "product": "Product A",  // optional
    "start_date": "2024-01-01",  // optional
    "end_date": "2024-12-31"  // optional
}
```

**Response**:
```json
{
    "success": true,
    "forecasts": [
        {
            "date": "2025-01-01",
            "forecast": 750.50,
            "lower": 600.00,
            "upper": 900.00
        },
        ...
    ],
    "method": "prophet"
}
```

### GET /api/product-performance/
Get product performance metrics.

**Query Parameters**:
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

**Response**:
```json
{
    "products": [
        {
            "product": "Product A",
            "total_revenue": 50000.00,
            "avg_revenue": 500.00,
            "total_quantity": 1000,
            "avg_quantity": 10.0,
            "transactions": 100
        },
        ...
    ]
}
```

## Forecasting Models

### Prophet
- **Best for**: Data with seasonal patterns, holidays, and trends
- **Advantages**: Handles missing data well, automatic seasonality detection
- **Requirements**: Minimum 2 data points

### ARIMA
- **Best for**: Stationary time series data
- **Advantages**: Good for short-term forecasts, interpretable
- **Requirements**: Sufficient historical data (recommended: 30+ points)

The system automatically falls back to a simple moving average if advanced models fail.

## Data Cleaning & Preprocessing

The system automatically performs:
1. **Date validation**: Converts dates to datetime format, removes invalid dates
2. **Duplicate removal**: Removes duplicate entries (keeps latest)
3. **Missing value handling**: Fills missing numeric values with 0
4. **Data validation**: Removes negative values for quantity and revenue
5. **Product name cleaning**: Strips whitespace from product names
6. **Sorting**: Sorts data by date

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running: `mysql -u root -p`
- Check credentials in `settings.py`
- Ensure database exists: `CREATE DATABASE sales_forecast_db;`

### Import Errors
- **mysqlclient**: Install MySQL development libraries (see Installation Step 3)
- **Prophet**: May require additional dependencies on some systems

### Forecast Generation Fails
- Ensure sufficient historical data (minimum 2-7 data points recommended)
- Check date range covers enough periods
- Try different forecast methods (Prophet vs ARIMA)

### Static Files Not Loading
- Run: `python manage.py collectstatic` (if using production)
- Check `STATIC_URL` and `STATICFILES_DIRS` in `settings.py`
- Ensure static files are in the `static/` directory

## Development

### Running Tests
```bash
python manage.py test dashboard
```

### Django Admin
Access admin panel at `http://127.0.0.1:8000/admin/` (requires superuser)

### Making Changes
1. Models: After changing models, run `makemigrations` and `migrate`
2. Static files: Changes to CSS/JS are reflected immediately in development
3. Views: Server auto-reloads on code changes

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS` with your domain
3. Change `SECRET_KEY` to a secure random value
4. Configure proper static file serving (e.g., WhiteNoise, Nginx)
5. Use environment variables for sensitive settings
6. Set up proper database backups
7. Use HTTPS for security

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django and MySQL logs
3. Verify CSV file format matches requirements

## Future Enhancements

Potential improvements:
- User authentication and multi-user support
- Export forecasts to CSV/PDF
- Email notifications for forecasts
- Advanced analytics (trend analysis, anomaly detection)
- Machine learning models (LSTM, XGBoost)
- Real-time data updates via API
- Dashboard customization options


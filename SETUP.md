# Quick Setup Guide

## Step-by-Step Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**If mysqlclient installation fails:**

**Windows:**
- Install MySQL Connector/C from MySQL website
- Or use: `pip install mysqlclient` (requires Visual C++ Build Tools)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

**Mac:**
```bash
brew install mysql pkg-config
pip install mysqlclient
```

### 2. Setup MySQL Database

**Option A: Using MySQL Command Line**
```bash
mysql -u root -p
```

Then run:
```sql
CREATE DATABASE sales_forecast_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

**Option B: Using MySQL Workbench**
- Create new database named `sales_forecast_db`
- Set character set to `utf8mb4`
- Set collation to `utf8mb4_unicode_ci`

### 3. Configure Database Settings

Edit `sales_forecast/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sales_forecast_db',
        'USER': 'root',  # Your MySQL username
        'PASSWORD': 'your_password',  # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Create Database Tables

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

### 6. Run the Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and go to:
- **Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Testing the Application

### 1. Upload Sample Data

1. Click "Upload CSV" button
2. Select `sample_sales_data.csv` from the project root
3. Wait for upload confirmation

### 2. View Dashboard

- Historical sales trends will appear automatically
- Product performance metrics will be displayed

### 3. Generate Forecast

1. Select forecast method (Prophet or ARIMA)
2. Set forecast periods (e.g., 30 days)
3. Click "Generate Forecast"
4. View forecasted sales on the chart

## Common Issues & Solutions

### Issue: "Can't connect to MySQL server"
**Solution**: 
- Ensure MySQL service is running
- Check username/password in settings.py
- Verify database exists

### Issue: "No module named 'prophet'"
**Solution**: 
- Install Prophet: `pip install prophet`
- Note: Prophet may take time to install (compiles C++ code)

### Issue: "Static files not loading"
**Solution**: 
- Ensure `static/` folder exists in project root
- Check browser console for 404 errors
- Verify STATIC_URL in settings.py

### Issue: "CSRF verification failed"
**Solution**: 
- Clear browser cache
- Ensure CSRF token is included in forms
- Check Django version compatibility

## Next Steps

1. Upload your own sales data CSV
2. Experiment with different forecast methods
3. Use filters to analyze specific products or date ranges
4. Export data if needed (feature can be added)

## File Structure Checklist

Ensure these files/folders exist:
- ✅ `manage.py`
- ✅ `requirements.txt`
- ✅ `sales_forecast/settings.py`
- ✅ `dashboard/models.py`
- ✅ `dashboard/views.py`
- ✅ `dashboard/utils.py`
- ✅ `dashboard/templates/dashboard/dashboard.html`
- ✅ `static/css/style.css`
- ✅ `static/js/dashboard.js`
- ✅ `sample_sales_data.csv`

## Database Tables Created

After migrations, you should have:
- `sales_data` - Historical sales records
- `forecasts` - Generated forecasts
- `data_uploads` - Upload history
- `django_migrations` - Migration tracking
- `auth_*` - Django authentication tables (if using admin)

## Verification

To verify everything works:
1. ✅ Server starts without errors
2. ✅ Dashboard page loads
3. ✅ Can upload CSV file
4. ✅ Charts display data
5. ✅ Forecast generation works
6. ✅ Product performance table shows data

If all checks pass, you're ready to use the application!


# Quick Start Guide - Sales Forecasting Dashboard

Follow these steps to get your Sales Forecasting Dashboard up and running.

## Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7+ or MySQL 8.0+
- pip (Python package manager)

## Step 1: Install Python Dependencies

Open your terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

**Note**: If `mysqlclient` installation fails:

**Windows:**
- Install MySQL Connector/C from MySQL website, OR
- Install Visual C++ Build Tools, then: `pip install mysqlclient`

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

## Step 2: Create MySQL Database

### Option A: Using MySQL Command Line

1. Open MySQL command line:
```bash
mysql -u root -p
```

2. Enter your MySQL root password when prompted

3. Create the database:
```sql
CREATE DATABASE sales_forecast_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Create a new schema named `sales_forecast_db`
4. Set character set to `utf8mb4` and collation to `utf8mb4_unicode_ci`

## Step 3: Configure Database Settings

Edit `sales_forecast/settings.py` and update the database credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sales_forecast_db',
        'USER': 'root',  # Change to your MySQL username
        'PASSWORD': 'your_password',  # Change to your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**Important**: Replace `'your_password'` with your actual MySQL password!

## Step 4: Create Database Tables

Run Django migrations to create all database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

You should see output like:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, dashboard, sessions
Running migrations:
  ...
```

## Step 5: Create Admin User (Optional)

Create a superuser account to access Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:
- Username
- Email (optional)
- Password (twice)

## Step 6: Start the Development Server

Run the Django development server:

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## Step 7: Access the Application

Open your web browser and navigate to:

- **Main Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Using the Dashboard

### 1. Upload Sales Data

1. Click the **"Upload CSV"** button in the top right
2. Select your CSV file (or use `sample_sales_data.csv` for testing)
3. Wait for the upload confirmation message

**CSV Format Required:**
```csv
date,product,quantity,revenue
2024-01-01,Product A,10,500.00
2024-01-02,Product A,15,750.00
```

### 2. View Historical Data

- Historical sales trends are displayed automatically
- Use filters to:
  - Set **Start Date** and **End Date**
  - Select a specific **Product**
  - Choose **Group By** (Day, Week, or Month)

### 3. Generate Forecasts

1. Select **Forecast Method**:
   - **Prophet**: Best for seasonal patterns
   - **ARIMA**: Good for short-term forecasts
2. Set **Forecast Periods** (7-365 days)
3. Click **"Generate Forecast"**
4. View forecasted sales with confidence intervals on the chart

### 4. Analyze Product Performance

- View product-wise metrics in the bar chart
- Check detailed statistics in the product performance table
- See total revenue, average revenue, quantities, and transaction counts

## Troubleshooting

### Issue: "Can't connect to MySQL server"

**Solution:**
- Ensure MySQL service is running
- Check username/password in `settings.py`
- Verify database exists: `SHOW DATABASES;` in MySQL

### Issue: "No module named 'django'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Static files not loading"

**Solution:**
- Ensure `static/` folder exists in project root
- Check browser console for errors
- Try hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)

### Issue: "CSRF verification failed"

**Solution:**
- Clear browser cache
- Ensure you're accessing via `http://127.0.0.1:8000/`
- Check that CSRF token is included in forms

### Issue: "Forecast generation fails"

**Solution:**
- Ensure you have at least 7-10 data points
- Try different forecast methods
- Check date range covers sufficient historical data

## Sample Data

A sample CSV file (`sample_sales_data.csv`) is included in the project. You can use it to test the application:

1. Click "Upload CSV"
2. Select `sample_sales_data.csv`
3. Wait for import confirmation
4. View charts and generate forecasts

## Next Steps

1. **Upload Your Own Data**: Replace sample data with your actual sales data
2. **Customize Forecasts**: Experiment with different forecast periods and methods
3. **Analyze Products**: Use filters to analyze specific products or date ranges
4. **Export Data**: (Feature can be added) Export forecasts to CSV/PDF

## Stopping the Server

Press `Ctrl+C` (or `Ctrl+Break` on Windows) in the terminal to stop the development server.

## Production Deployment

For production use:
1. Set `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS` with your domain
3. Change `SECRET_KEY` to a secure random value
4. Use a production WSGI server (Gunicorn, uWSGI)
5. Configure proper static file serving
6. Set up HTTPS

## Need Help?

- Check `README.md` for detailed documentation
- Review `COMPONENT_EXPLANATION.md` for code structure
- Check Django logs in terminal for error messages


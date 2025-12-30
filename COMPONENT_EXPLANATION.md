# Component Explanation

This document provides a detailed explanation of each component in the Sales Forecasting & Analytics Dashboard.

## 1. Django Project Structure

### `sales_forecast/` (Main Project Directory)

**`settings.py`**
- **Purpose**: Central configuration file for the Django project
- **Key Settings**:
  - Database configuration (MySQL connection details)
  - Installed apps (includes 'dashboard' app)
  - Static files configuration (CSS, JS, images)
  - Media files configuration (uploaded CSV files)
  - Security settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- **Database**: Configured to use MySQL with connection parameters

**`urls.py`**
- **Purpose**: Main URL routing configuration
- **Routes**:
  - `/admin/` → Django admin interface
  - `/` → Dashboard app URLs
- **Static/Media**: Serves static and media files in development mode

**`wsgi.py` / `asgi.py`**
- **Purpose**: WSGI/ASGI application entry points for deployment
- **Usage**: Used by web servers (Gunicorn, uWSGI) to serve the application

### `manage.py`
- **Purpose**: Django's command-line utility
- **Usage**: Run migrations, start server, create superusers, etc.
- **Commands**: `python manage.py runserver`, `python manage.py migrate`

---

## 2. Dashboard App (`dashboard/`)

### `models.py` - Database Models

**`SalesData` Model**
- **Purpose**: Stores historical sales data from uploaded CSV files
- **Fields**:
  - `date`: Date of sale (DateField)
  - `product`: Product name (CharField, max 200 chars)
  - `quantity`: Quantity sold (IntegerField, min 0)
  - `revenue`: Revenue amount (DecimalField, 12 digits, 2 decimals)
  - `uploaded_at`: Timestamp when record was created
- **Indexes**: Optimized queries on date, product, and date+product combinations
- **Usage**: Primary data storage for all sales transactions

**`Forecast` Model**
- **Purpose**: Stores generated sales forecasts
- **Fields**:
  - `forecast_date`: Date for which forecast is made
  - `product`: Product name (nullable for overall forecasts)
  - `predicted_revenue`: Predicted revenue value
  - `confidence_lower`: Lower bound of confidence interval
  - `confidence_upper`: Upper bound of confidence interval
  - `forecast_type`: 'overall' or 'product' forecast
  - `created_at`: Timestamp when forecast was generated
- **Usage**: Stores forecast results for display on dashboard

**`DataUpload` Model**
- **Purpose**: Tracks CSV file uploads and their status
- **Fields**:
  - `file_name`: Name of uploaded file
  - `uploaded_at`: Upload timestamp
  - `records_count`: Number of records successfully imported
  - `status`: 'processing', 'success', or 'failed'
  - `error_message`: Error details if upload failed
- **Usage**: Audit trail for data imports, helps debug upload issues

### `views.py` - API Endpoints and Views

**`dashboard(request)`**
- **Purpose**: Renders the main dashboard HTML page
- **Returns**: HTML template with dashboard interface
- **CSRF**: Ensures CSRF cookie is set for AJAX requests

**`upload_csv(request)`**
- **Purpose**: Handles CSV file uploads and imports data into database
- **Method**: POST
- **Process**:
  1. Receives uploaded CSV file
  2. Creates DataUpload record with 'processing' status
  3. Reads CSV using pandas
  4. Validates required columns (date, product, quantity, revenue)
  5. Cleans and preprocesses data (via `utils.clean_and_preprocess_data`)
  6. Inserts records into SalesData table
  7. Updates DataUpload status to 'success' or 'failed'
- **Returns**: JSON response with import status and record count
- **Error Handling**: Catches and reports errors for each row

**`get_historical_data(request)`**
- **Purpose**: API endpoint to retrieve historical sales data
- **Method**: GET
- **Query Parameters**:
  - `start_date`: Filter data from this date
  - `end_date`: Filter data until this date
  - `product`: Filter by specific product
  - `group_by`: Aggregate by 'day', 'week', or 'month'
- **Process**:
  1. Queries SalesData model with filters
  2. Converts to pandas DataFrame
  3. Groups data by time period
  4. Aggregates revenue and quantity
  5. Returns JSON with dates, revenue, quantity, and product list
- **Returns**: JSON with time series data for charts

**`generate_forecast(request)`**
- **Purpose**: Generates sales forecasts using ARIMA or Prophet
- **Method**: POST
- **Request Body**:
  - `method`: 'arima' or 'prophet'
  - `periods`: Number of future periods to forecast
  - `product`: Optional product filter
  - `start_date` / `end_date`: Optional date range for training data
- **Process**:
  1. Retrieves historical data based on filters
  2. Converts to time series format
  3. Calls forecasting function (ARIMA or Prophet)
  4. Saves forecasts to Forecast model
  5. Returns forecast data with confidence intervals
- **Returns**: JSON with forecast dates, values, and confidence bounds

**`get_product_performance(request)`**
- **Purpose**: Returns product-wise performance metrics
- **Method**: GET
- **Query Parameters**: `start_date`, `end_date` (optional)
- **Process**:
  1. Queries SalesData with date filters
  2. Groups by product
  3. Calculates aggregates: total/avg revenue, total/avg quantity, transaction count
  4. Sorts by total revenue (descending)
- **Returns**: JSON array of product statistics

### `utils.py` - Data Processing and Forecasting

**`clean_and_preprocess_data(df)`**
- **Purpose**: Cleans and preprocesses raw CSV data
- **Steps**:
  1. Converts date column to datetime format
  2. Removes rows with invalid dates
  3. Removes duplicate entries (keeps latest)
  4. Strips whitespace from product names
  5. Handles missing values (fills with 0)
  6. Removes negative values
  7. Sorts by date
- **Returns**: Cleaned pandas DataFrame
- **Error Handling**: Gracefully handles various data quality issues

**`generate_arima_forecast(df, periods)`**
- **Purpose**: Generates forecast using ARIMA time series model
- **Process**:
  1. Converts DataFrame to time series (daily frequency)
  2. Handles missing values and zeros
  3. Tests multiple ARIMA orders (p, d, q) to find best fit
  4. Selects model with lowest AIC (Akaike Information Criterion)
  5. Generates forecast with confidence intervals
  6. Creates future dates
- **Returns**: DataFrame with forecast dates, values, and confidence bounds
- **Fallback**: Uses simple moving average if ARIMA fails

**`generate_prophet_forecast(df, periods)`**
- **Purpose**: Generates forecast using Facebook Prophet model
- **Process**:
  1. Prepares data in Prophet format (ds, y columns)
  2. Handles zeros and missing values
  3. Configures Prophet with seasonality (yearly, weekly)
  4. Fits model to historical data
  5. Creates future dataframe
  6. Generates predictions with uncertainty intervals
- **Returns**: DataFrame with forecast dates, values, and confidence bounds
- **Advantages**: Handles seasonality, holidays, and missing data well
- **Fallback**: Falls back to ARIMA or simple forecast if Prophet unavailable

**`generate_simple_forecast(df, periods)`**
- **Purpose**: Simple fallback forecasting method
- **Method**: Moving average
- **Process**:
  1. Calculates moving average of recent data
  2. Uses standard deviation for confidence intervals
  3. Projects forward with constant value
- **Returns**: Simple forecast DataFrame
- **Usage**: Used when advanced models fail or insufficient data

### `urls.py` - URL Routing

**Routes**:
- `/` → Dashboard page
- `/upload/` → CSV upload endpoint
- `/api/historical-data/` → Historical data API
- `/api/forecast/` → Forecast generation API
- `/api/product-performance/` → Product metrics API

### `admin.py` - Django Admin Configuration

- **Purpose**: Customizes Django admin interface for models
- **Features**:
  - List display customization
  - Search and filter options
  - Date hierarchy for SalesData
- **Usage**: Access at `/admin/` for data management

---

## 3. Frontend Components

### `templates/dashboard/dashboard.html`

**Structure**:
- **Header**: Title and upload button
- **Upload Modal**: File upload form with CSRF token
- **Stats Cards**: Display total revenue, quantity, products, date range
- **Filters Section**: Date range, product filter, grouping options, forecast settings
- **Charts Section**: Three chart containers (historical, forecast, products)
- **Table Section**: Product performance details table
- **Loading Overlay**: Shows during data processing

**Key Elements**:
- CSRF token for form submissions
- Chart.js canvas elements
- Responsive grid layout
- Font Awesome icons

### `static/css/style.css`

**Design Features**:
- **Color Scheme**: Purple gradient theme (#667eea to #764ba2)
- **Layout**: Responsive grid system
- **Components**:
  - Header with gradient styling
  - Stat cards with hover effects
  - Filter section with organized form elements
  - Chart containers with shadows
  - Data table with hover effects
  - Modal with backdrop blur
  - Loading spinner animation
- **Responsive**: Mobile-friendly breakpoints
- **Typography**: Modern font stack (Segoe UI)

### `static/js/dashboard.js`

**Main Functions**:

**`initializeCharts()`**
- Creates three Chart.js instances:
  - Historical chart (line chart with dual Y-axis)
  - Forecast chart (line chart with confidence intervals)
  - Product chart (bar chart)
- Configures scales, legends, tooltips

**`loadHistoricalData()`**
- Fetches historical data from API
- Updates historical chart
- Updates stat cards (revenue, quantity, products, date range)
- Updates product filter dropdown

**`loadProductPerformance()`**
- Fetches product metrics from API
- Updates product bar chart
- Updates product performance table

**`generateForecast()`**
- Sends forecast request to API
- Combines historical and forecast data
- Updates forecast chart with predictions and confidence intervals

**`applyFilters()`**
- Reloads data when filters change
- Updates all charts and tables

**`setupUploadForm()`**
- Handles CSV file upload
- Shows loading indicator
- Displays success/error messages
- Reloads data after successful upload

**Utility Functions**:
- `formatCurrency()`: Formats numbers as currency
- `formatNumber()`: Formats numbers with commas
- `showNotification()`: Displays status messages
- `showLoading()` / `hideLoading()`: Loading overlay control

---

## 4. Database Schema

### MySQL Tables

**`sales_data`**
```sql
CREATE TABLE sales_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    product VARCHAR(200) NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    revenue DECIMAL(12, 2) NOT NULL CHECK (revenue >= 0),
    uploaded_at DATETIME NOT NULL,
    INDEX idx_date (date),
    INDEX idx_product (product),
    INDEX idx_date_product (date, product)
);
```

**`forecasts`**
```sql
CREATE TABLE forecasts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    forecast_date DATE NOT NULL,
    product VARCHAR(200) NULL,
    predicted_revenue DECIMAL(12, 2) NOT NULL,
    confidence_lower DECIMAL(12, 2) NULL,
    confidence_upper DECIMAL(12, 2) NULL,
    created_at DATETIME NOT NULL,
    forecast_type VARCHAR(20) NOT NULL,
    INDEX idx_forecast_date (forecast_date),
    INDEX idx_product (product)
);
```

**`data_uploads`**
```sql
CREATE TABLE data_uploads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    uploaded_at DATETIME NOT NULL,
    records_count INT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    error_message TEXT NULL
);
```

---

## 5. Data Flow

### Upload Flow
1. User selects CSV file → JavaScript captures file
2. FormData created → Sent via AJAX POST to `/upload/`
3. Django receives file → Creates DataUpload record
4. Pandas reads CSV → Validates columns
5. Data cleaning → `clean_and_preprocess_data()`
6. Database insert → SalesData records created
7. Response sent → Success message displayed
8. Dashboard reloads → New data appears in charts

### Forecast Flow
1. User clicks "Generate Forecast" → JavaScript collects parameters
2. AJAX POST to `/api/forecast/` → Method, periods, filters sent
3. Django queries historical data → Filters by date/product
4. Data converted to time series → Pandas DataFrame
5. Forecasting function called → ARIMA or Prophet
6. Forecasts saved to database → Forecast model
7. JSON response → Forecast data returned
8. Chart updated → Historical + forecast displayed

### Display Flow
1. Page loads → `loadHistoricalData()` called
2. API request → `/api/historical-data/` with filters
3. Database query → SalesData filtered and aggregated
4. JSON response → Dates, revenue, quantity arrays
5. Chart.js update → Charts rendered
6. Stats updated → Cards show totals

---

## 6. Forecasting Models Explained

### ARIMA (AutoRegressive Integrated Moving Average)
- **Components**:
  - **AR (p)**: Uses p previous values
  - **I (d)**: Differencing to make data stationary
  - **MA (q)**: Uses q previous forecast errors
- **Order Selection**: Tests combinations to find best (p,d,q)
- **Best For**: Stationary time series, short-term forecasts
- **Limitations**: Requires sufficient data, assumes stationarity

### Prophet (Facebook)
- **Components**:
  - Trend component (linear or logistic growth)
  - Seasonal components (yearly, weekly, daily)
  - Holiday effects
- **Advantages**: Handles missing data, outliers, seasonality automatically
- **Best For**: Business time series with seasonality
- **Limitations**: Requires more computational resources

### Simple Moving Average (Fallback)
- **Method**: Average of recent values
- **Usage**: When advanced models fail or insufficient data
- **Confidence**: Based on historical standard deviation

---

## 7. Security Considerations

- **CSRF Protection**: CSRF tokens in forms and AJAX requests
- **Input Validation**: Server-side validation of CSV data
- **SQL Injection**: Django ORM prevents SQL injection
- **File Upload**: Validates file type and size
- **Error Handling**: Graceful error handling without exposing internals

---

## 8. Performance Optimizations

- **Database Indexes**: Indexed on date, product, and combinations
- **Query Optimization**: Aggregations done in database/DataFrame
- **Caching**: Can be added for frequently accessed forecasts
- **Lazy Loading**: Charts load data on demand
- **Pagination**: Can be added for large datasets

---

## Summary

This application follows a clean architecture:
- **Backend**: Django handles data processing, API endpoints, database operations
- **Frontend**: HTML/CSS/JS provides interactive user interface
- **Database**: MySQL stores all data efficiently
- **Forecasting**: Python libraries (Prophet, ARIMA) provide predictions
- **Visualization**: Chart.js renders interactive charts

Each component has a specific responsibility, making the codebase maintainable and extensible.


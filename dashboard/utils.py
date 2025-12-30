"""
Utility functions for data processing and forecasting.
"""
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet  # type: ignore
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA  # type: ignore
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False


def clean_and_preprocess_data(df):
    """
    Clean and preprocess the uploaded CSV data.
    
    Steps:
    1. Remove duplicates
    2. Handle missing values
    3. Convert date column to datetime
    4. Remove invalid data (negative values, etc.)
    5. Sort by date
    """
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Remove rows with invalid dates
    df = df.dropna(subset=['date'])
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['date', 'product'], keep='last')
    
    # Clean product names (remove extra whitespace)
    df['product'] = df['product'].astype(str).str.strip()
    
    # Handle missing values
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
    
    # Remove negative values
    df = df[(df['quantity'] >= 0) & (df['revenue'] >= 0)]
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    return df


def generate_arima_forecast(df, periods=30):
    """
    Generate forecast using ARIMA model.
    
    Parameters:
    - df: DataFrame with 'date' and 'revenue' columns
    - periods: Number of periods to forecast
    
    Returns:
    - DataFrame with 'date', 'forecast', 'lower', 'upper' columns
    """
    if not ARIMA_AVAILABLE:
        raise ImportError("statsmodels is not installed. Please install it: pip install statsmodels")
    
    # Prepare data
    df = df.copy()
    df = df.set_index('date')
    df = df.asfreq('D', fill_value=0)  # Fill missing dates with 0
    
    # Use revenue as the time series
    ts = df['revenue']
    
    # Remove zeros or handle them
    ts = ts.replace(0, np.nan).interpolate(method='linear')
    ts = ts.fillna(ts.mean() if ts.mean() > 0 else 1)
    
    # Fit ARIMA model (auto-select order)
    try:
        # Try different ARIMA orders
        best_aic = np.inf
        best_order = (1, 1, 1)
        
        for p in range(3):
            for d in range(2):
                for q in range(3):
                    try:
                        model = ARIMA(ts, order=(p, d, q))
                        fitted_model = model.fit()
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        model = ARIMA(ts, order=best_order)
        fitted_model = model.fit()
        
        # Generate forecast
        forecast = fitted_model.forecast(steps=periods)
        conf_int = fitted_model.get_forecast(steps=periods).conf_int()
        
        # Create future dates
        last_date = df.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq='D')
        
        # Create result DataFrame
        result_df = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast.values,
            'lower': conf_int.iloc[:, 0].values,
            'upper': conf_int.iloc[:, 1].values
        })
        
        return result_df
        
    except Exception as e:
        # Fallback to simple moving average
        return generate_simple_forecast(df, periods)


def generate_prophet_forecast(df, periods=30):
    """
    Generate forecast using Facebook Prophet model.
    
    Parameters:
    - df: DataFrame with 'date' and 'revenue' columns
    - periods: Number of periods to forecast
    
    Returns:
    - DataFrame with 'date', 'forecast', 'lower', 'upper' columns
    """
    if not PROPHET_AVAILABLE:
        # Fallback to ARIMA if Prophet not available
        if ARIMA_AVAILABLE:
            return generate_arima_forecast(df, periods)
        else:
            return generate_simple_forecast(df, periods)
    
    # Prepare data for Prophet (requires 'ds' and 'y' columns)
    prophet_df = df[['date', 'revenue']].copy()
    prophet_df.columns = ['ds', 'y']
    
    # Remove zeros or handle them
    prophet_df['y'] = prophet_df['y'].replace(0, np.nan)
    prophet_df = prophet_df.dropna()
    
    if len(prophet_df) < 2:
        return generate_simple_forecast(df, periods)
    
    # Fit Prophet model
    try:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        model.fit(prophet_df)
        
        # Create future dates
        future = model.make_future_dataframe(periods=periods)
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Extract only future forecasts
        forecast_future = forecast.tail(periods)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        
        # Create result DataFrame
        result_df = pd.DataFrame({
            'date': forecast_future['ds'],
            'forecast': forecast_future['yhat'],
            'lower': forecast_future['yhat_lower'],
            'upper': forecast_future['yhat_upper']
        })
        
        return result_df
        
    except Exception as e:
        # Fallback to simple forecast
        return generate_simple_forecast(df, periods)


def generate_simple_forecast(df, periods=30):
    """
    Generate simple forecast using moving average (fallback method).
    
    Parameters:
    - df: DataFrame with 'date' and 'revenue' columns
    - periods: Number of periods to forecast
    
    Returns:
    - DataFrame with 'date', 'forecast', 'lower', 'upper' columns
    """
    df = df.copy()
    df = df.set_index('date')
    
    # Calculate moving average
    window = min(7, len(df))
    ma = df['revenue'].rolling(window=window).mean().iloc[-1]
    
    # Use last value if MA is NaN
    if pd.isna(ma):
        ma = df['revenue'].iloc[-1] if len(df) > 0 else 0
    
    # Create future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq='D')
    
    # Calculate standard deviation for confidence intervals
    std_dev = df['revenue'].std() if len(df) > 1 else ma * 0.1
    
    # Create result DataFrame
    result_df = pd.DataFrame({
        'date': future_dates,
        'forecast': [ma] * periods,
        'lower': [max(0, ma - 1.96 * std_dev)] * periods,
        'upper': [ma + 1.96 * std_dev] * periods
    })
    
    return result_df


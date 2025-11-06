import yfinance as yf
import pandas as pd
import numpy as np
import json
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score

# --- 1. Configuration ---

# We use 7 days of lag to predict the next day
LAG_DAYS = 7

# List of stocks to train. Replaced OpenAI with Tesla (TSLA).
STOCKS = {
    "Google": "GOOGL",
    "NVIDIA": "NVDA",
    "Citi": "C",
    "Reliance Industries": "RELIANCE.NS",
    "HCL India": "HCLTECH.NS",
    "Tesla": "TSLA"
}

# Models to train
MODELS = {
    "Linear Regression": LinearRegression(),
    "Lasso Regression": Lasso(),
    "Ridge Regression": Ridge(),
    "SVM Regression": SVR(),
    "Decision Tree": DecisionTreeRegressor(),
    "XGBoost": XGBRegressor(objective='reg:squarederror')
}

# --- 2. Feature Engineering ---

def create_features(data):
    """Creates lag features from the 'Close' price."""
    df = data[['Close']].copy()
    
    for i in range(1, LAG_DAYS + 1):
        df[f'lag_{i}'] = df['Close'].shift(i)
        
    # The 'target' is the price we want to predict
    df['target'] = df['Close'].shift(-1)
    
    # Drop rows with NaN values created by shifting
    df = df.dropna()
    
    # Separate features (X) from target (y)
    features = [f'lag_{i}' for i in range(1, LAG_DAYS + 1)]
    X = df[features]
    y = df['target']
    
    # Return features in the correct order (oldest to newest)
    # This is CRITICAL for prediction later
    return X[features[::-1]], y

# --- 3. Training Function ---

def train_stock(ticker):
    """Fetches data, trains all models, and saves the best one."""
    print(f"\n--- Training models for {ticker} ---")
    
    # Download 1.5 years of data to ensure we have 1 year after feature creation
    data = yf.download(ticker, period="18mo", interval="1d")
    
    if data.empty:
        print(f"Could not download data for {ticker}. Skipping.")
        return None
        
    X, y = create_features(data)
    
    if X.empty or y.empty:
        print(f"Not enough data to create features for {ticker}. Skipping.")
        return None
        
    # Split data: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    stock_performance = {}
    best_model_obj = None
    best_mse = float('inf')
    best_model_name = ""

    for name, model in MODELS.items():
        try:
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            preds = model.predict(X_test)
            
            # Evaluate model
            mse = mean_squared_error(y_test, preds)
            r2 = r2_score(y_test, preds)
            
            print(f"  {name}: MSE={mse:.4f}, R2={r2:.4f}")
            
            stock_performance[name] = {'mse': mse, 'r2': r2}
            
            # Check if this is the best model so far
            if mse < best_mse:
                best_mse = mse
                best_model_obj = model
                best_model_name = name
                
        except Exception as e:
            print(f"Failed to train {name} for {ticker}. Error: {e}")
            
    # Save the best model to disk
    if best_model_obj:
        print(f"  Best model for {ticker} is: {best_model_name} (MSE={best_mse:.4f})")
        model_filename = f"models/{ticker}_best_model.pkl"
        joblib.dump(best_model_obj, model_filename)
        print(f"  Saved best model to {model_filename}")
        
        # Add details about the best model
        stock_performance['best_model'] = {
            'name': best_model_name,
            'mse': best_mse,
            'r2': stock_performance[best_model_name]['r2'],
            'filename': model_filename
        }
                                
    return stock_performance

# --- 4. Main Execution ---

if __name__ == "__main__":
    
    # Create /models directory if it doesn't exist
    if not os.path.exists("models"):
        os.makedirs("models")
        
    all_model_performance = {}
    
    for pretty_name, ticker in STOCKS.items():
        performance = train_stock(ticker)
        if performance:
            all_model_performance[ticker] = performance
            
    # Save performance metrics to a JSON file
    with open("model_performance.json", "w") as f:
        json.dump(all_model_performance, f, indent=4)
        
    print("\n--- All training complete! ---")
    print("Model performance saved to model_performance.json")
    print("Best models saved to /models directory.")
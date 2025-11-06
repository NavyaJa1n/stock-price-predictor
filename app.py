import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import json
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Load the performance file to find model paths
try:
    with open("model_performance.json", "r") as f:
        model_performance = json.load(f)
except FileNotFoundError:
    print("FATAL ERROR: model_performance.json not found.")
    print("Please run train.py first!")
    exit()

# Load all the best models into memory
loaded_models = {}
for ticker, data in model_performance.items():
    if 'best_model' in data:
        filename = data['best_model']['filename']
        try:
            loaded_models[ticker] = joblib.load(filename)
            print(f"Successfully loaded model for {ticker} from {filename}")
        except FileNotFoundError:
            print(f"Warning: Model file {filename} not found for {ticker}.")

# --- 2. Define API Endpoints ---

@app.route('/')
def home():
    """Serves the main index.html file."""
    # Flask looks for files inside the /templates folder
    return render_template('index.html')

@app.route('/get_stock_data')
def get_stock_data():
    """Fetches historical data for the chart."""
    ticker = request.args.get('ticker')
    period = request.args.get('period', '1mo')  # Default to 1 month
    
    if not ticker or ticker not in loaded_models:
        return jsonify({"error": "Invalid ticker"}), 400

    try:
        data = yf.download(ticker, period=period, interval="1d")
        if data.empty:
            return jsonify({"error": "No data found for ticker"}), 404

        # ✅ Fix: Flatten multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # ✅ Now each column is a simple Series
        chart_data = {
            "dates": data.index.strftime('%Y-%m-%d').tolist(),
            "close_prices": data['Close'].to_list(),
            "open_prices": data['Open'].to_list(),
            "high_prices": data['High'].to_list(),
            "low_prices": data['Low'].to_list()
        }
        return jsonify(chart_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. NEW PREDICTION ENDPOINT ---
#
# THIS IS THE MISSING PIECE.
# Your app.js sends a POST request to /predict, and this
# function will now catch it.
#
# In app.py

@app.route('/predict', methods=['POST'])
def predict():
    """Receives data and uses a loaded model to make a prediction."""
    
    try:
        # 1. Get the data sent from app.js
        data = request.json
        ticker = data.get('ticker')
        recent_data = data.get('recent_data')

        # 2. Validation
        if not ticker or ticker not in loaded_models:
            return jsonify({"error": f"No model loaded for ticker: {ticker}"}), 400
        
        if not recent_data or len(recent_data) != 7:
            return jsonify({"error": "Prediction requires exactly 7 days of recent_data."}), 400

        # 3. Load the correct model from memory
        model = loaded_models[ticker]
        
        # --- ⬇️ FINAL FIX START ⬇️ ---

        # 4. Get the model's technique name from the performance JSON
        # Find the 'best_model' dictionary for the given ticker
        model_info = model_performance.get(ticker, {}).get('best_model', {})
        
        # Get the value from the "name" key (e.g., "Linear Regression")
        model_name = model_info.get('name', 'Unknown Model') 

        # --- ⬆️ FINAL FIX END ⬆️ ---

        # 5. Format data for prediction
        features = np.array(recent_data).reshape(1, -1)

        # 6. Make prediction
        prediction = model.predict(features)
        
        # 7. Extract the single value and send it back
        predicted_price = prediction[0]
        
        # 8. Return both the price and the correct model name
        return jsonify({
            "predicted_price": predicted_price,
            "model_name": model_name  # <-- This will now be "Linear Regression" etc.
        })

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

# --- 4. Run the App ---

if __name__ == "__main__":
    print("Starting Flask server... Access your UI at http://127.0.0.1:5000")
    # debug=True reloads server on code changes
    app.run(debug=True, port=5000)
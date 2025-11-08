# 📈 ML Stock Market Predictor

A **full-stack web application** that challenges you to predict future stock prices and compares your intuition against a trained machine learning model.

This project fetches **real-time stock data**, runs it through a pre-trained ML model, and hosts a **web-based game** for you to play.

---

## 🚀 Live Demo

➡️ **[View the Live Demo Here](https://stock-price-predictor-qhi6.onrender.com)**  
Note: If it doesn't work the first time, try loading it on another tab.

---

## 🌟 Key Features

- 🤖 **Human vs. Machine** — Pit your own intuition against a trained ML model. The app calculates who was closer to the actual price.  
- 📊 **Real-Time Data** — Fetches up-to-the-minute stock data directly from the **Yahoo Finance (yfinance)** API.  
- 🧠 **Intelligent Model Training** — `train.py` automatically trains six different regression models (from Linear Regression to XGBoost) and selects the best-performing one for each stock.  
- 🌐 **Full-Stack Application** — A complete, self-contained project with a **Python/Flask backend** and an **HTML/JavaScript frontend**.  
- 💅 **Interactive UI** — A clean, responsive user interface built with **Tailwind CSS** and an interactive graph powered by **Chart.js**.

---

## 🏗️ How It Works: The Architecture

This project is built in **three main parts**. Understanding this flow is key to understanding the app.

---

### 1️⃣ Part 1: The Model Trainer (`train.py`)

This is the “study session” for our app — an offline script you run before starting the server.

- 📥 **Fetches Data:** Downloads 3 months of historical data for each stock (e.g., `GOOGL`, `NVDA`, `TSLA`).  
- 🧩 **Creates Features:** Uses “lag features,” teaching the model to look at prices from the last 7 days (`lag_1`, `lag_2`, …) to predict the next day’s price.  
- 🏋️ **Trains & Competes:** Trains 6 different ML models (Linear Regression, Lasso, Random Forest, XGBoost, etc.).  
- 🏆 **Saves the Best:** Finds the model with the lowest MSE (Mean Squared Error) and saves it as a `.pkl` file in `/models/`. It also records results in `model_performance.json`.

---

### 2️⃣ Part 2: The Backend API (`app.py`)

This is the **brain** of the application — a Flask server that runs continuously.

- 🌐 **Serves the Website:** Sends your browser `index.html`, `app.js`, and other static files.  
- ⚙️ **Provides a Data API:**
  - `/get_stock_data` → Fetches fresh live data from Yahoo Finance for the chart.  
  - `/predict` → When you click “Reveal,” it sends the last 7 days of data to the server, which uses the correct `.pkl` model to predict the next price.

---

### 3️⃣ Part 3: The Frontend (`index.html` & `static/app.js`)

This is the **face** of the app — what users interact with in the browser.

- 🧱 **Renders the UI:** `index.html` builds the structure; **Tailwind CSS** makes it clean and responsive.  
- 🧭 **Handles Interaction:** `app.js` controls logic and user flow.
  - Calls `/get_stock_data` to draw the chart using **Chart.js**.  
  - Hides the last day’s price to create the “challenge.”  
  - When “Reveal Results” is clicked, it calls `/predict`.  
  - Finally, it compares your guess, the model’s prediction, and the actual price to declare a winner.

---

## 💻 Technology Stack

| Layer | Technologies |
|-------|---------------|
| **Backend** | Python, Flask, Gunicorn |
| **Frontend** | HTML5, Tailwind CSS, JavaScript (ES6+), Chart.js |
| **Data & ML** | Pandas, NumPy, Scikit-learn, XGBoost, Joblib, yfinance |
| **Deployment** | Render |

---

## 📂 Project Structure

```
market-predictor/
├── app.py                  # The main Flask API server
├── train.py                # Offline model trainer script
├── requirements.txt        # Python dependencies for deployment
├── model_performance.json  # Reports best model per stock
├── .gitignore              # Files to ignore in Git
│
├── models/                 # Trained ML models (.pkl)
│   ├── GOOGL_best_model.pkl
│   ├── NVDA_best_model.pkl
│   └── ...
│
├── static/                 # Frontend JavaScript
│   └── app.js
│
└── templates/              # Frontend HTML
    └── index.html
```

---

## ⚙️ How to Run Locally

### 🧩 Prerequisites
- Python 3.7+
- `pip` (Python package manager)
- Git

---

### 🪜 Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Train Your Models (Crucial Step!)
Run the following script to train and save models locally:
```bash
python train.py
```
This will:
- Fetch recent stock data
- Train multiple models
- Save the best model for each stock in `/models/`

You’ll see progress and performance stats printed to your terminal.

#### 4. Run the Flask Server
```bash
python app.py
```

#### 5. View the App
Open your browser and visit:
```
http://127.0.0.1:5000
```
Your stock predictor game should now be running locally 🎉

---

## ☁️ Deployment (Render)

This app can be deployed on **Render** as a “Web Service.”

### ✅ Configuration

- **Environment:** `Python 3`
- **Build Command:**  
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**  
  ```bash
  gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app
  ```

### 📝 Notes
- `--bind 0.0.0.0:$PORT` is required by Render to correctly route traffic.  
- `--timeout 120` ensures the app loads properly (since ML models may take time to initialize).

---

## 🧠 Future Improvements

- Add more stocks and dynamic model loading  
- Integrate deep learning (LSTM) models for improved predictions  
- Add user authentication and leaderboards  
- Support mobile layout optimizations
- Perform Hyper-parameter tuning

---

## 🏁 Author
💼 GitHub: [@navyaja1n](https://github.com/navyaja1n)  
---

⭐ If you like this project, consider giving it a **star** on GitHub!  
It helps others discover it and motivates further development. 🌟

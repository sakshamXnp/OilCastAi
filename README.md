# OilCast AI 🛢️
### Advanced Energy Market Prediction & Intelligence Platform

**OilCast AI** is a state-of-the-art predictive analytics platform designed to forecast global crude oil prices. By leveraging a multi-model Machine Learning architecture, the platform integrates historical technical data with real-world economic indicators, geopolitical signals, and news sentiment to provide actionable market intelligence.

---

## 🚀 Key Features

*   **📈 Real-Time Market Ticker:** Live tracking of global benchmarks (WTI, Brent, Arab Light) with dynamic volatility indicators.
*   **🤖 Hybrid AI Forecasting:** Combines **ARIMA**, **LSTM (Long Short-Term Memory)**, **XGBoost**, and **Transformer** models for short-term (7d), medium-term (30d), and long-term (90d) price predictions.
*   **🔍 Explainable AI (XAI):** Transparent prediction logic that highlights influencing factors such as OPEC+ decisions, SPR levels, and USD strength.
*   **📰 Sentiment Intelligence:** Automated news scraping and sentiment analysis of energy-sector headlines.
*   **📊 Performance Metrics:** Built-in validation suite calculating **RMSE**, **MAE**, and **MAPE** to ensure forecast reliability.
*   **💻 Modern Dashboard:** A high-performance, responsive UI built with Next.js and Tailwind CSS for a professional trading experience.

---

## 🛠️ Technical Architecture

*   **Frontend:** Next.js 14, React, Tailwind CSS (Glassmorphism UI).
*   **Backend:** FastAPI (Python), Uvicorn.
*   **Database:** SQLite (local-first storage for high-speed indexing).
*   **ML Engine:** TensorFlow, Scikit-learn, XGBoost, Pandas.
*   **Data Pipeline:** Yahoo Finance API integration for automated daily synchronization.

---

## Prerequisites
- [Node.js v18+](https://nodejs.org/)
- [Python 3.10+](https://www.python.org/)

## 1. Setup Backend (Machine Learning & API)

Open a terminal and navigate to the backend folder:
```bash
cd e:/Oil/oilcast-ai/backend
```

Create a virtual environment and install dependencies:
```bash
python -m venv venv
# On Windows, activate the virtual environment:
.\venv\Scripts\activate
# Install requirements
pip install -r requirements.txt
```

Initialize the Database and ML Models (this will download Yahoo Finance data and train the AI models):
```bash
# On Windows PowerShell:
$env:PYTHONPATH="."
python scripts/init_data.py
```

Run the FastAPI Server:
```bash
uvicorn main:app --reload --port 3001
```
*The API is now running at http://localhost:3001*

---

## 2. Setup Frontend (Dashboard UI)

Open a **new** terminal and navigate to the frontend folder:
```bash
cd e:/Oil/oilcast-ai/frontend
```

Install Node dependencies and start the Next.js server:
```bash
npm install
npm run dev
```

*The Dashboard is now running at **http://localhost:3000***

---

## 3. Persistent Execution (Background Mode)

To keep the servers running even after closing your terminal or the Antigravity tool, use the provided PowerShell script:

1.  Open PowerShell in the project root.
2.  Run the following command:
    ```powershell
    .\start_oilcast.ps1
    ```
3.  This will launch both the backend and frontend in minimized background windows. You can then safely close the main terminal.

---

## 4. Troubleshooting
-   **Port 3001**: The backend is now configured to run on port 3001. If you need to change this, update `.env` and `frontend/.env.local`.
-   **Database**: This version uses a local SQLite database (`oilcast.db`).

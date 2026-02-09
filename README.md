# 🇳🇬 Nigeria Retail Sales Predictor

A full-stack AI application that forecasts daily sales volume and revenue for retail stores across Nigeria. This tool combines a machine learning model (XGBoost) with a geospatial logic layer to provide realistic business intelligence for all 36 Nigerian States + FCT.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95-green)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![PWA](https://img.shields.io/badge/PWA-Ready-orange)

## 🚀 Overview

This project solves the "Cold Start" problem in retail forecasting. It uses a model trained on historical data from major commercial hubs and uses **Inference Mapping** to scale those insights to new regions.

**Key Features:**
* **AI-Powered Forecasts:** Uses XGBoost to detect seasonality, holiday trends, and oil price impact.
* **Nationwide Coverage:** Maps all 36 Nigerian states to specific economic tiers (Tier 1 Giants to Tier 4 Emerging Markets).
* **Revenue Estimation:** Converts raw unit predictions into **Naira (₦)** revenue using a 2017-adjusted price list.
* **Progressive Web App (PWA):** Can be installed on Android/iOS devices and works offline (caching the UI).
* **Database Logging:** Automatically saves every prediction to a PostgreSQL database for audit and analysis.

## 🛠️ Tech Stack

* **Frontend:** HTML5, Bootstrap 5, Jinja2 Templates (Server-Side Rendering).
* **Backend:** Python, FastAPI.
* **Machine Learning:** XGBoost, Scikit-Learn, Pandas.
* **Database:** PostgreSQL (via SQLAlchemy).
* **Infrastructure:** Docker & Docker Compose.

---

## 📋 Prerequisites

To run this project locally, you only need **one** tool installed:

* **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Windows/Mac/Linux)

*No local Python or Postgres installation is required. Docker handles everything.*

---

## ⚡ Quick Start (Local)

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/nigeria-sales-predictor.git](https://github.com/YOUR_USERNAME/nigeria-sales-predictor.git)
    cd nigeria-sales-predictor
    ```

2.  **Run with Docker Compose**
    This command builds the Python container, sets up the Database, and connects them.
    ```bash
    docker-compose up --build
    ```

3.  **Access the App**
    Open your browser and go to:
    👉 **[http://localhost:8000](http://localhost:8000)**

4.  **Stop the App**
    Press `Ctrl+C` in your terminal or run `docker-compose down`.

---

## 📱 How to Use the App

### 1. The Inputs
The dashboard requires four key business inputs to generate a forecast:

| Input Field | Description | Impact on AI |
| :--- | :--- | :--- |
| **Prediction Date** | The specific day you want to forecast. | Triggers seasonality logic (e.g., December dates spike sales; Sundays might dip). |
| **Store Location** | Select any of the 36 States + FCT. | Maps the state to an "Economic Tier." (e.g., Lagos/Kano = High Volume, Zamfara = Lower Volume). |
| **Product Category** | The family of goods (e.g., `HOME CARE`, `BEVERAGES`). | Determines the base price and typical sales volume (e.g., Bread sells more units than Electronics). |
| **Promotional Status** | Are items on sale? | **No Promotion:** Standard sales.<br>**Active Promotion:** ~10 items on sale.<br>**High Intensity:** Black Friday levels (massive spike). |

### 2. The Output
The model generates two numbers:
* **Projected Revenue (₦):** The estimated cash flow for that specific category in that state for the day.
* **Unit Breakdown:** The estimated number of items sold (e.g., "1,200 units").

---

## 📂 Project Structure

```text
├── main.py                  # The Brain: FastAPI backend, Logic Layer, and DB connection
├── nigeria_sales_model.pkl  # The AI: Pre-trained XGBoost model
├── encoders.pkl             # The Translator: Maps text labels to model numbers
├── stores_nigeria.csv       # The Map: logic linking States to Economic Tiers
├── requirements.txt         # Python dependencies
├── Dockerfile               # Blueprint for the App container
├── docker-compose.yml       # Orchestrator for App + Database
├── templates/
│   └── index.html           # The Face: User Interface
└── static/
    ├── manifest.json        # PWA Identity file
    ├── service-worker.js    # PWA Offline logic
    └── icon-192.png         # App Icons

💾 Database Inspection
Every prediction is saved to a PostgreSQL container. To view the history:

Option A: Command Line

Bash
# 1. Enter the database container
docker exec -it <container_name> psql -U sales_user -d sales_db

# 2. Run SQL query
SELECT * FROM prediction_history;
Option B: GUI Tool (DBeaver/TablePlus) Connect using these credentials (exposed on port 5432):

Host: localhost

Port: 5432

User: sales_user

Password: sales_password

Database: sales_db

🌍 Mobile Installation (Android/iOS)
This app is a Progressive Web App (PWA).

Open the app in Chrome (Android) or Safari (iOS).

Tap the menu (⋮ or Share icon).

Select "Add to Home Screen" or "Install App".

It will appear as a native app on your device.

🤝 Contributing
Fork the repository.

Create a feature branch (git checkout -b feature/NewFeature).

Commit your changes.

Push to the branch and open a Pull Request.

📄 License
This project is open-source and available under the MIT License.
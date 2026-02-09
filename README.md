
---
title: Nigeria Sales Predictor
emoji: 📈
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
app_port: 7860
---

# 🇳🇬 Nigeria Retail Sales Predictor

**A Full-Stack AI Forecasting Tool for Emerging Markets.**

This application predicts daily sales volume and revenue for retail stores across all 36 Nigerian States + FCT. It combines a robust **XGBoost** machine learning model with a **Geospatial Logic Layer** to provide realistic business intelligence for regions with sparse data.

### 🚀 **[View Live Demo on Hugging Face](https://huggingface.co/spaces/YOUR_USERNAME/nigeria-sales-predictor)**

---

## 🏗️ Architecture & Features

This project solves the **"Cold Start"** problem in African retail. It trains on data from major commercial hubs (Lagos, Kano) and uses **Inference Mapping** to scale insights to developing regions.

* **🧠 AI-Powered Forecasts:** XGBoost model detecting seasonality, oil price correlations, and holiday spikes.
* **⚡ Lazy Loading & Memory Optimization:** Uses `mmap` and Just-In-Time loading to run heavy 180MB models on lightweight cloud containers.
* **☁️ Cloud-Native Database:** Connects to a serverless **Neon PostgreSQL** database for real-time logging of every prediction.
* **📱 Mobile Ready:** Functions as a **Progressive Web App (PWA)** and can be wrapped into a native Android APK.
* **🗺️ Tiered Economic Mapping:** Automatically maps user-selected states to economic tiers (Tier 1 Giants vs. Tier 4 Emerging Markets).
* **💰 Revenue Estimation:** Converts raw unit predictions into **Naira (₦)** revenue using a 2017-adjusted price list.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, Bootstrap 5, Jinja2 (Server-Side Rendering).
* **Backend:** Python, FastAPI (High-performance Async API).
* **Machine Learning:** XGBoost, Scikit-Learn, Joblib (Compressed).
* **Database:** PostgreSQL (Production: **Neon**, Local: **Docker Container**).
* **DevOps:** Docker, Git LFS (Large File Storage), Hugging Face Spaces.

---

## ⚡ Quick Start (Local Development)

To run this on your laptop, you only need **Docker Desktop**.

**1. Clone the Repository**
```bash
git clone [https://github.com/YOUR_USERNAME/nigeria-sales-predictor.git](https://github.com/YOUR_USERNAME/nigeria-sales-predictor.git)
cd nigeria-sales-predictor

```

**2. Initialize Git LFS (Crucial)**
This pulls the actual 180MB model file instead of the pointer.

```bash
git lfs install
git lfs pull

```

**3. Run with Docker Compose**
This builds the Python app and spins up a local Postgres database automatically.

```bash
docker-compose up --build

```

**4. Access the App**
👉 Open **http://localhost:8000** in your browser.

---

## ☁️ Deployment (Hugging Face Spaces)

This project is optimized for **Hugging Face Spaces (Docker SDK)**.

1. **Create a Space:** Select "Docker" as the SDK.
2. **Upload Code:** Push your files (ensure `.dockerignore` is set).
3. **Set Secrets:** Go to **Settings > Variables and secrets** and add:
* `DATABASE_URL`: Your Neon Tech connection string (e.g., `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`).


4. **Port Config:** The `Dockerfile` is configured to expose port `7860` for Hugging Face compatibility.

---

## 📱 How to Install on Mobile (Android)

You can turn this web app into a native-feeling mobile app.

**Option A: Instant Install (PWA)**

1. Open your deployed URL in **Chrome** on Android.
2. Tap the **three dots (⋮)** menu.
3. Tap **"Install App"** or **"Add to Home Screen"**.

**Option B: Generate an APK**

1. Go to [WebIntoApp.com](https://www.webintoapp.com) or [PWABuilder.com](https://www.pwabuilder.com).
2. Paste your **Direct Space URL** (e.g., `https://yourname-nigeria-sales-predictor.hf.space`).
3. Generate and download the `.apk` file.
4. Install on your device.

---

## 📂 Project Structure

```text
├── main.py                  # The Brain: FastAPI backend, Lazy Loading logic, DB Routes
├── nigeria_sales_model.pkl  # The AI: Pre-trained XGBoost model (via Git LFS)
├── encoders.pkl             # The Translator: Maps text labels to model numbers
├── stores_nigeria.csv       # The Map: Linking States to Economic Tiers
├── Dockerfile               # Production build instructions (Port 7860)
├── docker-compose.yml       # Local development orchestrator
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html           # The UI: Responsive Dashboard
└── static/
    ├── css/                 # Custom Styles
    └── icons/               # PWA Icons

```

---

## 💾 Database Inspection

Every prediction is saved to the PostgreSQL database.

**Option A: Command Line (Local Docker)**

```bash
# 1. Enter the database container
docker exec -it <container_name> psql -U sales_user -d sales_db

# 2. Run SQL query
SELECT * FROM prediction_history;

```

**Option B: Production (Neon)**
Use the SQL Editor in your Neon Dashboard to run:

```sql
SELECT * FROM prediction_history ORDER BY timestamp DESC;

```

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes.
4. Push to the branch and open a Pull Request.

## 📄 License

This project is open-source and available under the **MIT License**.

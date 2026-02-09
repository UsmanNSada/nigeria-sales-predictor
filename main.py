import os
import gc
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# FastAPI Imports
from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Database Imports
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ===========================
# 1. DATABASE CONFIGURATION
# ===========================
# Connects to Render's Neon DB or Localhost fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sales_user:sales_password@localhost/sales_db")

# FIX: Render/Neon provides 'postgres://', but SQLAlchemy needs 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the History Table
class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    id = Column(Integer, primary_key=True, index=True)
    date_input = Column(Date)
    city = Column(String)
    family = Column(String)
    sales_prediction = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables if they don't exist
try:
    Base.metadata.create_all(bind=engine)
except:
    print("⚠️ Warning: DB connection not ready yet. Docker will retry.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===========================
# 2. INTELLIGENT LOADING (The Fix)
# ===========================

# A. LOAD ENCODERS & CSV IMMEDIATELY 
# These are small files. We need them for the Homepage dropdowns.
try:
    print("⏳ Loading Encoders & Store Data...")
    encoders = joblib.load('encoders.pkl')
    
    if os.path.exists('stores_nigeria.csv'):
        stores_df = pd.read_csv('stores_nigeria.csv')
        all_cities = sorted(stores_df['city'].unique())
    else:
        all_cities = ['Lagos'] # Fallback
        stores_df = pd.DataFrame()

except Exception as e:
    print(f"❌ Critical Error loading context files: {e}")
    encoders = None
    all_cities = []

# B. LAZY LOAD THE MODEL (The Memory Saver)
# We keep 'model' as None so the app starts fast and uses low RAM.
model = None

def get_lazy_model():
    """
    Only load the heavy 180MB model when a user actually clicks 'Predict'.
    """
    global model
    if model is None:
        print("⚡ Waking up the AI Brain (Lazy Load)...")
        gc.collect() # Clean RAM before loading
        # mmap_mode='r' reads from disk without copying to RAM
        model = joblib.load('nigeria_sales_model.pkl', mmap_mode='r')
        print("✅ AI Model Loaded Successfully.")
    return model

# ===========================
# 3. APP SETUP
# ===========================
app = FastAPI(title="Nigeria Sales Predictor")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DEFAULT_OIL_PRICE = 50.0 

# ===========================
# 4. WEB ROUTES
# ===========================

@app.get("/")
def read_form(request: Request):
    # Encoders are already loaded, so this works instantly!
    family_list = sorted(encoders['family'].classes_) if encoders else []
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cities": all_cities,
        "families": family_list,
        "selected_city": "Lagos",
        "selected_family": "GROCERY I",
        "selected_date": "2017-08-16",
        "selected_promo": "no"
    })

@app.post("/")
def predict_sales(
    request: Request,
    date: str = Form(...),
    city: str = Form(...),
    family: str = Form(...),
    promotion_status: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # --- 1. WAKE UP THE MODEL ---
        # This is where we load the heavy file!
        clf = get_lazy_model()

        # --- A. LOGIC: Find Store ID ---
        city_stores = stores_df[stores_df['city'] == city]
        if not city_stores.empty:
            selected_store = city_stores.iloc[0]
            store_nbr = selected_store['store_nbr']
            cluster = selected_store['cluster']
            store_type = selected_store['type']
        else:
            store_nbr = 1; cluster = 1; store_type = 'D'

        # --- B. SAFE ENCODING ---
        if city in encoders['city'].classes_:
            safe_city_code = encoders['city'].transform([city])[0]
        else:
            safe_city_code = encoders['city'].transform([encoders['city'].classes_[0]])[0]

        # --- C. PREPROCESSING ---
        promo_map = {"no": 0.0, "yes": 10.0, "high": 50.0}
        onpromotion_value = promo_map.get(promotion_status, 0.0)
        dt = datetime.strptime(date, '%Y-%m-%d')
        
        input_data = pd.DataFrame({
            'store_nbr': [store_nbr],
            'family': [encoders['family'].transform([family])[0]],
            'onpromotion': [onpromotion_value],
            'type': [encoders['type'].transform([store_type])[0]],
            'cluster': [cluster],
            'dcoilwtico': [DEFAULT_OIL_PRICE],
            'month': [dt.month],
            'day_of_month': [dt.day],
            'day_of_week': [dt.weekday()],
            'day_of_year': [dt.timetuple().tm_yday],
            'quarter': [(dt.month - 1) // 3 + 1],
            'is_weekend': [1 if dt.weekday() >= 5 else 0],
            'is_payday': [1 if dt.day in [15, 30, 31] else 0],
            'is_post_payday': [1 if dt.day in [1, 16] else 0],
            'is_holiday_or_event': [0], 
            'city': [safe_city_code], 
            'state': [safe_city_code] 
        })

        # --- D. PREDICTION ---
        # Use 'clf' (the locally loaded model)
        log_pred = clf.predict(input_data)[0]
        units_pred = np.expm1(log_pred)
        units_pred = max(0, float(units_pred))

        # Scale to Department Level
        CATEGORY_MULTIPLIER = 50 
        adjusted_units = units_pred * CATEGORY_MULTIPLIER

        # --- E. REVENUE CALCULATION ---
        price_map = {
            'AUTOMOTIVE': 4500, 'BABY CARE': 2500, 'BEAUTY': 3000,
            'BEVERAGES': 1200, 'BOOKS': 2500, 'BREAD/BAKERY': 500,
            'CELEBRATION': 2000, 'CLEANING': 1500, 'DAIRY': 1800,
            'DELI': 2500, 'EGGS': 1200, 'FROZEN FOODS': 3500,
            'GROCERY I': 2000, 'GROCERY II': 2000, 'HARDWARE': 8000,
            'HOME AND KITCHEN I': 6000, 'HOME AND KITCHEN II': 6000,
            'HOME APPLIANCES': 45000, 'HOME CARE': 1500,
            'LADIESWEAR': 6500, 'LAWN AND GARDEN': 5000, 'LINGERIE': 4000,
            'LIQUOR,WINE,BEER': 4500, 'MAGAZINES': 800, 'MEATS': 4500,
            'PERSONAL CARE': 1800, 'PET SUPPLIES': 3000,
            'PLAYERS AND ELECTRONICS': 25000, 'POULTRY': 4000,
            'PREPARED FOODS': 2000, 'PRODUCE': 800,
            'SCHOOL AND OFFICE SUPPLIES': 1200, 'SEAFOOD': 5500
        }
        
        avg_price = price_map.get(family, 1500)
        revenue = adjusted_units * avg_price

        formatted_result = f"₦ {revenue:,.2f}"
        detail_text = f"Forecast: {int(adjusted_units):,} items (Dept. Total) × ₦{avg_price:,}/item"

        # --- F. SAVE TO DB ---
        db.add(PredictionHistory(date_input=dt.date(), city=city, family=family, sales_prediction=revenue))
        db.commit()

    except Exception as e:
        formatted_result = f"Error: {str(e)}"
        detail_text = "Please check logs."
        print(f"❌ Prediction Error: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "cities": all_cities,
        "families": sorted(encoders['family'].classes_) if encoders else [],
        "prediction": formatted_result,
        "detail": detail_text,
        "selected_city": city,
        "selected_family": family,
        "selected_date": date,
        "selected_promo": promotion_status
    })
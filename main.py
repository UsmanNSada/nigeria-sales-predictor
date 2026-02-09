import os
from fastapi.staticfiles import StaticFiles  # <--- Make sure this is imported
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import pandas as pd
import numpy as np
import joblib

# ===========================
# 1. DATABASE CONFIGURATION
# ===========================
# Connects to 'db' container in Docker, or 'localhost' if running locally
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sales_user:sales_password@localhost/sales_db")

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
# 2. LOAD AI MODEL & CONTEXT
# ===========================
print("⏳ Loading AI Model & Context Data...")
try:
    model = joblib.load('nigeria_sales_model.pkl')
    encoders = joblib.load('encoders.pkl')
    
    # Load the State-to-Store Mapping CSV
    if os.path.exists('stores_nigeria.csv'):
        stores_df = pd.read_csv('stores_nigeria.csv')
        # This gives us the full list of 36 States + FCT for the dropdown
        all_cities = sorted(stores_df['city'].unique())
    else:
        # Fallback (Safety Mode)
        stores_df = pd.DataFrame({'store_nbr': [1], 'city': ['Lagos'], 'cluster': [1], 'type': ['D']})
        all_cities = ['Lagos']
        
    print("✅ AI System Ready.")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    stores_df = pd.DataFrame()
    all_cities = []

app = FastAPI(title="Nigeria Sales Predictor")

# NEW: Tell FastAPI to serve files inside the 'static' folder
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DEFAULT_OIL_PRICE = 50.0 

# ===========================
# 3. WEB ROUTES
# ===========================

@app.get("/")
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cities": all_cities, # Shows all 36 States
        "families": sorted(encoders['family'].classes_),
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
        # --- A. LOGIC: Find the Best Store ID for this State ---
        # Map user's State choice to a specific Store ID (Economic Tier)
        city_stores = stores_df[stores_df['city'] == city]
        
        if not city_stores.empty:
            selected_store = city_stores.iloc[0]
            store_nbr = selected_store['store_nbr']
            cluster = selected_store['cluster']
            store_type = selected_store['type']
        else:
            # Fallback defaults
            store_nbr = 1
            cluster = 1
            store_type = 'D'

        # --- B. SAFE ENCODING ---
        # If the AI doesn't know the name "Zamfara", use a known name (e.g. Lagos)
        # to prevent crashing. The Store ID drives the prediction, so this is safe.
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

        # --- D. PREDICTION & SCALING ---
        log_pred = model.predict(input_data)[0]
        units_pred = np.expm1(log_pred)
        units_pred = max(0, float(units_pred))

        # NEW: Scale single-item prediction to "Department Total"
        # We assume a category (e.g. "Dairy") has ~50 different products on shelf.
        CATEGORY_MULTIPLIER = 50 
        adjusted_units = units_pred * CATEGORY_MULTIPLIER

        # --- E. REVENUE CALCULATION ---
        # Estimated Average Price per Item (in 2017 Naira)
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
        detail_text = ""
        print(f"❌ Prediction Error: {e}")

    # Return template with "Sticky" values (user inputs preserved)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cities": all_cities,
        "families": sorted(encoders['family'].classes_),
        "prediction": formatted_result,
        "detail": detail_text,
        "selected_city": city,
        "selected_family": family,
        "selected_date": date,
        "selected_promo": promotion_status
    })
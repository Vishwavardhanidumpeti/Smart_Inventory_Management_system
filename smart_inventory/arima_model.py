# arima_model.py
import os
import pickle
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from models import Product, SaleRecord

MODEL_DIR = "data/models"
os.makedirs(MODEL_DIR, exist_ok=True)


# --------------------------------------------
# Train ARIMA for a single product
# --------------------------------------------
def train_and_forecast_for_product(product_id, series, steps=14):
    """
    Train ARIMA(1,1,1) on sales series and forecast next `steps` days.
    Saves trained model as product_{id}.pkl
    """
    try:
        series = pd.Series(series)
        series.index = pd.to_datetime(series.index)
        series = series.asfreq("D").fillna(0)
        series = series.clip(lower=0)

        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()

        # Save the trained model
        path = os.path.join(MODEL_DIR, f"product_{product_id}.pkl")
        with open(path, "wb") as f:
            pickle.dump(model_fit, f)

        forecast = model_fit.forecast(steps=steps)
        return np.maximum(forecast, 0)

    except Exception as e:
        print(f"⚠️ ARIMA failed for product {product_id}: {e}")
        return np.zeros(steps)


# --------------------------------------------
# Load trained model if exists
# --------------------------------------------
def load_model(product_id):
    path = os.path.join(MODEL_DIR, f"product_{product_id}.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


# --------------------------------------------
# Compute alerts (forecast-based)
# --------------------------------------------
def compute_alert_for_product(product, series, steps=14):
    forecast = train_and_forecast_for_product(product.id, series, steps=steps)
    expected_future = max(0, forecast.sum())
    expected_stock = product.stock_quantity - expected_future
    will_alert = expected_stock <= product.reorder_level
    return {
        "product_id": product.id,
        "product": product.name,
        "expected_stock": round(expected_stock, 2),
        "will_alert": will_alert
    }


# --------------------------------------------
# Train for all products
# --------------------------------------------
def train_all_products():
    from app import app  # import here to avoid circular import
    with app.app_context():
        print("🧠 Training ARIMA models for all products...")
        products = Product.query.all()
        trained = 0
        for p in products:
            sales = SaleRecord.query.filter_by(product_id=p.id).order_by(SaleRecord.date).all()
            if not sales:
                continue
            series = (
                pd.DataFrame([{"date": s.date, "qty": s.qty} for s in sales])
                .set_index("date")["qty"]
                .resample("D").sum()
            )
            train_and_forecast_for_product(p.id, series)
            trained += 1
        print(f"✅ ARIMA models trained for {trained} products!")

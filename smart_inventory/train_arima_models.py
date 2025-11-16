# train_arima_models.py
from app import app, db
from models import Product, SaleRecord
from arima_model import train_and_forecast_for_product
import pandas as pd

with app.app_context():
    products = Product.query.all()
    for product in products:
        sales = SaleRecord.query.filter_by(product_id=product.id).order_by(SaleRecord.date).all()
        if not sales:
            print(f"Skipping {product.name} — no sales data.")
            continue

        # Convert sales to a daily time series
        series = (
            pd.DataFrame([{"date": s.date, "qty": s.qty} for s in sales])
            .set_index("date")["qty"]
            .resample("D")
            .sum()
        )

        print(f"📊 Training ARIMA for {product.name}...")
        forecast = train_and_forecast_for_product(product.id, series, steps=14)
        print(f"✅ Forecast for {product.name}: {forecast.round(2)}")

print("\n🎯 All ARIMA models trained and saved in data/models/")

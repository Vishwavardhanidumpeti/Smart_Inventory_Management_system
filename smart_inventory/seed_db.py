# seed_db.py (example)
import pandas as pd
from models import db, Product, Supplier, SaleRecord
from app import app

df = pd.read_csv("data/synthetic_sales.csv", parse_dates=["date"])
with app.app_context():
    # create some products if missing
    for pid in sorted(df['product_id'].unique()):
        p = Product.query.filter_by(sku=f"SKU{pid}").first()
        if not p:
            p = Product(sku=f"SKU{pid}", name=f"Product {pid}", stock_quantity=200, reorder_level=20)
            db.session.add(p)
            db.session.commit()
    # add sale records
    for _, row in df.iterrows():
        prod = Product.query.filter_by(sku=f"SKU{int(row.product_id)}").first()
        sr = SaleRecord(product_id=prod.id, date=row.date.date(), qty=int(row.qty), type='sale')
        db.session.add(sr)
    db.session.commit()
    print("Seeded DB with sales records.")

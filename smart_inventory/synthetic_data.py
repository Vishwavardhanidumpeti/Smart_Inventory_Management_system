from app import db, Product, Supplier, SaleRecord
from datetime import datetime, timedelta
import random

def create_synthetic_data():
    db.drop_all()
    db.create_all()

    supplier = Supplier(name="GlobalTech Ltd", contact="supplier@globaltech.com")
    db.session.add(supplier)
    db.session.commit()

    # Add some sample products
    products = [
        Product(sku="P001", name="Smart Sensor", category="Electronics", cost_price=1200, selling_price=1500, stock_quantity=45, reorder_level=10, supplier_id=supplier.id),
        Product(sku="P002", name="IoT Camera", category="Security", cost_price=1800, selling_price=2200, stock_quantity=25, reorder_level=8, supplier_id=supplier.id),
        Product(sku="P003", name="Thermal Detector", category="Safety", cost_price=2500, selling_price=3100, stock_quantity=15, reorder_level=5, supplier_id=supplier.id),
    ]

    db.session.add_all(products)
    db.session.commit()

    # Generate sales records
    for product in products:
        for i in range(30):
            date_val = datetime.utcnow() - timedelta(days=30 - i)
            qty = random.randint(1, 6)
            sale = SaleRecord(product_id=product.id, qty=qty, type='sale', date=date_val)
            db.session.add(sale)
    db.session.commit()
    print("✅ Synthetic data added successfully!")

if __name__ == "__main__":
    create_synthetic_data()

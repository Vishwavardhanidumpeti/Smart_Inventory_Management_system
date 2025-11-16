# create_synthetic_data.py
from app import db, Product, Supplier, SaleRecord, User
from datetime import datetime, timedelta
import random

def create_synthetic_data():
    db.drop_all()
    db.create_all()

    # Create admin user
    admin = User(username='admin', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)

    # Add suppliers
    suppliers = [
        Supplier(name="TechWorld Ltd", contact="support@techworld.com"),
        Supplier(name="FreshMart Foods", contact="contact@freshmart.in"),
        Supplier(name="StyleHub Clothing", contact="help@stylehub.com"),
        Supplier(name="HealthCare Plus", contact="info@healthcareplus.in"),
        Supplier(name="HomeNeeds Depot", contact="sales@homeneeds.com"),
        Supplier(name="OfficeWorks Stationery", contact="order@officeworks.in")
    ]
    db.session.add_all(suppliers)
    db.session.commit()

    # Dictionary of categories with example products
    product_data = {
        "Groceries": [
            ("G001", "Rice 5kg Bag", 250, 320, 50, 10),
            ("G002", "Wheat Flour 5kg", 220, 290, 60, 15),
            ("G003", "Sunflower Oil 1L", 120, 160, 100, 20),
            ("G004", "Sugar 1kg", 40, 60, 80, 15),
            ("G005", "Tea Powder 500g", 180, 230, 40, 10),
            ("G006", "Toor Dal 1kg", 130, 170, 70, 15),
        ],
        "Electronics": [
            ("E001", "Bluetooth Speaker", 1200, 1800, 25, 5),
            ("E002", "Power Bank 10000mAh", 900, 1400, 30, 8),
            ("E003", "LED Bulb 12W", 120, 180, 60, 15),
            ("E004", "Smartphone Charger", 250, 400, 50, 10),
            ("E005", "Earphones Wired", 150, 300, 40, 10),
        ],
        "Clothing": [
            ("C001", "Men T-Shirt", 300, 500, 50, 10),
            ("C002", "Women Kurti", 450, 700, 35, 8),
            ("C003", "Jeans (Unisex)", 800, 1200, 40, 10),
            ("C004", "Kids Dress", 350, 600, 30, 8),
        ],
        "Stationery": [
            ("S001", "Notebook 200 pages", 40, 70, 100, 20),
            ("S002", "Ball Pen (Pack of 10)", 50, 90, 80, 15),
            ("S003", "Marker Pen", 25, 50, 70, 10),
            ("S004", "A4 Paper Ream", 250, 350, 20, 5),
        ],
        "Household": [
            ("H001", "Detergent Powder 1kg", 80, 120, 60, 10),
            ("H002", "Dish Wash Liquid 500ml", 60, 90, 50, 8),
            ("H003", "Floor Cleaner 1L", 100, 150, 40, 10),
            ("H004", "Mop Stick", 180, 250, 30, 5),
        ],
        "Health": [
            ("HL001", "Toothpaste 150g", 70, 110, 100, 20),
            ("HL002", "Shampoo 200ml", 120, 180, 80, 15),
            ("HL003", "Soap Pack (3 pcs)", 90, 140, 90, 15),
            ("HL004", "Hand Sanitizer 100ml", 60, 100, 50, 10),
            ("HL005", "Pain Relief Spray", 180, 250, 30, 5),
        ]
    }

    all_products = []
    supplier_list = suppliers

    # Add all products
    for category, items in product_data.items():
        supplier = random.choice(supplier_list)
        for sku, name, cost, price, stock, reorder in items:
            product = Product(
                sku=sku,
                name=name,
                category=category,
                cost_price=cost,
                selling_price=price,
                stock_quantity=stock,
                reorder_level=reorder,
                supplier_id=supplier.id
            )
            all_products.append(product)

    db.session.add_all(all_products)
    db.session.commit()

    # Create random 30 days of sales for each product
    for product in all_products:
        for i in range(30):
            date_val = datetime.utcnow() - timedelta(days=30 - i)
            qty = random.randint(1, 10)
            sale = SaleRecord(product_id=product.id, qty=qty, type='sale', date=date_val)
            db.session.add(sale)

    db.session.commit()
    print("✅ Realistic multi-category data successfully added to smart_inventory.db!")

if __name__ == "__main__":
    create_synthetic_data()

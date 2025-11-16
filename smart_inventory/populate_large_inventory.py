from app import db, Product, Supplier, SaleRecord, User, app
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker()

# -------------------------------------------------------------
# Product to Category Mapping (Module-level for import)
# -------------------------------------------------------------
product_category_map = {
    # Electronics
    "Bluetooth Speaker": "Electronics",
    "Wireless Mouse": "Electronics",
    "USB-C Charger": "Electronics",
    "Smart LED Bulb": "Electronics",
    "Power Bank": "Electronics",
    "Laptop Cooling Pad": "Electronics",
    "Portable SSD": "Electronics",
    "Noise Cancelling Headphones": "Electronics",
    "4K Monitor": "Electronics",
    "Smart Watch": "Electronics",
    # Furniture
    "Ergonomic Chair": "Furniture",
    "Office Desk": "Furniture",
    "Wooden Bookshelf": "Furniture",
    "Bean Bag": "Furniture",
    "Dining Table Set": "Furniture",
    "Sofa Cum Bed": "Furniture",
    "TV Stand": "Furniture",
    "Shoe Rack": "Furniture",
    "Recliner Chair": "Furniture",
    "Storage Cabinet": "Furniture",
    # Groceries
    "Organic Rice 5kg": "Groceries",
    "Sunflower Oil 1L": "Groceries",
    "Whole Wheat Flour 10kg": "Groceries",
    "Instant Coffee 200g": "Groceries",
    "Green Tea Pack": "Groceries",
    "Almonds 500g": "Groceries",
    "Cashew Nuts 1kg": "Groceries",
    "Olive Oil 1L": "Groceries",
    "Honey Jar 250ml": "Groceries",
    "Brown Bread Pack": "Groceries",
    # Clothing
    "Cotton T-Shirt": "Clothing",
    "Denim Jeans": "Clothing",
    "Formal Shirt": "Clothing",
    "Hoodie Sweatshirt": "Clothing",
    "Track Pants": "Clothing",
    "Sports Jacket": "Clothing",
    "Leather Belt": "Clothing",
    "Woolen Scarf": "Clothing",
    "Summer Dress": "Clothing",
    "Sneakers": "Clothing",
    # Toys
    "LEGO Classic Box": "Toys",
    "Remote Control Car": "Toys",
    "Barbie Doll Set": "Toys",
    "Building Blocks": "Toys",
    "Rubik's Cube": "Toys",
    "Toy Train": "Toys",
    "Soft Teddy Bear": "Toys",
    "Kids Puzzle Board": "Toys",
    "Action Figure": "Toys",
    "Water Gun": "Toys",
    # Sports
    "Cricket Bat": "Sports",
    "Football": "Sports",
    "Badminton Racket": "Sports",
    "Yoga Mat": "Sports",
    "Dumbbell Set": "Sports",
    "Skipping Rope": "Sports",
    "Tennis Ball Pack": "Sports",
    "Gym Gloves": "Sports",
    "Sports Bottle": "Sports",
    "Basketball": "Sports",
    # Beauty
    "Face Wash 100ml": "Beauty",
    "Moisturizer Cream": "Beauty",
    "Shampoo 500ml": "Beauty",
    "Hair Serum": "Beauty",
    "Body Lotion": "Beauty",
    "Lip Balm": "Beauty",
    "Compact Powder": "Beauty",
    "Perfume Spray": "Beauty",
    "Sunscreen Lotion": "Beauty",
    "Nail Polish Set": "Beauty",
    # Kitchen
    "Non-stick Frying Pan": "Kitchen",
    "Pressure Cooker 5L": "Kitchen",
    "Kitchen Knife Set": "Kitchen",
    "Cutting Board": "Kitchen",
    "Mixing Bowl Set": "Kitchen",
    "Electric Kettle": "Kitchen",
    "Mixer Grinder": "Kitchen",
    "Microwave Oven": "Kitchen",
    "Rice Cooker": "Kitchen",
    "Glass Tumbler Set": "Kitchen",
    # Stationery
    "A4 Notebook": "Stationery",
    "Gel Pen Set": "Stationery",
    "Highlighter Pack": "Stationery",
    "Stapler": "Stationery",
    "Sticky Notes": "Stationery",
    "Drawing Book": "Stationery",
    "Pencil Box": "Stationery",
    "Whiteboard Marker": "Stationery",
    "Calculator": "Stationery",
    "Sketch Pen Set": "Stationery",
    # Hardware
    "Electric Drill Machine": "Hardware",
    "Screwdriver Kit": "Hardware",
    "Hammer": "Hardware",
    "Measuring Tape": "Hardware",
    "Wrench Set": "Hardware",
    "Nails Pack": "Hardware",
    "Pliers": "Hardware",
    "Hand Saw": "Hardware",
    "Toolbox": "Hardware",
    "Safety Gloves": "Hardware",
    # Books
    "Python Programming Guide": "Books",
    "Data Science for Beginners": "Books",
    "Machine Learning Basics": "Books",
    "Novel - The Alchemist": "Books",
    "Autobiography of a Yogi": "Books",
    "Think and Grow Rich": "Books",
    "Rich Dad Poor Dad": "Books",
    "Atomic Habits": "Books",
    "To Kill a Mockingbird": "Books",
    "1984 by George Orwell": "Books"
}

# Additional products for missing categories
additional_products = {
    # Automotive
    "Car Battery": "Automotive",
    "Engine Oil 5L": "Automotive",
    "Car Air Freshener": "Automotive",
    "Tire Pressure Gauge": "Automotive",
    "Car Phone Mount": "Automotive",
    "Car Charger": "Automotive",
    "Car Floor Mat": "Automotive",
    "Windshield Wiper": "Automotive",
    "Car Vacuum Cleaner": "Automotive",
    "Jump Starter Kit": "Automotive",
    # Gardening
    "Garden Shovel": "Gardening",
    "Watering Can": "Gardening",
    "Garden Gloves": "Gardening",
    "Plant Pot Set": "Gardening",
    "Garden Pruner": "Gardening",
    "Fertilizer Pack": "Gardening",
    "Garden Hose": "Gardening",
    "Lawn Mower": "Gardening",
    "Garden Trowel": "Gardening",
    "Seed Pack": "Gardening",
    # Pharmacy
    "Pain Relief Tablets": "Pharmacy",
    "Cough Syrup": "Pharmacy",
    "Bandage Pack": "Pharmacy",
    "Antiseptic Solution": "Pharmacy",
    "Thermometer": "Pharmacy",
    "First Aid Kit": "Pharmacy",
    "Vitamin D Supplements": "Pharmacy",
    "Hand Sanitizer": "Pharmacy",
    "Face Mask Pack": "Pharmacy",
    "Blood Pressure Monitor": "Pharmacy",
    # Pet Supplies
    "Dog Food 10kg": "Pet Supplies",
    "Cat Litter": "Pet Supplies",
    "Pet Leash": "Pet Supplies",
    "Pet Bowl Set": "Pet Supplies",
    "Dog Toy": "Pet Supplies",
    "Pet Grooming Brush": "Pet Supplies",
    "Pet Bed": "Pet Supplies",
    "Cat Food 5kg": "Pet Supplies",
    "Pet Carrier": "Pet Supplies",
    "Pet Shampoo": "Pet Supplies"
}

# -------------------------------------------------------------
# Function: create large, realistic dataset for inventory
# -------------------------------------------------------------
def populate_large_inventory():
    with app.app_context():
        print("🧹 Clearing existing data...")
        db.drop_all()
        db.create_all()

        # -------------------------------------------------------------
        # Create admin user and supplier
        # -------------------------------------------------------------
        print("🏭 Adding supplier and admin...")
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)

        supplier = Supplier(
            name="Global Distributors Pvt Ltd",
            contact="info@globaldist.com"
        )
        db.session.add(supplier)
        db.session.commit()

        # -------------------------------------------------------------
        # Create 1000 unique products
        # -------------------------------------------------------------
        print("📦 Populating 1000 random products...")
        
        # Combine all products (using module-level mappings)
        all_products = {**product_category_map, **additional_products}
        product_names = list(all_products.keys())

        used_skus = set()
        products = []

        for _ in range(1000):
            sku = f"SKU{random.randint(10000, 99999)}"
            while sku in used_skus:
                sku = f"SKU{random.randint(10000, 99999)}"
            used_skus.add(sku)

            product_name = random.choice(product_names)
            product_category = all_products[product_name]

            product = Product(
                sku=sku,
                name=product_name,
                category=product_category,
                cost_price=round(random.uniform(100, 5000), 2),
                selling_price=round(random.uniform(500, 8000), 2),
                stock_quantity=random.randint(10, 500),
                reorder_level=random.randint(5, 25),
                supplier_id=supplier.id
            )

            db.session.add(product)
            products.append(product)

        db.session.commit()
        print("✅ 1000 unique products added successfully!")

        # -------------------------------------------------------------
        # Generate synthetic sales for the past 60 days
        # -------------------------------------------------------------
        print("💰 Generating 60 days of sales data...")
        for product in products:
            for i in range(60):
                date_val = datetime.utcnow() - timedelta(days=60 - i)
                qty = random.randint(1, 15)
                sale = SaleRecord(
                    product_id=product.id,
                    qty=qty,
                    type='sale',
                    date=date_val
                )
                db.session.add(sale)

        db.session.commit()
        print("📊 Sales records added successfully!")
        print("🎯 Database successfully populated with 1000 products and 60 days of sales data!")
        from arima_model import train_all_products
        print("🚀 Starting ARIMA training for all products...")
        train_all_products()
        print("✅ All ARIMA models trained and saved successfully!")


# -------------------------------------------------------------
# Run the function directly
# -------------------------------------------------------------
if __name__ == "__main__":
    populate_large_inventory()

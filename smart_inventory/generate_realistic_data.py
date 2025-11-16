import random
import mysql.connector
from faker import Faker

# Initialize Faker for realistic names and dates
fake = Faker()

# Database connection (adjust if needed)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sath",
    database="smart_inventory"
)
cursor = conn.cursor()

# Define realistic product categories and items
categories = {
    "Groceries": ["Rice", "Milk", "Eggs", "Sugar", "Bread", "Tea", "Coffee", "Oil", "Pasta", "Cheese"],
    "Electronics": ["Smartphone", "Laptop", "Earbuds", "Smartwatch", "Monitor", "Keyboard", "Mouse", "Charger"],
    "Clothing": ["T-shirt", "Jeans", "Jacket", "Socks", "Cap", "Scarf", "Sweater"],
    "Furniture": ["Chair", "Table", "Sofa", "Bed", "Wardrobe", "Lamp", "Shelf"],
    "Beauty": ["Shampoo", "Conditioner", "Soap", "Face Cream", "Perfume", "Toothpaste"],
    "Stationery": ["Pen", "Notebook", "Pencil", "Eraser", "File", "Marker"],
    "Automotive": ["Tyre", "Car Battery", "Wiper", "Seat Cover", "Engine Oil"],
    "Toys": ["Lego Set", "Doll", "Puzzle", "RC Car", "Action Figure"]
}

# Generate 1000 products
products = []
for _ in range(1000):
    category = random.choice(list(categories.keys()))
    name = random.choice(categories[category])
    price = round(random.uniform(10, 5000), 2)
    stock = random.randint(5, 300)
    sold = random.randint(0, stock)
    date = fake.date_this_year()

    products.append((name, category, price, stock, sold, date))

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price FLOAT,
    stock INT,
    sold INT,
    last_sold_date DATE
)
""")

# Clear old data (optional)
cursor.execute("DELETE FROM products")

# Insert data
cursor.executemany("""
INSERT INTO products (name, category, price, stock, sold, last_sold_date)
VALUES (%s, %s, %s, %s, %s, %s)
""", products)

conn.commit()
conn.close()

print("✅ Realistic product data (1000 items) added successfully!")

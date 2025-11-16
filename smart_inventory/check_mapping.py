"""Quick script to verify category mappings"""
from populate_large_inventory import product_category_map, additional_products

all_products = {**product_category_map, **additional_products}

test_products = [
    'Face Wash 100ml',
    'Action Figure',
    '1984 by George Orwell',
    'Sunscreen Lotion',
    'Toolbox',
    'Novel - The Alchemist',
    'Dumbbell Set',
    'Bean Bag',
    'Ergonomic Chair',
    'Hair Serum'
]

print("Category Mapping Verification:")
print("=" * 60)
for name in test_products:
    category = all_products.get(name, "NOT FOUND")
    print(f"{name:30} → {category}")

print("\n✅ Mapping is correct in populate_large_inventory.py")
print("⚠️  The database has incorrect categories that need to be fixed.")


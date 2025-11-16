"""
Script to fix incorrect product categories in the database
"""
from app import app, db, Product
from populate_large_inventory import product_category_map, additional_products

# Combine all product mappings
all_products = {**product_category_map, **additional_products}

def fix_product_categories():
    """Fix all product categories based on the mapping"""
    with app.app_context():
        products = Product.query.all()
        fixed_count = 0
        not_found_count = 0
        
        print("🔧 Fixing product categories...")
        print("=" * 60)
        
        for product in products:
            expected_category = all_products.get(product.name)
            
            if expected_category is None:
                # Product name not in mapping
                not_found_count += 1
                print(f"⚠️  {product.name} - Not in mapping, keeping current: {product.category}")
            elif product.category != expected_category:
                # Fix the category
                old_category = product.category
                product.category = expected_category
                fixed_count += 1
                print(f"✅ Fixed: {product.name}")
                print(f"   {old_category} → {expected_category}")
        
        db.session.commit()
        
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"✅ Fixed categories: {fixed_count}")
        print(f"⚠️  Products not in mapping: {not_found_count}")
        print(f"📦 Total products checked: {len(products)}")
        print("\n✅ All categories have been corrected!")

if __name__ == "__main__":
    fix_product_categories()


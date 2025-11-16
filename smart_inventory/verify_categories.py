"""
Script to verify that products are correctly categorized
"""
from app import app, db, Product
from populate_large_inventory import product_category_map, additional_products

# Combine all product mappings
all_products = {**product_category_map, **additional_products}

def verify_product_categories():
    """Verify that all products in the database have correct categories"""
    with app.app_context():
        products = Product.query.all()
        mismatched = []
        correct = 0
        uncategorized = 0
        
        print("🔍 Verifying product categories...")
        print("=" * 60)
        
        for product in products:
            expected_category = all_products.get(product.name)
            
            if expected_category is None:
                # Product name not in mapping - might be manually added
                if product.category:
                    uncategorized += 1
                    print(f"⚠️  {product.name} - Category: {product.category} (Not in mapping)")
                else:
                    uncategorized += 1
                    print(f"❌ {product.name} - No category assigned")
            elif product.category != expected_category:
                mismatched.append({
                    'name': product.name,
                    'current': product.category,
                    'expected': expected_category
                })
                print(f"❌ MISMATCH: {product.name}")
                print(f"   Current: {product.category}")
                print(f"   Expected: {expected_category}")
            else:
                correct += 1
        
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"✅ Correctly categorized: {correct}")
        print(f"❌ Mismatched categories: {len(mismatched)}")
        print(f"⚠️  Uncategorized/Unknown: {uncategorized}")
        print(f"📦 Total products: {len(products)}")
        
        if mismatched:
            print(f"\n🔧 Products that need category correction:")
            for item in mismatched[:10]:  # Show first 10
                print(f"   - {item['name']}: '{item['current']}' → '{item['expected']}'")
            if len(mismatched) > 10:
                print(f"   ... and {len(mismatched) - 10} more")
        
        return {
            'correct': correct,
            'mismatched': len(mismatched),
            'uncategorized': uncategorized,
            'total': len(products),
            'mismatches': mismatched
        }

if __name__ == "__main__":
    verify_product_categories()



# real_time_update.py
from app import app, db
from models import Product, SaleRecord
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import random
import time

def update_real_time_data():
    with app.app_context():
        products = Product.query.all()
        for product in products:
            # ✅ use stock_quantity, not quantity
            change = random.randint(-3, 5)
            product.stock_quantity = max(0, product.stock_quantity + change)

            # Log change as sale/purchase
            sale_type = "sale" if change < 0 else "restock"
            sale = SaleRecord(
                product_id=product.id,
                qty=abs(change),
                type=sale_type,
                date=datetime.utcnow()
            )
            db.session.add(sale)

        db.session.commit()
        print(f"[{datetime.now()}] 🔄 Real-time inventory updated.")

if __name__ == "__main__":
    print("Starting real-time inventory updates...")
    update_real_time_data()  # Run once at startup

    scheduler = BackgroundScheduler()
    scheduler.add_job(update_real_time_data, 'interval', minutes=2)  # runs every 2 mins
    scheduler.start()

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")

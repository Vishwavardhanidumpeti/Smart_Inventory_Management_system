
import os
import random
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from models import db, User, Product, Supplier, SaleRecord
from arima_model import train_and_forecast_for_product

# ------------------ APP SETUP ------------------
app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------ INITIAL SETUP ------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created — username: admin, password: admin123")


# ------------------ SYNTHETIC DATA ------------------
def ensure_synthetic_data():
    """Add sample data if DB is empty."""
    if Product.query.count() == 0:
        p = Product(
            sku="SYN001",
            name="Synthetic Sensor",
            category="Electronics",
            cost_price=1200.0,
            selling_price=1499.0,
            stock_quantity=50,
            reorder_level=10
        )
        db.session.add(p)
        db.session.commit()

        for i in range(30):
            qty = random.randint(1, 8)
            date_val = datetime.utcnow() - timedelta(days=(30 - i))
            sale = SaleRecord(product_id=p.id, qty=qty, type='sale', date=date_val)
            db.session.add(sale)
        db.session.commit()
        print("✅ Synthetic product and sales data created.")


# ------------------ AUTH ROUTES ------------------
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = User.query.filter_by(username=request.form["username"]).first()
        if u and u.check_password(request.form["password"]):
            login_user(u)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "warning")
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully. Login now.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ------------------ DASHBOARD ------------------
@app.route("/dashboard")
@login_required
def dashboard():
    ensure_synthetic_data()
    products = Product.query.all()
    
    # Calculate profit metrics
    total_products = len(products)
    total_stock_value = sum((p.stock_quantity or 0) * (p.cost_price or 0) for p in products)
    total_potential_revenue = sum((p.stock_quantity or 0) * (p.selling_price or 0) for p in products)
    total_potential_profit = total_potential_revenue - total_stock_value
    
    # Calculate sales metrics
    total_sales = SaleRecord.query.filter_by(type='sale').count()
    recent_sales = SaleRecord.query.filter_by(type='sale').order_by(SaleRecord.date.desc()).limit(10).all()
    
    # Calculate revenue from sales
    sales_revenue = 0
    sales_cost = 0
    for sale in SaleRecord.query.filter_by(type='sale').all():
        if sale.product:
            sales_revenue += sale.qty * (sale.product.selling_price or 0)
            sales_cost += sale.qty * (sale.product.cost_price or 0)
    actual_profit = sales_revenue - sales_cost
    
    # Products with ARIMA forecasts
    products_with_forecast = []
    for p in products:
        sales = SaleRecord.query.filter_by(product_id=p.id).order_by(SaleRecord.date).all()
        if len(sales) >= 10:
            products_with_forecast.append(p)
    
    metrics = {
        'total_products': total_products,
        'total_stock_value': total_stock_value,
        'total_potential_revenue': total_potential_revenue,
        'total_potential_profit': total_potential_profit,
        'actual_profit': actual_profit,
        'sales_revenue': sales_revenue,
        'sales_cost': sales_cost,
        'total_sales': total_sales,
        'products_with_forecast': len(products_with_forecast)
    }
    
    return render_template("dashboard.html", products=products[:10], metrics=metrics)


# ------------------ PRODUCT CRUD ------------------
@app.route("/products")
@login_required
def products_page():
    query = request.args.get("q", "")
    if query:
        products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    else:
        products = Product.query.all()
    return render_template("products.html", products=products, query=query)


@app.route("/inventory")
@login_required
def inventory():
    query = request.args.get("q", "")
    if query:
        products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    else:
        products = Product.query.all()
    return render_template("inventory.html", products=products, query=query)


@app.route("/product/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        # Try to auto-categorize based on product name
        product_name = request.form["name"]
        category = request.form.get("category")
        
        # Import category mapping
        try:
            from populate_large_inventory import product_category_map, additional_products
            all_products = {**product_category_map, **additional_products}
            # Auto-categorize if category not provided and product name matches
            if not category and product_name in all_products:
                category = all_products[product_name]
        except:
            pass
        
        p = Product(
            sku=request.form["sku"],
            name=product_name,
            category=category,
            cost_price=float(request.form.get("cost_price", 0)),
            selling_price=float(request.form.get("selling_price", 0)),
            stock_quantity=int(request.form.get("stock_quantity", 0)),
            reorder_level=int(request.form.get("reorder_level", 10))
        )
        db.session.add(p)
        db.session.commit()
        flash("✅ Product added successfully!", "success")
        return redirect(url_for("products_page"))
    return render_template("add_product.html")


@app.route("/product/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):
    p = Product.query.get_or_404(id)
    if request.method == "POST":
        p.sku = request.form["sku"]
        p.name = request.form["name"]
        p.category = request.form.get("category")
        p.cost_price = float(request.form.get("cost_price", 0))
        p.selling_price = float(request.form.get("selling_price", 0))
        p.stock_quantity = int(request.form.get("stock_quantity", 0))
        p.reorder_level = int(request.form.get("reorder_level", 10))
        db.session.commit()
        flash("✅ Product updated successfully!", "success")
        return redirect(url_for("products_page"))
    return render_template("edit_product.html", product=p)


@app.route("/product/update/<int:id>", methods=["POST"])
@login_required
def update_product(id):
    """Alternative route name for inventory.html compatibility"""
    p = Product.query.get_or_404(id)
    p.name = request.form.get("name", p.name)
    p.category = request.form.get("category", p.category)
    p.cost_price = float(request.form.get("cost_price", 0) or p.cost_price or 0)
    p.selling_price = float(request.form.get("selling_price", 0) or p.selling_price or 0)
    p.stock_quantity = int(request.form.get("stock", 0) or p.stock_quantity or 0)
    p.reorder_level = int(request.form.get("reorder", 10) or p.reorder_level or 10)
    db.session.commit()
    flash("✅ Product updated successfully!", "success")
    return redirect(url_for("inventory"))


@app.route("/product/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_product(id):
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("🗑️ Product deleted successfully.", "info")
    # Redirect based on referrer or default to products_page
    referrer = request.referrer
    if referrer and "inventory" in referrer:
        return redirect(url_for("inventory"))
    return redirect(url_for("products_page"))


# ------------------ SALES ------------------
@app.route("/sales/add", methods=["POST"])
@login_required
def add_sale():
    product_id = int(request.form["product_id"])
    qty = int(request.form["qty"])
    type_ = request.form.get("type", "sale")
    date_val = datetime.strptime(request.form.get("date"), "%Y-%m-%d") if request.form.get("date") else datetime.utcnow()

    sr = SaleRecord(product_id=product_id, qty=qty, type=type_, date=date_val)
    db.session.add(sr)

    p = Product.query.get(product_id)
    if p:
        if type_ == "sale":
            p.stock_quantity = max(0, (p.stock_quantity or 0) - qty)
        else:
            p.stock_quantity = (p.stock_quantity or 0) + qty

    db.session.commit()
    return jsonify({"status": "success"})


# ------------------ PRODUCT DETAILS + FORECAST ------------------
@app.route("/product/<int:id>")
@login_required
def product_detail(id):
    product = Product.query.get_or_404(id)
    sales = SaleRecord.query.filter_by(product_id=product.id).order_by(SaleRecord.date).all()

    actual_dates, actual_vals, forecast_dates, forecast_vals = [], [], [], []
    if sales:
        df = pd.DataFrame([{"date": s.date, "qty": s.qty} for s in sales])
        df["date"] = pd.to_datetime(df["date"])
        daily = df.groupby("date").sum().asfreq("D").fillna(0)["qty"]

        actual_dates = [d.strftime("%Y-%m-%d") for d in daily.index]
        actual_vals = daily.tolist()

        if len(daily) >= 10:
            forecast = train_and_forecast_for_product(product.id, daily, steps=14)
            last_date = pd.to_datetime(daily.index[-1])
            forecast_len = len(forecast)
            forecast_dates = [(last_date + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, forecast_len + 1)]
            forecast_vals = [float(x) for x in forecast]
            
            # Calculate forecast statistics
            forecast_sum = sum(forecast_vals)
            forecast_avg = forecast_sum / len(forecast_vals) if forecast_vals else 0
            projected_revenue = forecast_sum * (product.selling_price or 0)
        else:
            forecast_sum = 0
            forecast_avg = 0
            projected_revenue = 0

    forecast_data = {
        "dates": actual_dates + forecast_dates,
        "actual": actual_vals + [None] * len(forecast_vals),
        "forecast": [None] * len(actual_vals) + forecast_vals,
        "forecast_sum": forecast_sum,
        "forecast_avg": forecast_avg,
        "projected_revenue": projected_revenue
    }

    return render_template("product_detail.html", product=product, forecast_data=forecast_data)


# ------------------ ALERTS ------------------
@app.route("/alerts")
@login_required
def alerts_page():
    products = Product.query.all()
    # Filter products with low stock
    low_stock_products = [p for p in products if (p.stock_quantity is not None and p.reorder_level is not None and p.stock_quantity <= p.reorder_level)]
    
    # Format alerts for template
    alerts = []
    for p in low_stock_products:
        alerts.append({
            "product": p.name,
            "expected_stock": p.stock_quantity,
            "status": "Low"
        })
    
    return render_template("alerts.html", alerts=alerts, low_stock_alerts=[])


# ------------------ PROFIT ANALYSIS ------------------
@app.route("/profit-analysis")
@login_required
def profit_analysis():
    products = Product.query.all()
    
    # Calculate profit by product
    product_profits = []
    for p in products:
        sales = SaleRecord.query.filter_by(product_id=p.id, type='sale').all()
        units_sold = sum(s.qty for s in sales)
        revenue = units_sold * (p.selling_price or 0)
        cost = units_sold * (p.cost_price or 0)
        profit = revenue - cost
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        # Calculate profit per unit
        profit_per_unit = (p.selling_price or 0) - (p.cost_price or 0)
        
        # Potential profit from current stock
        potential_profit = (p.stock_quantity or 0) * profit_per_unit
        
        product_profits.append({
            'product': p,
            'units_sold': units_sold,
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
            'profit_margin': profit_margin,
            'profit_per_unit': profit_per_unit,
            'potential_profit': potential_profit,
            'stock_value': (p.stock_quantity or 0) * (p.cost_price or 0)
        })
    
    # Sort by profit
    product_profits.sort(key=lambda x: x['profit'], reverse=True)
    
    # Calculate totals
    total_revenue = sum(p['revenue'] for p in product_profits)
    total_cost = sum(p['cost'] for p in product_profits)
    total_profit = total_revenue - total_cost
    total_potential_profit = sum(p['potential_profit'] for p in product_profits)
    total_stock_value = sum(p['stock_value'] for p in product_profits)
    
    # Calculate profit by category
    category_profits = {}
    for p in product_profits:
        category = p['product'].category or 'Uncategorized'
        if category not in category_profits:
            category_profits[category] = {'revenue': 0, 'cost': 0, 'profit': 0}
        category_profits[category]['revenue'] += p['revenue']
        category_profits[category]['cost'] += p['cost']
        category_profits[category]['profit'] += p['profit']
    
    # Monthly profit trend
    monthly_data = {}
    for sale in SaleRecord.query.filter_by(type='sale').all():
        if sale.product and sale.date:
            month_key = sale.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'revenue': 0, 'cost': 0, 'profit': 0}
            revenue = sale.qty * (sale.product.selling_price or 0)
            cost = sale.qty * (sale.product.cost_price or 0)
            monthly_data[month_key]['revenue'] += revenue
            monthly_data[month_key]['cost'] += cost
            monthly_data[month_key]['profit'] += revenue - cost
    
    # Sort monthly data
    monthly_trend = sorted(monthly_data.items())
    
    return render_template("profit_analysis.html", 
                         product_profits=product_profits,
                         total_revenue=total_revenue,
                         total_cost=total_cost,
                         total_profit=total_profit,
                         total_potential_profit=total_potential_profit,
                         total_stock_value=total_stock_value,
                         category_profits=category_profits,
                         monthly_trend=monthly_trend)


# ------------------ CATEGORY VERIFICATION ------------------
@app.route("/verify-categories")
@login_required
def verify_categories():
    """Verify product categories are correctly mapped"""
    try:
        from populate_large_inventory import product_category_map, additional_products
        all_products = {**product_category_map, **additional_products}
    except:
        all_products = {}
    
    products = Product.query.all()
    mismatched = []
    correct = 0
    uncategorized = 0
    category_stats = {}
    
    for product in products:
        expected_category = all_products.get(product.name)
        
        if expected_category is None:
            uncategorized += 1
        elif product.category != expected_category:
            mismatched.append({
                'id': product.id,
                'name': product.name,
                'current': product.category,
                'expected': expected_category
            })
        else:
            correct += 1
        
        # Count by category
        cat = product.category or 'Uncategorized'
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    return render_template("verify_categories.html",
                         total=len(products),
                         correct=correct,
                         mismatched=mismatched,
                         uncategorized=uncategorized,
                         category_stats=sorted(category_stats.items()))


@app.route("/fix-categories", methods=["POST"])
@login_required
def fix_categories():
    """Fix all product categories based on mapping"""
    try:
        from populate_large_inventory import product_category_map, additional_products
        all_products = {**product_category_map, **additional_products}
    except:
        all_products = {}
    
    products = Product.query.all()
    fixed_count = 0
    not_found_count = 0
    
    for product in products:
        expected_category = all_products.get(product.name)
        
        if expected_category is None:
            not_found_count += 1
        elif product.category != expected_category:
            product.category = expected_category
            fixed_count += 1
    
    db.session.commit()
    
    flash(f"✅ Fixed {fixed_count} product categories! {not_found_count} products not in mapping.", "success")
    return redirect(url_for("verify_categories"))


# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(debug=True)

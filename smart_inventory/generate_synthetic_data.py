import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

np.random.seed(42)

def generate_product_series(product_id, days=365, base=10, trend=0.01, seasonality=7):
    dates = pd.date_range(end=datetime.today(), periods=days, freq='D')
    # daily demand = base + trend*day + weekly seasonality + noise
    day_idx = np.arange(days)
    seasonal = 3 * np.sin(2*np.pi*day_idx/seasonality)
    trend_component = trend * day_idx
    noise = np.random.poisson(lam=1.5, size=days) - 1
    demand = np.maximum(0, base + trend_component + seasonal + noise).astype(int)
    df = pd.DataFrame({"date":dates, "product_id":product_id, "qty":demand})
    return df

def generate_dataset(n_products=6, days=365):
    rows = []
    for pid in range(1, n_products+1):
        base = np.random.randint(2, 30)
        trend = np.random.uniform(-0.02, 0.02)
        df = generate_product_series(pid, days=days, base=base, trend=trend, seasonality=7)
        rows.append(df)
    df_all = pd.concat(rows, ignore_index=True)
    return df_all

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_dataset(n_products=8, days=420)
    df.to_csv("data/synthetic_sales.csv", index=False)
    print("Saved synthetic_sales.csv with shape", df.shape)

import numpy as np, pandas as pd

rng = np.random.default_rng(42)
catalog = {  # product: (category, price)
    "Laptop": ("Electronics", 900), "Smartphone": ("Electronics", 650),
    "Headphones": ("Electronics", 120), "Office Chair": ("Furniture", 210),
    "Standing Desk": ("Furniture", 480), "Notebook Pack": ("Stationery", 15),
    "Printer": ("Electronics", 260), "Monitor": ("Electronics", 300),
}
customers = [f"Customer_{i:02d}" for i in range(1, 31)]
regions = ["North", "South", "East", "West"]
n = 1500
products = rng.choice(list(catalog), n)
dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
df = pd.DataFrame({
    "Order_ID": [f"ORD{1000 + i}" for i in range(n)],
    "Date": dates,
    "Customer": rng.choice(customers, n),
    "Product": products,
    "Category": [catalog[p][0] for p in products],
    "Region": rng.choice(regions, n, p=[0.3, 0.2, 0.25, 0.25]),
    "Quantity": rng.integers(1, 8, n),
})
df["Unit_Price"] = [round(catalog[p][1] * rng.uniform(0.9, 1.1), 2) for p in products]
df["Revenue"] = (df["Quantity"] * df["Unit_Price"]).round(2)
df.sort_values("Date").to_csv("sales_data.csv", index=False)

open("business_notes.txt", "w").write("""ACME Retail - Business Notes 2025
Goal: grow annual revenue by 15% versus 2024 and keep Electronics above 60% of sales.
Strategy: push Standing Desk and Monitor bundles in Q3; run a back-to-school Notebook Pack promotion in July.
The West region is the priority for expansion; the South region has weaker marketing coverage.
Top customers receive a 5% loyalty discount when they exceed 20 orders per year.
""")
print("Created sales_data.csv and business_notes.txt")

"""Generate a transparent, reproducible synthetic beauty-FMCG sales dataset."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20260721)

products = pd.DataFrame([
    ("SKN-01", "Brightening Serum", "Skincare", 129_000, 35_000, 1.35),
    ("SKN-02", "Barrier Moisturizer", "Skincare", 99_000, 28_000, 1.20),
    ("SKN-03", "UV Sunscreen", "Skincare", 79_000, 22_000, 1.55),
    ("MUP-01", "Matte Lip Cream", "Makeup", 69_000, 18_000, 1.05),
    ("MUP-02", "Cushion Foundation", "Makeup", 149_000, 42_000, 0.90),
    ("HRC-01", "Anti-Hairfall Shampoo", "Haircare", 89_000, 25_000, 1.10),
], columns=["sku", "product", "category", "unit_price", "unit_cost", "demand_factor"])

channels = {"Marketplace": 1.25, "Modern Trade": 1.05, "Beauty Store": 0.85}
regions = {"Java": 1.35, "Sumatra": 0.95, "Bali-Nusra": 0.72}
dates = pd.date_range("2024-01-01", "2025-12-28", freq="W-MON")
rows = []
for _, p in products.iterrows():
    for channel, cf in channels.items():
        for region, rf in regions.items():
            for i, date in enumerate(dates):
                trend = 1 + 0.0035 * i
                seasonal = 1 + 0.16 * np.sin(2 * np.pi * date.month / 12)
                ramadan = 1.30 if date.month in (3, 4) else 1
                year_end = 1.22 if date.month in (11, 12) else 1
                promotion = int(rng.random() < (0.25 if channel == "Marketplace" else 0.16))
                discount = float(rng.choice([0.10, 0.15, 0.20])) if promotion else 0.0
                marketing = max(0, rng.normal(2.0, 0.7)) * 1_000_000
                mean = 44 * p.demand_factor * cf * rf * trend * seasonal * ramadan * year_end
                mean *= (1 + 1.8 * discount) * (1 + 0.025 * marketing / 1_000_000)
                units = max(0, int(rng.normal(mean, max(4, mean * 0.16))))
                rows.append((date, p.sku, p["product"], p.category, channel, region,
                             p.unit_price, p.unit_cost, promotion, discount, marketing, units))

df = pd.DataFrame(rows, columns=["date", "sku", "product", "category", "channel", "region",
                                     "unit_price", "unit_cost", "promotion", "discount_pct",
                                     "marketing_spend_idr", "units_sold"])
df["net_revenue_idr"] = (df.unit_price * (1 - df.discount_pct) * df.units_sold).round().astype("int64")
df["gross_profit_idr"] = (df.net_revenue_idr - df.unit_cost * df.units_sold).round().astype("int64")
df.to_csv(OUT / "beauty_fmcg_weekly_sales.csv", index=False)
print(f"Saved {len(df):,} rows to {OUT}")

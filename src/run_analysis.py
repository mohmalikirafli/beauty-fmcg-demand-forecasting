"""Train a time-aware demand model and translate forecasts into inventory actions."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "beauty_fmcg_weekly_sales.csv"
OUT = ROOT / "outputs"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["date"]).sort_values(["sku", "channel", "region", "date"])
keys = ["sku", "channel", "region"]
g = df.groupby(keys, observed=True)["units_sold"]
for lag in [1, 2, 4, 8]: df[f"lag_{lag}"] = g.shift(lag)
df["rolling_mean_4"] = g.transform(lambda s: s.shift(1).rolling(4).mean())
df["rolling_std_8"] = g.transform(lambda s: s.shift(1).rolling(8).std())
df["month"] = df.date.dt.month
df["weekofyear"] = df.date.dt.isocalendar().week.astype(int)
df["trend"] = (df.date - df.date.min()).dt.days / 7
model_df = df.dropna().copy()

cutoff = pd.Timestamp("2025-10-01")
train, test = model_df[model_df.date < cutoff], model_df[model_df.date >= cutoff]
features = ["sku", "category", "channel", "region", "promotion", "discount_pct",
            "marketing_spend_idr", "month", "weekofyear", "trend", "lag_1", "lag_2",
            "lag_4", "lag_8", "rolling_mean_4", "rolling_std_8"]
cats = ["sku", "category", "channel", "region"]
pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats)],
                        remainder="passthrough")
pipe = Pipeline([("preprocess", pre), ("model", HistGradientBoostingRegressor(
    learning_rate=.07, max_iter=250, max_leaf_nodes=24, l2_regularization=1.0, random_state=42))])
pipe.fit(train[features], train.units_sold)
pred = np.maximum(0, pipe.predict(test[features]))
baseline = test.lag_1.to_numpy()

def metrics(y, p):
    return {"MAE": float(mean_absolute_error(y, p)),
            "RMSE": float(mean_squared_error(y, p) ** .5),
            "WAPE_pct": float(np.abs(y-p).sum()/y.sum()*100)}

score = {"model": metrics(test.units_sold.to_numpy(), pred),
         "naive_last_week": metrics(test.units_sold.to_numpy(), baseline),
         "cutoff": str(cutoff.date()), "train_rows": len(train), "test_rows": len(test)}
(OUT / "model_metrics.json").write_text(json.dumps(score, indent=2))

forecast = test[["date", "sku", "product", "category", "channel", "region", "units_sold",
                 "unit_price", "unit_cost"]].copy()
forecast["forecast_units"] = np.rint(pred).astype(int)
forecast["abs_error"] = (forecast.units_sold - forecast.forecast_units).abs()
forecast.to_csv(OUT / "test_forecasts.csv", index=False)

# Inventory planning for the next replenishment cycle using the latest model forecast.
latest = forecast.sort_values("date").groupby(keys, as_index=False).tail(1).copy()
std = df.groupby(keys, observed=True).units_sold.std().rename("demand_std").reset_index()
latest = latest.merge(std, on=keys)
latest["lead_time_weeks"] = 2
latest["service_level_z"] = 1.645  # 95% cycle service level
latest["safety_stock"] = np.ceil(latest.service_level_z * latest.demand_std * np.sqrt(latest.lead_time_weeks)).astype(int)
latest["reorder_point"] = np.ceil(latest.forecast_units * latest.lead_time_weeks + latest.safety_stock).astype(int)
rng = np.random.default_rng(42)
latest["on_hand_units"] = np.maximum(0, np.rint(latest.reorder_point * rng.uniform(.55, 1.45, len(latest)))).astype(int)
latest["recommended_order_units"] = np.maximum(0, latest.reorder_point - latest.on_hand_units)
latest["inventory_status"] = np.select(
    [latest.on_hand_units < latest.reorder_point, latest.on_hand_units > latest.reorder_point * 1.30],
    ["Reorder", "Overstock risk"], default="Healthy")
latest.to_csv(OUT / "inventory_recommendations.csv", index=False)

summary = df.groupby("category", as_index=False).agg(units_sold=("units_sold","sum"),
    revenue_idr=("net_revenue_idr","sum"), gross_profit_idr=("gross_profit_idr","sum"))
summary.to_csv(OUT / "category_performance.csv", index=False)

sns.set_theme(style="whitegrid")
weekly = df.groupby("date", as_index=False).units_sold.sum()
fig, ax = plt.subplots(figsize=(12,5)); sns.lineplot(weekly, x="date", y="units_sold", ax=ax, color="#6C4AB6")
ax.set(title="Weekly demand across all beauty products", xlabel="", ylabel="Units sold")
fig.tight_layout(); fig.savefig(FIG / "weekly_demand.png", dpi=180); plt.close(fig)

plot = forecast.groupby("date", as_index=False)[["units_sold","forecast_units"]].sum().melt("date", var_name="series", value_name="units")
fig, ax = plt.subplots(figsize=(12,5)); sns.lineplot(plot, x="date", y="units", hue="series", ax=ax, palette=["#22223B", "#E76F51"])
ax.set(title="Holdout forecast vs actual demand", xlabel="", ylabel="Units"); fig.tight_layout()
fig.savefig(FIG / "forecast_vs_actual.png", dpi=180); plt.close(fig)
print(json.dumps(score, indent=2))

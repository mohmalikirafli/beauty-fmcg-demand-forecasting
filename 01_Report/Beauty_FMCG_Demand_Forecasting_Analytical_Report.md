# Beauty FMCG Demand Forecasting and Inventory Optimization

## Analytical Report

**Author:** Mohammad Maliki Rafli  
**Project type:** FMCG analytics portfolio  
**Data source:** Reproducible synthetic weekly sales data  
**Analysis period:** January 2024–December 2025

## Executive Summary

This project develops a time-aware machine-learning workflow for beauty FMCG demand forecasting and translates model outputs into inventory recommendations. The model achieved lower MAE, RMSE, and WAPE than a naïve last-week baseline. In the illustrative inventory scenario, 27 of 54 SKU–channel–region combinations required replenishment and seven indicated potential overstock.

Because the dataset is synthetic and the inventory assumptions are simplified, the results should be interpreted as a portfolio demonstration rather than a production-ready policy.

## 1. Business Context

Beauty FMCG demand is influenced by product category, channel, geography, promotions, marketing activity, seasonality, and major commercial periods. Underforecasting may create stockouts and lost sales, while overforecasting increases holding costs and obsolescence risk.

## 2. Objectives

1. Describe demand patterns across products, categories, channels, regions, and time.
2. Build a time-aware forecasting model.
3. Compare performance with a naïve last-week baseline.
4. Estimate safety stock and reorder points.
5. Classify inventory combinations as `Reorder`, `Healthy`, or `Overstock risk`.

## 3. Data

The synthetic dataset contains weekly observations for six fictional beauty SKUs, three product categories, three sales channels, and three Indonesian market regions from January 2024 to December 2025. The generator incorporates trend, seasonality, Ramadan and year-end uplift, promotions, discounts, marketing expenditure, channel effects, regional effects, and random variation. No proprietary or personal data are used.

## 4. Methods

### Feature engineering

Predictors include 1-, 2-, 4-, and 8-week demand lags; four-week rolling mean; eight-week rolling standard deviation; calendar variables; trend; promotion; discount; marketing expenditure; product; category; channel; and region. Lagged and rolling variables use prior observations only.

### Validation design

Observations before 1 October 2025 form the training set. Later observations form an untouched temporal holdout.

### Forecasting model

A `HistGradientBoostingRegressor` is fitted after one-hot encoding categorical predictors. The benchmark uses demand from the previous week.

### Evaluation metrics

- MAE: average absolute error in units.
- RMSE: error metric that penalizes larger misses.
- WAPE: total absolute error divided by total actual demand.

### Inventory logic

`Safety stock = z × demand standard deviation × √lead time`

`Reorder point = forecast demand × lead time + safety stock`

The scenario assumes a two-week lead time and a 95% cycle service level (`z = 1.645`).

## 5. Results

| Metric | Forecast model | Last-week baseline | Relative improvement |
|---|---:|---:|---:|
| MAE | 12.86 units | 18.45 units | 30.3% |
| RMSE | 17.71 units | 25.51 units | 30.6% |
| WAPE | 14.68% | 21.05% | 30.3% |

The illustrative inventory scenario produced 27 reorder combinations, 1,272 recommended order units, seven potential-overstock combinations, and 20 healthy combinations. Skincare generated approximately IDR 24.6 billion in simulated net revenue.

Detailed results are available in [`04_Output/`](../04_Output/).

## 6. Business Interpretation

The results indicate that lagged demand, rolling behavior, promotions, marketing, product, channel, and regional information improve short-term forecasting within the simulated environment. Forecasts become more actionable when translated into transparent replenishment rules. In practice, service levels and lead times should be differentiated by SKU value, velocity, volatility, and strategic importance.

## 7. Limitations

- The dataset is synthetic.
- Only one temporal holdout is used.
- On-hand inventory is simulated.
- Supplier capacity, minimum order quantities, case packs, shelf life, and stockout costs are excluded.
- Hierarchical coherence is not modeled.
- External market drivers are excluded.

## 8. Recommendations

1. Integrate validated ERP, sell-in, sell-out, promotion, pricing, and inventory data.
2. Use rolling-origin backtesting.
3. Benchmark statistical, machine-learning, and hierarchical models.
4. Estimate lead-time distributions.
5. Set service levels by SKU segmentation.
6. Include operational order constraints.
7. Monitor forecast bias, WAPE, stockouts, overstock, and model drift.

## 9. Conclusion

The project demonstrates an end-to-end FMCG analytics workflow connecting demand forecasting with inventory decisions. The model improves holdout accuracy relative to a naïve baseline and produces transparent replenishment recommendations. The next step is validation with real operational data and realistic supply-chain constraints.

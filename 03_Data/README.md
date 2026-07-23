# Synthetic Beauty FMCG Dataset

The dataset in this directory is synthetic and reproducible. It contains weekly sales observations for six fictional beauty products across three sales channels and three Indonesian market regions during 2024–2025.

## File

- `processed/beauty_fmcg_weekly_sales.csv`

## Generation

```bash
python 02_Script/generate_data.py
```

The generator models product, category, channel, and regional effects; time trend and monthly seasonality; Ramadan and year-end uplift; promotions, discounts, marketing expenditure; and random demand variation.

## Data Statement

No proprietary company data, customer records, or personally identifiable information are included. The dataset is intended for reproducibility, education, and portfolio demonstration.

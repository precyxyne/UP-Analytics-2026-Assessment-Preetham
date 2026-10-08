# Smart Home Energy Usage Consumption Prediction

## Overview

This project predicts two smart-home energy consumption targets:

- `Appliances`
- `lights`

The analysis combines indoor environmental measurements, outdoor weather conditions, and engineered temporal features. Because the data is time-dependent, all model evaluation uses chronological train/validation/test splits rather than random sampling.

The project includes exploratory analysis, data-quality checks, feature engineering, model comparison, driver analysis, error diagnostics, exported predictions, and a FastAPI inference API.

---

## Dataset

The dataset contains **19,735 observations** sampled at 10-minute intervals from:

**January 11, 2016 to May 27, 2016**

The original dataset contains 29 columns, including:

- Appliance and lighting energy consumption
- Indoor temperature and humidity measurements
- Outdoor temperature and humidity
- Atmospheric pressure
- Wind speed
- Visibility
- Dew point temperature
- `rv1` and `rv2`

### Data quality

The following checks were performed:

- Missing values: **0**
- Duplicate rows: **0**
- Duplicate timestamps: **0**
- Invalid timestamps: **0**
- Irregular timestamp gaps: **0**
- Sampling frequency: **10 minutes**

No observations were removed because of missing or malformed data.

---

## Feature Engineering

The final model schema contains **39 features**.

### Temporal features

- Hour
- Minute
- Day of week
- Day of month
- Month
- Week of year
- Weekday/weekend indicators
- Cyclical hour features
- Cyclical day-of-week features

### Environmental features

Indoor temperature and humidity measurements were combined with outdoor weather variables.

Additional aggregate features:

- Mean indoor temperature
- Mean indoor humidity
- Indoor-outdoor temperature difference

The variables `rv1` and `rv2` were evaluated separately and excluded from the final feature schema because they did not improve validation performance.

---

## Validation Strategy

The data was split chronologically:

| Split | Share | Period |
|---|---:|---|
| Train | 70% | Jan 11 – Apr 16 |
| Validation | 15% | Apr 16 – May 7 |
| Test | 15% | May 7 – May 27 |

No random shuffling was used.

The validation set was used for model and hyperparameter selection. The test set was kept untouched until final evaluation.

---

## Model Comparison

Several approaches were evaluated, including a mean baseline, Ridge Regression, and XGBoost.

### Appliances

Ridge Regression with strong regularization performed best among the tested approaches.

| Model | MAE | RMSE |
|---|---:|---:|
| Mean baseline | 53.97 | 92.39 |
| XGBoost | 74.72 | 107.68 |
| Ridge (α=1000) | **49.17** | **86.17** |

### Lights

A dedicated experiment compared temporal and environmental information.

| Model | MAE | RMSE |
|---|---:|---:|
| Mean baseline | 5.31 | 5.99 |
| Environment-only XGBoost | 5.82 | 7.22 |
| Combined XGBoost | 5.15 | 6.73 |
| Time-only XGBoost | **3.91** | **6.19** |

The results indicate that lighting consumption is substantially more schedule/time-driven than environment-driven.

---

## Final Models

| Target | Model | Features |
|---|---|---|
| Appliances | Ridge Regression (α=1000) | Environmental + temporal |
| lights | XGBoost | Temporal only |

The selected models were refitted using the combined training and validation data before final test evaluation.

---

## Final Test Performance

| Target | MAE | RMSE | sMAPE |
|---|---:|---:|---:|
| Appliances | **47.91** | **83.71** | 41.99% |
| lights | **3.22** | **5.92** | 146.95% |

MAE and RMSE are emphasized for `lights` because approximately **77.3% of lighting observations are zero**, making percentage-based metrics such as sMAPE unstable.

---

## Key Findings

### Appliances

Appliance consumption is influenced by both temporal and environmental variables. The model captures typical consumption patterns but tends to underestimate extreme demand spikes.

The observed maximum Appliances consumption is **1080**, while the 95th percentile is **330**.

### Lights

Lighting consumption is highly zero-inflated and strongly schedule-driven.

The strongest temporal drivers are:

1. `hour`
2. `day_of_week`

The time-only model substantially outperformed the environment-only model.

### `rv1` and `rv2`

`rv1` and `rv2` were explicitly tested rather than automatically retained. Adding them did not improve validation performance, so they were excluded from the final model schema.

---

## Business Recommendations

1. **Use separate modelling strategies for Appliances and lights.** Their predictive structures are materially different.

2. **Prioritize peak-demand monitoring for Appliances.** Extreme consumption events are difficult for the current model to predict accurately and may require a separate peak-alerting mechanism.

3. **Use schedule-based optimization for lighting.** Hour and day-of-week patterns suggest that automated schedules and occupancy-aware controls could reduce unnecessary lighting consumption.

4. **Collect occupancy and appliance-state data.** These variables could improve detection of abrupt consumption changes that cannot be explained by the current environmental and temporal features.

5. **Consider probabilistic forecasting in future versions.** Prediction intervals or quantile forecasts could be useful for energy-management decisions involving peak demand.

---

## API

The trained models are exposed through a FastAPI service.

### Start the API

```bash
uvicorn api.main:app --reload
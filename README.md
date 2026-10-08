# Smart Home Energy Usage Consumption Prediction

## Overview

This project predicts household energy consumption for two targets:

* `Appliances`
* `lights`

The solution covers data-quality assessment, exploratory analysis, time-based feature engineering, chronological model validation, model comparison, error analysis, and FastAPI deployment.

The dataset contains **19,735 observations** recorded at 10-minute intervals from **2016-01-11 to 2016-05-27**.

## Data Quality & Exploration

The dataset was checked for:

* Missing values
* Duplicate rows and timestamps
* Invalid timestamps
* Irregular time intervals
* Negative target values
* Extreme consumption observations

Results:

* No missing values
* No duplicate rows or timestamps
* No timestamp gaps
* Consistent 10-minute sampling
* No negative target values

Extreme observations were retained because they represent genuine high-consumption events.

`lights` is highly zero-inflated, with **77.3% of observations equal to zero**. Therefore, sMAPE is interpreted cautiously for this target.

Key exploratory findings:

* Appliance consumption varies substantially by time of day.
* Appliance usage peaks around the evening.
* Lighting usage is strongly concentrated around specific times.
* `lights` appears substantially more schedule-driven than environmentally driven.

## Feature Engineering

The final model schema contains **39 features**.

### Time features

* Hour and minute
* Day of week/month
* Month and week of year
* Weekday/weekend indicators
* Cyclical hour and day-of-week encodings

### Environmental features

* Indoor temperature and humidity sensors
* Outdoor temperature and humidity
* Atmospheric pressure
* Wind speed
* Visibility
* Dew point
* Mean indoor temperature
* Mean indoor humidity
* Indoor-outdoor temperature difference

The `date` column itself is not passed directly to the models.

`rv1` and `rv2` were explicitly evaluated and did not improve validation performance. They were therefore excluded from the final feature schema.

## Validation Strategy

Because the data is time ordered, **random train/test splitting was not used**.

| Split      | Percentage |   Rows |
| ---------- | ---------: | -----: |
| Train      |        70% | 13,814 |
| Validation |        15% |  2,960 |
| Test       |        15% |  2,961 |

The test set contains the latest observations and was reserved for final evaluation.

Metrics:

* MAE
* RMSE
* sMAPE

sMAPE is reported with caution for `lights` because of its large number of zero observations.

## Model Comparison

### Appliances

| Model         |       MAE |      RMSE |      sMAPE |
| ------------- | --------: | --------: | ---------: |
| Mean baseline |     53.97 |     92.39 |     50.68% |
| Ridge, α=1000 | **49.17** | **86.17** | **43.58%** |
| XGBoost       |     74.72 |    107.68 |     57.14% |

**Selected model: Ridge Regression, α=1000**

### Lights

| Model                    |      MAE |     RMSE |   sMAPE |
| ------------------------ | -------: | -------: | ------: |
| Mean baseline            |     5.31 |     5.99 | 184.27% |
| Time-only XGBoost        | **3.91** | **6.19** | 188.97% |
| Environment-only XGBoost |     5.82 |     7.22 | 180.74% |
| Combined XGBoost         |     5.15 |     6.73 | 182.91% |

**Selected model: XGBoost using time-based features only**

The time-only model's substantially lower MAE supports the conclusion that lighting consumption is primarily schedule-driven.

## Final Test Performance

The selected models were refitted using the combined training and validation data and evaluated once on the held-out test set.

| Target     | Model              |       MAE |      RMSE |       sMAPE |
| ---------- | ------------------ | --------: | --------: | ----------: |
| Appliances | Ridge, α=1000      | **47.91** | **83.71** |  **41.99%** |
| lights     | XGBoost, time-only |  **3.22** |  **5.92** | **146.95%** |

## Key Drivers & Error Analysis

Permutation importance identified time-of-day and indoor environmental variables as important drivers of appliance consumption. Important features included `hour_cos`, `T3`, `RH_2`, `hour_sin`, `RH_1`, and `RH_3`.

For `lights`, `hour` was the dominant feature, followed by `day_of_week`.

The Appliances model performs well on typical consumption levels but is conservative during extreme spikes. The Lights model captures normal schedule patterns but can miss abrupt lighting events.

## Business Recommendations

1. **Use time-aware forecasting:** household energy consumption has strong temporal structure.
2. **Model targets separately:** appliance consumption benefits from environmental and temporal features, while lighting is primarily schedule-driven.
3. **Monitor extreme peaks:** large appliance spikes are difficult to predict and may warrant separate anomaly monitoring.
4. **Add behavioral data:** occupancy, appliance states, holidays, and lagged consumption could improve future models.
5. **Use uncertainty estimates:** production systems should consider prediction intervals rather than relying only on point forecasts.

## FastAPI

The project includes a FastAPI inference service.

Start the API:

```bash
uvicorn api.main:app --reload
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Endpoints

**Health check**

```text
GET /health
```

Returns API status, loaded models, and the final feature count.

**Prediction**

```text
POST /predict
```

Accepts the final 39-feature schema and returns predictions for both targets:

```json
{
  "Appliances": 54.58591586682878,
  "lights": 0.0
}
```

The API loads the saved models from `models/` and automatically applies the appropriate feature subset to each model.

API screenshots are included in `screenshots/`.

## Repository Structure

```text
├── api/main.py
├── data/raw/energydata_complete.csv
├── models/
│   ├── appliances_model.joblib
│   ├── feature_schema.joblib
│   └── lights_model.joblib
├── notebooks/Smart_Home_Energy_Analysis.ipynb
├── outputs/
│   ├── test_predictions.csv
│   └── test_predictions.xlsx
├── screenshots/
├── .gitignore
├── README.md
└── requirements.txt
```

## Reproducibility

Install dependencies:

```bash
pip install -r requirements.txt
```

The complete analysis and modeling workflow is available in:

```text
notebooks/Smart_Home_Energy_Analysis.ipynb
```

## AI & Tools Disclosure

The project uses Python, pandas, NumPy, scikit-learn, XGBoost, Matplotlib, Seaborn, Joblib, FastAPI, Pydantic, and Jupyter.

AI assistance was used for coding guidance, debugging, analysis structuring, interpretation, and documentation. Model training, validation, evaluation, feature selection, final model selection, and API testing were executed and verified in the project environment.

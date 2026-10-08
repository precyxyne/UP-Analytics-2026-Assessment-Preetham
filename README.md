# Smart Home Energy Usage Consumption Prediction

## 1. Project Overview

This project predicts two household energy consumption targets:

* `Appliances`
* `lights`

The objective is to build reliable regression models using indoor environmental measurements, outdoor weather conditions, and engineered time-based features.

The project follows a chronological machine learning workflow designed to avoid data leakage and better reflect real-world forecasting conditions.

## 2. Dataset

The dataset contains **19,735 observations** recorded at 10-minute intervals from:

**2016-01-11 17:00:00 to 2016-05-27 18:00:00**

Original variables include:

* Indoor temperature and humidity sensors (`T1`-`T9`, `RH_1`-`RH_9`)
* Outdoor temperature and humidity
* Atmospheric pressure
* Wind speed
* Visibility
* Dew point
* Energy consumption targets
* `rv1` and `rv2`

## 3. Data Quality

The dataset was checked for:

* Invalid timestamps
* Missing values
* Duplicate rows
* Duplicate timestamps
* Irregular time intervals
* Negative target values
* Extreme target observations

Results:

* No missing values
* No duplicate rows
* No duplicate timestamps
* No timestamp gaps
* Consistent 10-minute sampling interval
* No negative target values

The extreme consumption observations were retained because they represent genuine high-usage events rather than automatically treating them as data errors.

`lights` is highly zero-inflated: approximately **77.3% of observations are zero**. Consequently, sMAPE is interpreted cautiously for this target.

## 4. Exploratory Analysis

Key findings from the exploratory analysis:

* `Appliances` has a median consumption of 60 and a mean of approximately 97.7.
* `Appliances` reaches substantially higher usage during high-demand periods, with the hourly average peaking around 18:00.
* `lights` has a median of zero and is strongly concentrated around specific times of day.
* Average lighting consumption peaks around 20:00.
* Appliance consumption is more strongly associated with indoor environmental conditions and time of day.
* Lighting consumption is predominantly schedule-driven.

## 5. Feature Engineering

The final feature set contains **39 features**.

### Time features

* Hour
* Minute
* Day of week
* Day of month
* Month
* Week of year
* Weekend/weekday indicators
* Cyclical hour features
* Cyclical day-of-week features

Cyclical encoding was used so that adjacent times such as 23:00 and 00:00 remain close in feature space.

### Environmental features

* Indoor temperature sensors
* Indoor humidity sensors
* Outdoor temperature
* Outdoor humidity
* Atmospheric pressure
* Wind speed
* Visibility
* Dew point
* Mean indoor temperature
* Mean indoor humidity
* Indoor-outdoor temperature difference

The `date` column itself is not passed directly to the models.

## 6. Validation Strategy

Random train/test splitting was deliberately avoided because the observations are time ordered.

The dataset was divided chronologically:

| Split      | Percentage | Observations |
| ---------- | ---------: | -----------: |
| Train      |        70% |       13,814 |
| Validation |        15% |        2,960 |
| Test       |        15% |        2,961 |

The final test set represents the latest portion of the time series and was not used for model selection.

## 7. Evaluation Metrics

Models were evaluated using:

* **MAE**: Mean Absolute Error
* **RMSE**: Root Mean Squared Error
* **sMAPE**: Symmetric Mean Absolute Percentage Error

sMAPE is reported for completeness but interpreted carefully for `lights` because approximately 77.3% of its observations are zero.

## 8. Model Comparison

A mean prediction baseline was established before evaluating machine learning models.

### Appliances

| Model         |       MAE |      RMSE |      sMAPE |
| ------------- | --------: | --------: | ---------: |
| Mean baseline |     53.97 |     92.39 |     50.68% |
| Ridge, α=1000 | **49.17** | **86.17** | **43.58%** |
| XGBoost       |     74.72 |    107.68 |     57.14% |

Ridge regression with `alpha=1000` produced the strongest validation performance for `Appliances`.

### Lights

| Model                    |      MAE |     RMSE |   sMAPE |
| ------------------------ | -------: | -------: | ------: |
| Mean baseline            |     5.31 |     5.99 | 184.27% |
| Time-only XGBoost        | **3.91** | **6.19** | 188.97% |
| Environment-only XGBoost |     5.82 |     7.22 | 180.74% |
| Combined XGBoost         |     5.15 |     6.73 | 182.91% |

For `lights`, the time-only model achieved the lowest MAE, supporting the conclusion that lighting consumption is primarily schedule-driven.

## 9. `rv1` and `rv2` Validation

The variables `rv1` and `rv2` were evaluated rather than automatically included simply because they were present in the dataset.

Their inclusion did not improve validation performance of the selected Ridge model. They were therefore excluded from the final feature schema.

This reduces unnecessary model inputs and avoids retaining variables without demonstrated predictive value.

## 10. Key Driver Analysis

Permutation importance was used to identify features that contributed most to validation performance.

For `Appliances`, important predictors included:

* `hour_cos`
* `T3`
* `RH_2`
* `hour_sin`
* `RH_1`
* `RH_3`
* `dow_sin`
* `T8`
* `RH_out`
* `T2`

The results indicate that both time-of-day patterns and indoor environmental conditions contribute materially to appliance consumption.

For `lights`, `hour` was by far the most important predictor, followed by `day_of_week`. This provides additional evidence that lighting usage is primarily driven by household schedules rather than environmental conditions.

## 11. Final Models

After validation and model selection:

### Appliances

**Ridge Regression (`alpha=1000`)**

### Lights

**XGBoost using time-based features**

The models were then refitted using the combined training and validation data before being evaluated once on the held-out test set.

## 12. Final Test Performance

| Target     | Final Model        |       MAE |      RMSE |       sMAPE |
| ---------- | ------------------ | --------: | --------: | ----------: |
| Appliances | Ridge, α=1000      | **47.91** | **83.71** |  **41.99%** |
| lights     | XGBoost, time-only |  **3.22** |  **5.92** | **146.95%** |

The final models were selected using only chronological training/validation data. The test set was reserved for the final performance estimate.

## 13. Error Diagnostics

The `Appliances` model performs well on typical consumption levels but is conservative during extreme spikes.

The largest appliance prediction errors occur during unusually high-consumption events where actual consumption substantially exceeds the model prediction.

The `lights` model captures normal time-of-day patterns but can miss abrupt lighting events. This is expected because the model intentionally prioritizes schedule-related features and does not have direct information about individual light-switching events.

Hourly error analysis also shows that appliance prediction errors become larger during high-demand daytime and evening periods.

## 14. Business Insights and Recommendations

### 1. Use time-aware forecasting

Household energy consumption has strong temporal structure. Operational forecasting systems should therefore explicitly model time-of-day and day-of-week effects.

### 2. Treat appliance and lighting consumption differently

The results support separate modeling strategies:

* Appliances: environmental + temporal variables
* Lights: primarily temporal variables

A single feature strategy is not necessarily optimal for both targets.

### 3. Monitor extreme consumption events

The appliance model performs substantially worse on extreme peaks. These events should be monitored separately because they may be operationally important despite being relatively infrequent.

### 4. Use prediction intervals in production

For an operational energy-management system, point predictions alone would be insufficient. Prediction intervals or probabilistic forecasting would help communicate uncertainty, particularly during unusual consumption spikes.

### 5. Consider additional behavioral features

Future versions could incorporate occupancy, appliance-specific states, holidays, room-level activity, and historical lag features to better capture sudden changes in household behavior.

## 15. FastAPI

The project includes a FastAPI inference service.

Start the API from the project root:

```bash
uvicorn api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Health Check

**Endpoint**

```text
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "models": [
    "Appliances",
    "lights"
  ],
  "feature_count": 39
}
```

### Prediction

**Endpoint**

```text
POST /predict
```

The request accepts the final feature schema used by the trained models.

Example structure:

```json
{
  "features": {
    "T1": 21.5,
    "T2": 20.5,
    "T3": 21.0,
    "T4": 20.8,
    "T5": 20.5,
    "T6": 7.5,
    "T7": 20.2,
    "T8": 20.0,
    "T9": 19.5,
    "RH_1": 40.0,
    "RH_2": 40.0,
    "RH_3": 40.0,
    "RH_4": 40.0,
    "RH_5": 50.0,
    "RH_6": 30.0,
    "RH_7": 40.0,
    "RH_8": 40.0,
    "RH_9": 40.0,
    "T_out": 7.0,
    "Press_mm_hg": 733.0,
    "RH_out": 80.0,
    "Windspeed": 2.0,
    "Visibility": 60.0,
    "Tdewpoint": 3.0,
    "hour": 18,
    "minute": 0,
    "day_of_week": 2,
    "day_of_month": 15,
    "month": 5,
    "week_of_year": 20,
    "is_weekend": 0,
    "is_weekday": 1,
    "hour_sin": -1.0,
    "hour_cos": -1.0,
    "dow_sin": 0.43,
    "dow_cos": -0.90,
    "mean_indoor_temperature": 20.5,
    "mean_indoor_humidity": 40.0,
    "indoor_outdoor_temp_diff": 13.5
  }
}
```

Example response:

```json
{
  "Appliances": 54.58591586682878,
  "lights": 0.0
}
```

The API loads the saved production models from the `models/` directory and automatically uses the appropriate feature subset for each target.

API screenshots are included in the `screenshots/` directory.

## 16. Project Structure

```text
UP-Analytics-2026-Assessment-Preetham/
│
├── api/
│   └── main.py
│
├── data/
│   └── raw/
│       └── energydata_complete.csv
│
├── models/
│   ├── appliances_model.joblib
│   ├── feature_schema.joblib
│   └── lights_model.joblib
│
├── notebooks/
│   └── Smart_Home_Energy_Analysis.ipynb
│
├── outputs/
│   ├── test_predictions.csv
│   └── test_predictions.xlsx
│
├── screenshots/
│   ├── api_health_1.png
│   ├── api_health_2.png
│   ├── api_predict_1.png
│   ├── api_predict_2.png
│   └── api_predict_3.png
│
├── .gitignore
├── README.md
└── requirements.txt
```

## 17. Running the Project

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the notebook:

```text
notebooks/Smart_Home_Energy_Analysis.ipynb
```

Run the API:

```bash
uvicorn api.main:app --reload
```

## 18. Outputs

The repository contains:

* Trained Appliances model
* Trained lights model
* Feature schema
* Test-set predictions in CSV format
* Test-set predictions in Excel format
* API implementation
* API screenshots
* Complete analysis notebook

## 19. AI and Tools Disclosure

The project was developed using Python and standard data-science and machine-learning libraries.

Key tools and packages include:

* Python
* pandas
* NumPy
* scikit-learn
* XGBoost
* Matplotlib
* Seaborn
* Joblib
* FastAPI
* Pydantic
* Jupyter

AI assistance was used during development for coding guidance, debugging, structuring the analysis, interpreting model results, and improving documentation. All data processing, model training, validation, evaluation, model selection, and API testing were executed and verified within the project environment.

The final analytical decisions, feature selection, validation strategy, model comparison, interpretation of results, and reported metrics were reviewed against the executed notebook outputs.

## 20. Conclusion

The project demonstrates an end-to-end machine learning workflow for smart-home energy prediction, from data-quality assessment and exploratory analysis through feature engineering, chronological validation, model selection, error analysis, and API deployment.

The results show that appliance consumption benefits from combining temporal and environmental information, while lighting consumption is substantially more schedule-driven. The final models provide a reproducible baseline for further development toward real-time household energy forecasting and management.

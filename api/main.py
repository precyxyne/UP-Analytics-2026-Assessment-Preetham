from pathlib import Path
from typing import Dict

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models"


# --------------------------------------------------
# Load models
# --------------------------------------------------

app_model = joblib.load(
    MODEL_PATH / "appliances_model.joblib"
)

light_model = joblib.load(
    MODEL_PATH / "lights_model.joblib"
)

feature_schema = joblib.load(
    MODEL_PATH / "feature_schema.joblib"
)

FEATURES = feature_schema["all_features"]
TIME_FEATURES = feature_schema["time_features"]


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Smart Home Energy Prediction API",
    description=(
        "API for predicting Appliances and lights energy consumption "
        "using trained machine learning models."
    ),
    version="1.0.0"
)


# --------------------------------------------------
# Request schema
# --------------------------------------------------

class PredictionRequest(BaseModel):
    features: Dict[str, float] = Field(
        ...,
        description="Final model feature values."
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "models": [
            "Appliances",
            "lights"
        ],
        "feature_count": len(FEATURES)
    }


# --------------------------------------------------
# Prediction endpoint
# --------------------------------------------------

@app.post("/predict")
def predict(request: PredictionRequest):

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in request.features
    ]

    if missing_features:
        return {
            "error": "Missing required features",
            "missing_features": missing_features
        }

    input_data = pd.DataFrame(
        [[request.features[feature] for feature in FEATURES]],
        columns=FEATURES
    )

    appliances_prediction = float(
        app_model.predict(input_data)[0]
    )

    lights_input = input_data[TIME_FEATURES]

    lights_prediction = float(
        light_model.predict(lights_input)[0]
    )

    # Energy consumption cannot be negative
    lights_prediction = max(
        0.0,
        lights_prediction
    )

    return {
        "Appliances": appliances_prediction,
        "lights": lights_prediction
    }
"""
Machine Learning Training Pipeline
=================================
Model: Random Forest Regressor for Traffic Demand Prediction
Target: traffic_demand (PCU/hr)
Evaluation: MAE, RMSE, R² Score
Persistence: Joblib

Design Principles:
- Strict train-test split (80/20) with seed 42 to prevent data leakage.
- Full Scikit-learn Pipeline incorporating OneHotEncoder and ColumnTransformer
  so that incoming inference records can be passed directly as raw dictionaries or DataFrames.
- Feature importance analysis and evaluation metric logging to JSON.
"""

import json
import os
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def train_traffic_model(
    data_path: str = "data/traffic_dataset.csv",
    model_dir: str = "models",
    random_seed: int = 42
):
    """
    Train, evaluate, and save Random Forest Regressor for Traffic Demand.
    """
    os.makedirs(model_dir, exist_ok=True)

    print(f"[*] Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)

    features = [
        "road",
        "vehicle_count",
        "traffic_density",
        "queue_length",
        "avg_speed",
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "prev_waiting_time"
    ]
    target = "traffic_demand"

    X = df[features]
    y = df[target]

    categorical_features = ["road"]
    numerical_features = [
        "vehicle_count",
        "traffic_density",
        "queue_length",
        "avg_speed",
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "prev_waiting_time"
    ]

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(drop=None, handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", StandardScaler(), numerical_features)
        ],
        remainder="passthrough"
    )

    # Scikit-Learn Pipeline
    model_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=120,
                    max_depth=14,
                    min_samples_split=4,
                    min_samples_leaf=2,
                    random_state=random_seed,
                    n_jobs=-1
                )
            )
        ]
    )

    # Train / Test split (80 / 20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_seed
    )

    print(f"[*] Training Random Forest Regressor on {len(X_train)} samples...")
    model_pipeline.fit(X_train, y_train)

    print(f"[*] Evaluating model on test set ({len(X_test)} samples)...")
    y_pred = model_pipeline.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    print(f"\n================ MODEL EVALUATION METRICS ================")
    print(f"  Mean Absolute Error (MAE)       : {mae:.2f} PCU/hr")
    print(f"  Root Mean Squared Error (RMSE)  : {rmse:.2f} PCU/hr")
    print(f"  R² Score (Coefficient of Det.) : {r2:.4f} ({r2*100:.2f}%)")
    print(f"==========================================================\n")

    # Feature Importance extraction
    onehot_encoder = model_pipeline.named_steps["preprocessor"].named_transformers_["cat"]
    encoded_cat_names = list(onehot_encoder.get_feature_names_out(categorical_features))
    all_feature_names = encoded_cat_names + numerical_features

    importances = model_pipeline.named_steps["regressor"].feature_importances_
    feat_importance_dict = {
        name: round(float(imp), 4)
        for name, imp in sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)
    }

    # Save Pipeline
    model_file = os.path.join(model_dir, "traffic_rf_model.joblib")
    joblib.dump(model_pipeline, model_file)
    print(f"[+] Serialized model saved to: {model_file}")

    # Metadata & Metrics JSON
    metadata = {
        "model_type": "RandomForestRegressor",
        "algorithm": "Scikit-Learn Random Forest",
        "n_estimators": 120,
        "max_depth": 14,
        "random_seed": random_seed,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4),
        "target_variable": target,
        "features": features,
        "feature_importances": feat_importance_dict,
        "training_timestamp": datetime.now().isoformat(),
        "notes": "Predicts short-term incoming traffic demand (PCU/hr) for dynamic Webster optimization."
    }

    meta_file = os.path.join(model_dir, "model_metadata.json")
    with open(meta_file, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"[+] Model metadata exported to: {meta_file}")

    return metadata


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_csv = os.path.join(base_dir, "data", "traffic_dataset.csv")
    model_path = os.path.join(base_dir, "models")
    train_traffic_model(data_path=data_csv, model_dir=model_path, random_seed=42)

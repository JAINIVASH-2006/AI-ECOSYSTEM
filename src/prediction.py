"""
EcoRestore AI — Prediction Module
===================================
Load saved models and predict priority score / class for new data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from config.config import MODELS_DIR
from config.thresholds import PRIORITY_CLASSES
from src.model_training import FEATURE_COLUMNS


def _load_model(filename: str):
    """Load a model from the models directory."""
    path = MODELS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Select and order feature columns for prediction."""
    cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    if not cols:
        raise ValueError("No feature columns found in data for prediction.")
    return df[cols]


def predict_classification(
    df: pd.DataFrame,
    model_name: str = "Random Forest",
) -> pd.DataFrame:
    """Predict priority class for new data.

    Parameters
    ----------
    df : pd.DataFrame
        Environmental data with feature columns.
    model_name : str
        One of: ``"Random Forest"``, ``"XGBoost"``, ``"Logistic Regression"``.

    Returns
    -------
    pd.DataFrame
        Original data with ``predicted_class`` and ``prediction_probabilities``.
    """
    safe_name = model_name.lower().replace(" ", "_")
    model = _load_model(f"clf_{safe_name}.joblib")
    le = _load_model("label_encoder.joblib")

    X = _prepare_features(df)
    y_pred = model.predict(X)
    result = df.copy()
    result["predicted_class"] = le.inverse_transform(y_pred)

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        result["prediction_confidence"] = np.max(proba, axis=1).round(4)
        # model.classes_ holds the encoded integer indices the model knows;
        # use them to index proba columns and map back to human-readable names.
        for col_idx, enc_label in enumerate(model.classes_):
            cls_name = le.inverse_transform([enc_label])[0]
            result[f"prob_{cls_name}"] = proba[:, col_idx].round(4)
    else:
        result["prediction_confidence"] = np.nan

    return result


def predict_regression(
    df: pd.DataFrame,
    model_name: str = "Random Forest",
) -> pd.DataFrame:
    """Predict priority score for new data.

    Parameters
    ----------
    df : pd.DataFrame
        Environmental data with feature columns.
    model_name : str
        One of: ``"Random Forest"``, ``"XGBoost"``, ``"Linear Regression"``.

    Returns
    -------
    pd.DataFrame
        Original data with ``predicted_score``.
    """
    safe_name = model_name.lower().replace(" ", "_")
    model = _load_model(f"reg_{safe_name}.joblib")

    X = _prepare_features(df)
    y_pred = model.predict(X)
    result = df.copy()
    result["predicted_score"] = np.clip(y_pred, 0, 100).round(2)
    return result


def get_available_models() -> Dict[str, List[str]]:
    """List trained model files available in the models directory.

    Returns
    -------
    dict
        ``{"classification": [...], "regression": [...]}``.
    """
    clf_models: List[str] = []
    reg_models: List[str] = []

    if not MODELS_DIR.exists():
        return {"classification": clf_models, "regression": reg_models}

    for p in MODELS_DIR.glob("*.joblib"):
        name = p.stem
        if name.startswith("clf_"):
            display = name.replace("clf_", "").replace("_", " ").title()
            clf_models.append(display)
        elif name.startswith("reg_"):
            display = name.replace("reg_", "").replace("_", " ").title()
            reg_models.append(display)

    return {"classification": clf_models, "regression": reg_models}

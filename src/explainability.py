"""
EcoRestore AI — Explainability Module
=======================================
Feature importance display and per-zone explanations.
Optional SHAP integration (loaded via try/except).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config.thresholds import INDICATOR_SEVERITY


def _severity_label(value: float) -> str:
    """Return a severity label for a 0–100 indicator value."""
    for label, (lo, hi) in INDICATOR_SEVERITY.items():
        if lo <= value <= hi:
            return label
    return "UNKNOWN"


def get_feature_importance(
    model,
    feature_names: List[str],
    top_n: int = 10,
) -> List[Tuple[str, float]]:
    """Extract feature importance from a trained model.

    Parameters
    ----------
    model
        A scikit-learn-compatible model with ``feature_importances_`` or ``coef_``.
    feature_names : list
        Column names matching the model features.
    top_n : int
        Number of top features to return.

    Returns
    -------
    list of (feature_name, importance)
        Sorted descending by importance.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).mean(axis=0) if model.coef_.ndim > 1 else np.abs(model.coef_)
    else:
        return []

    pairs = sorted(
        zip(feature_names, importances),
        key=lambda x: x[1],
        reverse=True,
    )
    return pairs[:top_n]


def explain_zone(
    zone_row: pd.Series,
    indicator_cols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Produce a human-readable explanation for a single zone's priority.

    Parameters
    ----------
    zone_row : pd.Series
        A row from the processed DataFrame (must contain indicator columns).
    indicator_cols : list, optional
        Indicator columns to examine.

    Returns
    -------
    dict
        ``{zone_id, priority_score, priority_class, factors: [{name, value, severity, contribution}]}``.
    """
    if indicator_cols is None:
        indicator_cols = [
            "vegetation_stress",
            "soil_degradation_risk",
            "water_stress",
            "habitat_degradation",
            "biodiversity_risk",
            "human_pressure_index",
        ]

    zone_id = zone_row.get("zone_id", "Unknown")
    priority_score = zone_row.get("priority_score", 0)
    priority_class = zone_row.get("priority_class", "N/A")

    factors = []
    for col in indicator_cols:
        val = zone_row.get(col, 50.0)
        severity = _severity_label(val)
        # Contribution level relative to thresholds
        if val >= 76:
            contribution = "Very High"
        elif val >= 51:
            contribution = "High"
        elif val >= 26:
            contribution = "Moderate"
        else:
            contribution = "Low"
        factors.append({
            "name": col.replace("_", " ").title(),
            "column": col,
            "value": round(float(val), 2),
            "severity": severity,
            "contribution": contribution,
        })

    # Sort by value descending (worst first)
    factors.sort(key=lambda f: f["value"], reverse=True)

    return {
        "zone_id": zone_id,
        "priority_score": round(float(priority_score), 2),
        "priority_class": priority_class,
        "factors": factors,
    }


def explain_zones_batch(
    df: pd.DataFrame,
    indicator_cols: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Explain multiple zones."""
    return [explain_zone(df.iloc[i], indicator_cols) for i in range(len(df))]


# ------------------------------------------------------------------ #
# Optional SHAP Integration
# ------------------------------------------------------------------ #

def get_shap_explanation(
    model,
    X: pd.DataFrame,
    zone_index: int = 0,
) -> Optional[Dict[str, Any]]:
    """Generate a SHAP explanation for a single zone.

    Returns None if SHAP is not installed.
    """
    try:
        import shap
    except ImportError:
        return None

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X.iloc[[zone_index]])

        # For classification models, shap_values may be a list of arrays
        if isinstance(shap_values, list):
            # Use the predicted class's SHAP values
            pred_class = int(model.predict(X.iloc[[zone_index]])[0])
            sv = shap_values[pred_class][0]
        else:
            sv = shap_values[0]

        feature_shap = dict(zip(X.columns, [round(float(v), 4) for v in sv]))
        sorted_features = sorted(feature_shap.items(), key=lambda x: abs(x[1]), reverse=True)

        return {
            "base_value": round(float(explainer.expected_value if np.isscalar(explainer.expected_value) else explainer.expected_value[0]), 4),
            "feature_shap": dict(sorted_features),
            "top_positive": [(k, v) for k, v in sorted_features if v > 0][:5],
            "top_negative": [(k, v) for k, v in sorted_features if v < 0][:5],
        }
    except Exception:
        return None

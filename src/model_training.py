"""
EcoRestore AI — Model Training
================================
Train classification and regression models for restoration priority prediction.

Models:
    - Random Forest (classifier + regressor)
    - XGBoost (classifier + regressor)
    - Logistic Regression (baseline classifier)
    - Linear Regression (baseline regressor)

**Important**: The target variable (``priority_score`` / ``priority_class``)
is derived from the weighted baseline formula.  The ML models learn to
approximate this baseline reference target — they do *not* independently
discover a restoration priority.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder

from config.config import (
    CV_FOLDS,
    MODELS_DIR,
    RANDOM_STATE,
    RF_MAX_DEPTH,
    RF_MIN_SAMPLES_LEAF,
    RF_MIN_SAMPLES_SPLIT,
    RF_N_ESTIMATORS,
    TEST_SIZE,
    XGB_LEARNING_RATE,
    XGB_MAX_DEPTH,
    XGB_N_ESTIMATORS,
    XGB_SUBSAMPLE,
)
from config.thresholds import PRIORITY_CLASSES

warnings.filterwarnings("ignore", category=UserWarning)

# Features used by the ML models (raw environmental + indicators,
# excluding target-leak columns).
FEATURE_COLUMNS = [
    "vegetation_index",
    "soil_degradation",
    "rainfall",
    "water_availability",
    "land_use_change",
    "habitat_quality",
    "biodiversity_index",
    "human_pressure",
    "elevation",
    "slope",
    "forest_cover",
    "drought_index",
]


def _ensure_models_dir() -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    return MODELS_DIR


def _get_features(df: pd.DataFrame) -> pd.DataFrame:
    """Select available feature columns from *df*."""
    cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    if not cols:
        raise ValueError("No feature columns found in data.")
    return df[cols]


# ------------------------------------------------------------------ #
# Train / Test Split
# ------------------------------------------------------------------ #

def split_data(
    df: pd.DataFrame,
    target_col: str = "priority_class",
    test_size: float = TEST_SIZE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split into train/test sets, returning (X_train, X_test, y_train, y_test)."""
    X = _get_features(df)
    y = df[target_col].copy()

    stratify = y if target_col == "priority_class" else None
    return train_test_split(
        X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=stratify,
    )


# ------------------------------------------------------------------ #
# Model Builders
# ------------------------------------------------------------------ #

def build_random_forest_clf() -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        min_samples_split=RF_MIN_SAMPLES_SPLIT,
        min_samples_leaf=RF_MIN_SAMPLES_LEAF,
        random_state=RANDOM_STATE,
        n_jobs=None,
    )


def build_random_forest_reg() -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        min_samples_split=RF_MIN_SAMPLES_SPLIT,
        min_samples_leaf=RF_MIN_SAMPLES_LEAF,
        random_state=RANDOM_STATE,
        n_jobs=None,
    )


def build_xgboost_clf():
    from xgboost import XGBClassifier
    return XGBClassifier(
        n_estimators=XGB_N_ESTIMATORS,
        max_depth=XGB_MAX_DEPTH,
        learning_rate=XGB_LEARNING_RATE,
        subsample=XGB_SUBSAMPLE,
        random_state=RANDOM_STATE,
        use_label_encoder=False,
        eval_metric="mlogloss",
        verbosity=0,
    )


def build_xgboost_reg():
    from xgboost import XGBRegressor
    return XGBRegressor(
        n_estimators=XGB_N_ESTIMATORS,
        max_depth=XGB_MAX_DEPTH,
        learning_rate=XGB_LEARNING_RATE,
        subsample=XGB_SUBSAMPLE,
        random_state=RANDOM_STATE,
        verbosity=0,
    )


def build_logistic_regression() -> LogisticRegression:
    return LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        multi_class="multinomial",
        solver="lbfgs",
    )


def build_linear_regression() -> LinearRegression:
    return LinearRegression()


# ------------------------------------------------------------------ #
# Training Orchestration
# ------------------------------------------------------------------ #

def train_classification_models(
    df: pd.DataFrame,
) -> Dict[str, Dict[str, Any]]:
    """Train all classification models and return results.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain feature columns and ``priority_class``.

    Returns
    -------
    dict
        ``{model_name: {model, metrics, label_encoder, feature_names}}``.
    """
    X_train, X_test, y_train, y_test = split_data(df, target_col="priority_class")

    # Encode labels — fit ONLY on classes present in the data so that the
    # encoded integers are always consecutive 0..n-1 (required by XGBoost).
    # We sort by PRIORITY_CLASSES order so the encoding is deterministic and
    # human-readable (LOW < MODERATE < HIGH < CRITICAL when all present).
    present_classes = [c for c in PRIORITY_CLASSES if c in y_train.unique()]
    le = LabelEncoder()
    le.fit(present_classes)            # stable, data-driven, consecutive labels
    y_train_enc = le.transform(y_train)
    y_test_enc = le.transform(y_test)

    models = {
        "Random Forest": build_random_forest_clf(),
        "XGBoost": build_xgboost_clf(),
        "Logistic Regression": build_logistic_regression(),
    }

    results: Dict[str, Dict[str, Any]] = {}
    model_dir = _ensure_models_dir()

    for name, model in models.items():
        model.fit(X_train, y_train_enc)
        y_pred = model.predict(X_test)

        # Metrics
        metrics: Dict[str, Any] = {
            "accuracy": round(accuracy_score(y_test_enc, y_pred), 4),
            "precision_weighted": round(
                precision_score(y_test_enc, y_pred, average="weighted", zero_division=0), 4
            ),
            "recall_weighted": round(
                recall_score(y_test_enc, y_pred, average="weighted", zero_division=0), 4
            ),
            "f1_weighted": round(
                f1_score(y_test_enc, y_pred, average="weighted", zero_division=0), 4
            ),
            "confusion_matrix": confusion_matrix(
                y_test_enc, y_pred,
                labels=list(range(len(le.classes_)))
            ).tolist(),
            "classification_report": classification_report(
                y_test_enc, y_pred,
                target_names=list(le.classes_),
                output_dict=True,
                zero_division=0,
                labels=range(len(le.classes_)),
            ),
        }

        # ROC-AUC (one-vs-rest) — only if predict_proba available
        if hasattr(model, "predict_proba"):
            try:
                y_proba = model.predict_proba(X_test)
                metrics["roc_auc"] = round(
                    roc_auc_score(y_test_enc, y_proba, multi_class="ovr", average="weighted"),
                    4,
                )
            except Exception:
                metrics["roc_auc"] = None
        else:
            metrics["roc_auc"] = None

        # Cross-validation score
        try:
            cv_scores = cross_val_score(model, X_train, y_train_enc, cv=CV_FOLDS, scoring="accuracy")
            metrics["cv_mean"] = round(float(cv_scores.mean()), 4)
            metrics["cv_std"] = round(float(cv_scores.std()), 4)
        except Exception:
            metrics["cv_mean"] = None
            metrics["cv_std"] = None

        # Feature importance
        if hasattr(model, "feature_importances_"):
            metrics["feature_importance"] = dict(
                zip(X_train.columns, [round(float(v), 4) for v in model.feature_importances_])
            )
        elif hasattr(model, "coef_"):
            # For logistic regression — average absolute coefficients across classes
            avg_coef = np.abs(model.coef_).mean(axis=0)
            metrics["feature_importance"] = dict(
                zip(X_train.columns, [round(float(v), 4) for v in avg_coef])
            )

        # Save model
        safe_name = name.lower().replace(" ", "_")
        model_path = model_dir / f"clf_{safe_name}.joblib"
        joblib.dump(model, model_path)

        results[name] = {
            "model": model,
            "metrics": metrics,
            "label_encoder": le,
            "feature_names": list(X_train.columns),
            "model_path": str(model_path),
            "y_test": y_test_enc,
            "y_pred": y_pred,
        }

    # Save label encoder
    joblib.dump(le, model_dir / "label_encoder.joblib")

    return results


def train_regression_models(
    df: pd.DataFrame,
) -> Dict[str, Dict[str, Any]]:
    """Train all regression models and return results.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain feature columns and ``priority_score``.

    Returns
    -------
    dict
        ``{model_name: {model, metrics, feature_names}}``.
    """
    X_train, X_test, y_train, y_test = split_data(df, target_col="priority_score")

    models = {
        "Random Forest": build_random_forest_reg(),
        "XGBoost": build_xgboost_reg(),
        "Linear Regression": build_linear_regression(),
    }

    results: Dict[str, Dict[str, Any]] = {}
    model_dir = _ensure_models_dir()

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        metrics: Dict[str, Any] = {
            "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
            "rmse": round(rmse, 4),
            "r2": round(float(r2_score(y_test, y_pred)), 4),
        }

        # Cross-validation
        try:
            cv_scores = cross_val_score(
                model, X_train, y_train, cv=CV_FOLDS, scoring="r2",
            )
            metrics["cv_mean_r2"] = round(float(cv_scores.mean()), 4)
            metrics["cv_std_r2"] = round(float(cv_scores.std()), 4)
        except Exception:
            metrics["cv_mean_r2"] = None
            metrics["cv_std_r2"] = None

        # Feature importance
        if hasattr(model, "feature_importances_"):
            metrics["feature_importance"] = dict(
                zip(X_train.columns, [round(float(v), 4) for v in model.feature_importances_])
            )
        elif hasattr(model, "coef_"):
            metrics["feature_importance"] = dict(
                zip(X_train.columns, [round(float(v), 4) for v in np.abs(model.coef_)])
            )

        safe_name = name.lower().replace(" ", "_")
        model_path = model_dir / f"reg_{safe_name}.joblib"
        joblib.dump(model, model_path)

        results[name] = {
            "model": model,
            "metrics": metrics,
            "feature_names": list(X_train.columns),
            "model_path": str(model_path),
            "y_test": np.array(y_test),
            "y_pred": y_pred,
        }

    return results


def train_all_models(df: pd.DataFrame) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Train both classification and regression models.

    Returns
    -------
    dict
        ``{"classification": {...}, "regression": {...}}``.
    """
    return {
        "classification": train_classification_models(df),
        "regression": train_regression_models(df),
    }


def get_best_model(
    results: Dict[str, Dict[str, Any]],
    metric: str = "accuracy",
) -> str:
    """Return the name of the best model by the given metric."""
    best_name = None
    best_val = -np.inf
    for name, info in results.items():
        val = info["metrics"].get(metric)
        if val is not None and val > best_val:
            best_val = val
            best_name = name
    return best_name or list(results.keys())[0]

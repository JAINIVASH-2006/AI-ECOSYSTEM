"""
EcoRestore AI — Priority Engine
=================================
Compute the baseline Restoration Priority Score (0–100) using configurable
weighted indicators, and classify each zone into a priority category.

Score interpretation: **HIGH = NEEDS RESTORATION** (critical).

Classification boundaries (from ``config/thresholds.py``):

    0–25   LOW
    26–50  MODERATE
    51–75  HIGH
    76–100 CRITICAL
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

from config.thresholds import PRIORITY_THRESHOLDS, PRIORITY_WEIGHTS


def compute_priority_score(
    df: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> pd.Series:
    """Compute the weighted Restoration Priority Score (0–100).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain indicator columns matching the keys in *weights*.
    weights : dict, optional
        ``{indicator_column: weight}``.  Defaults to ``PRIORITY_WEIGHTS``.

    Returns
    -------
    pd.Series
        Priority score for each row, rounded to 2 decimals.
    """
    if weights is None:
        weights = PRIORITY_WEIGHTS

    # Validate weights sum ≈ 1.0
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(
            f"Priority weights must sum to 1.0 (got {total_weight:.4f})."
        )

    score = pd.Series(0.0, index=df.index)
    for col, w in weights.items():
        if col in df.columns:
            score += w * df[col]
        else:
            # Fall back to neutral 50 if indicator is missing
            score += w * 50.0

    return score.clip(0, 100).round(2)


def classify_priority(score: pd.Series) -> pd.Series:
    """Map a numeric priority score to a category string.

    Uses threshold ranges from ``PRIORITY_THRESHOLDS``.

    Parameters
    ----------
    score : pd.Series
        Priority scores (0–100).

    Returns
    -------
    pd.Series
        Category labels (LOW / MODERATE / HIGH / CRITICAL).
    """
    if score.isna().any() or not score.between(0, 100).all():
        raise ValueError("Priority scores must be finite values from 0 to 100.")
    # Continuous cutoffs include decimal values (e.g. 50.5 is HIGH).
    return pd.Series(
        np.select([score <= 25, score <= 50, score <= 75],
                  ["LOW", "MODERATE", "HIGH"], default="CRITICAL"),
        index=score.index,
    )


def compute_priority(
    df: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Attach priority score and class to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Must already contain environmental indicator columns.
    weights : dict, optional
        Custom weights (defaults to ``PRIORITY_WEIGHTS``).

    Returns
    -------
    pd.DataFrame
        Original columns plus ``priority_score`` and ``priority_class``.
    """
    result = df.copy()
    result["priority_score"] = compute_priority_score(df, weights)
    result["priority_class"] = classify_priority(result["priority_score"])
    return result


def get_priority_summary(df: pd.DataFrame) -> Dict[str, object]:
    """Return a summary of priority distribution.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ``priority_score`` and ``priority_class``.

    Returns
    -------
    dict
        Counts per class, average score, highest/lowest zone, etc.
    """
    if "priority_class" not in df.columns or "priority_score" not in df.columns:
        return {}

    class_counts = df["priority_class"].value_counts().to_dict()
    # Ensure all classes present
    for cls in PRIORITY_THRESHOLDS:
        class_counts.setdefault(cls, 0)

    highest_idx = df["priority_score"].idxmax()
    lowest_idx = df["priority_score"].idxmin()
    zone_col = "zone_id" if "zone_id" in df.columns else None

    return {
        "total_zones": len(df),
        "class_counts": class_counts,
        "average_score": round(float(df["priority_score"].mean()), 2),
        "median_score": round(float(df["priority_score"].median()), 2),
        "max_score": round(float(df["priority_score"].max()), 2),
        "min_score": round(float(df["priority_score"].min()), 2),
        "highest_zone": df.at[highest_idx, zone_col] if zone_col else str(highest_idx),
        "lowest_zone": df.at[lowest_idx, zone_col] if zone_col else str(lowest_idx),
    }

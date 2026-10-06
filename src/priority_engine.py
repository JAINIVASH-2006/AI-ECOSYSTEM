"""
EcoRestore AI — Priority Engine
=================================
Compute the baseline Restoration Priority Score (0–100) using configurable
weighted indicators, and classify each zone into a 5-tier priority category.

Score interpretation: **HIGH = NEEDS RESTORATION** (critical).

Classification boundaries (5 tiers):
    0–20   VERY_LOW  (Stable, minimal intervention needed)
    21–40  LOW       (Minor conservation needed)
    41–60  MODERATE  (Targeted restoration recommended)
    61–80  HIGH      (Substantial restoration required)
    81–100 CRITICAL  (Immediate urgent ecological action needed)
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
    """Compute the weighted Restoration Priority Score (0–100)."""
    if weights is None:
        weights = PRIORITY_WEIGHTS

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
            score += w * 50.0

    return score.clip(0, 100).round(2)


def classify_priority(score: pd.Series) -> pd.Series:
    """Map a numeric priority score to 5-tier category string:
    VERY_LOW (0-20), LOW (21-40), MODERATE (41-60), HIGH (61-80), CRITICAL (81-100).
    """
    if score.isna().any() or not score.between(0, 100).all():
        raise ValueError("Priority scores must be finite values from 0 to 100.")
    
    return pd.Series(
        np.select(
            [score <= 20, score <= 40, score <= 60, score <= 80],
            ["VERY_LOW", "LOW", "MODERATE", "HIGH"],
            default="CRITICAL"
        ),
        index=score.index,
    )


def compute_priority(
    df: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Attach priority score and 5-tier priority class to the DataFrame."""
    out = df.copy()
    out["priority_score"] = compute_priority_score(out, weights)
    out["priority_class"] = classify_priority(out["priority_score"])
    return out

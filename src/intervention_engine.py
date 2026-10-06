"""
EcoRestore AI — Intervention Engine
======================================
Rule-based ecological restoration intervention recommendation.

For every zone, calculates a suitability score (0–100) for each of the
9 supported intervention types.  Returns primary, secondary, and supporting
interventions with human-readable reasons.

Suitability interpretation: **HIGH = MORE SUITABLE**.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from config.thresholds import (
    INTERVENTION_CONDITION_MODIFIERS,
    INTERVENTION_RULES,
    INTERVENTION_TYPES,
)


def _evaluate_condition(value: float, operator: str, threshold: float) -> bool:
    """Evaluate a single condition (e.g., forest_cover < 30)."""
    if operator == "<":
        return value < threshold
    elif operator == ">":
        return value > threshold
    elif operator == "<=":
        return value <= threshold
    elif operator == ">=":
        return value >= threshold
    elif operator == "==":
        return value == threshold
    return False


def compute_intervention_suitability(
    zone: pd.Series,
) -> List[Dict[str, Any]]:
    """Compute suitability scores for all interventions for a single zone.

    Parameters
    ----------
    zone : pd.Series
        A row of processed data containing indicator columns and raw features.

    Returns
    -------
    list of dict
        Each dict: ``{intervention, score, reasons}``, sorted by score descending.
    """
    results: List[Dict[str, Any]] = []

    for intervention in INTERVENTION_TYPES:
        rules = INTERVENTION_RULES.get(intervention, {})
        reasons: List[str] = []

        # Weighted sum of indicators
        score = 0.0
        for indicator, weight in rules.items():
            val = zone.get(indicator, 50.0)
            score += weight * val
            if val >= 60:
                nice_name = indicator.replace("_", " ").title()
                reasons.append(f"{nice_name} is elevated ({val:.0f}/100)")

        # Apply condition modifiers from raw features
        modifiers = INTERVENTION_CONDITION_MODIFIERS.get(intervention, [])
        for col, op, threshold, bonus in modifiers:
            raw_val = zone.get(col, 50.0)
            if _evaluate_condition(raw_val, op, threshold):
                score += bonus
                col_nice = col.replace("_", " ").title()
                reasons.append(
                    f"{col_nice} ({raw_val:.1f}) meets condition ({op} {threshold})"
                )

        score = float(np.clip(score, 0, 100))

        if not reasons:
            reasons.append("General environmental conditions support this intervention.")

        results.append({
            "intervention": intervention,
            "score": round(score, 2),
            "reasons": reasons,
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_zone_interventions(
    zone: pd.Series,
) -> Dict[str, Any]:
    """Return structured intervention recommendations for a zone.

    Returns
    -------
    dict
        ``{primary, secondary, supporting, all_interventions}``.
    """
    all_interventions = compute_intervention_suitability(zone)

    primary = all_interventions[0] if len(all_interventions) > 0 else None
    secondary = all_interventions[1] if len(all_interventions) > 1 else None
    supporting = all_interventions[2] if len(all_interventions) > 2 else None

    return {
        "primary": primary,
        "secondary": secondary,
        "supporting": supporting,
        "all_interventions": all_interventions,
    }


def compute_interventions_for_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Attach top-3 intervention recommendations to every row.

    Parameters
    ----------
    df : pd.DataFrame
        Processed data with indicator columns.

    Returns
    -------
    pd.DataFrame
        Original columns plus ``primary_intervention``, ``primary_score``,
        ``secondary_intervention``, ``secondary_score``,
        ``supporting_intervention``, ``supporting_score``.
    """
    result = df.copy()
    primaries, primary_scores = [], []
    secondaries, secondary_scores = [], []
    supportings, supporting_scores = [], []

    for _, row in df.iterrows():
        rec = get_zone_interventions(row)
        primaries.append(rec["primary"]["intervention"] if rec["primary"] else "N/A")
        primary_scores.append(rec["primary"]["score"] if rec["primary"] else 0)
        secondaries.append(rec["secondary"]["intervention"] if rec["secondary"] else "N/A")
        secondary_scores.append(rec["secondary"]["score"] if rec["secondary"] else 0)
        supportings.append(rec["supporting"]["intervention"] if rec["supporting"] else "N/A")
        supporting_scores.append(rec["supporting"]["score"] if rec["supporting"] else 0)

    result["primary_intervention"] = primaries
    result["primary_intervention_score"] = primary_scores
    result["secondary_intervention"] = secondaries
    result["secondary_intervention_score"] = secondary_scores
    result["supporting_intervention"] = supportings
    result["supporting_intervention_score"] = supporting_scores

    return result

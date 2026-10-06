"""
EcoRestore AI — Simulation Module
====================================
What-if scenario engine: users modify environmental parameters (% changes)
and the system recalculates indicators, priority score, priority class,
and intervention suitability.

Supports saving and comparing multiple named scenarios.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.feature_engineering import compute_all_indicators
from src.intervention_engine import get_zone_interventions
from src.priority_engine import classify_priority, compute_priority_score


def apply_scenario(
    zone: pd.Series,
    modifications: Dict[str, float],
) -> pd.Series:
    """Apply percentage modifications to a zone's raw features.

    Parameters
    ----------
    zone : pd.Series
        Original zone data (raw features).
    modifications : dict
        ``{column: percent_change}``  e.g. ``{"vegetation_index": +15}``
        means increase vegetation_index by 15 %.

    Returns
    -------
    pd.Series
        Modified zone data (raw features updated, but indicators NOT yet
        recomputed — call ``simulate_zone`` for the full pipeline).
    """
    modified = zone.copy()
    for col, pct in modifications.items():
        if col in modified.index:
            original = float(modified[col])
            new_val = original * (1 + pct / 100.0)
            modified[col] = np.clip(new_val, 0, 100)
    return modified


def simulate_zone(
    zone: pd.Series,
    modifications: Dict[str, float],
) -> Dict[str, Any]:
    """Run a full what-if simulation for a single zone.

    Parameters
    ----------
    zone : pd.Series
        Original row from processed data (with indicators & priority).
    modifications : dict
        ``{raw_feature_column: percent_change}``.

    Returns
    -------
    dict
        Before/after comparison including indicators, priority, interventions.
    """
    # --- Before ---
    before_indicators = {
        "vegetation_stress": zone.get("vegetation_stress", 50),
        "soil_degradation_risk": zone.get("soil_degradation_risk", 50),
        "water_stress": zone.get("water_stress", 50),
        "habitat_degradation": zone.get("habitat_degradation", 50),
        "biodiversity_risk": zone.get("biodiversity_risk", 50),
        "human_pressure_index": zone.get("human_pressure_index", 50),
        "overall_degradation": zone.get("overall_degradation", 50),
    }
    before_score = zone.get("priority_score", 50)
    before_class = zone.get("priority_class", "MODERATE")
    before_interventions = get_zone_interventions(zone)

    # --- Apply modifications ---
    modified_zone = apply_scenario(zone, modifications)

    # Recalculate indicators via DataFrame path
    mod_df = pd.DataFrame([modified_zone])
    mod_df = compute_all_indicators(mod_df)
    after_row = mod_df.iloc[0]

    after_score = float(compute_priority_score(mod_df).iloc[0])
    after_class = str(classify_priority(pd.Series([after_score])).iloc[0])
    after_interventions = get_zone_interventions(after_row)

    after_indicators = {
        "vegetation_stress": float(after_row.get("vegetation_stress", 50)),
        "soil_degradation_risk": float(after_row.get("soil_degradation_risk", 50)),
        "water_stress": float(after_row.get("water_stress", 50)),
        "habitat_degradation": float(after_row.get("habitat_degradation", 50)),
        "biodiversity_risk": float(after_row.get("biodiversity_risk", 50)),
        "human_pressure_index": float(after_row.get("human_pressure_index", 50)),
        "overall_degradation": float(after_row.get("overall_degradation", 50)),
    }

    return {
        "zone_id": zone.get("zone_id", "Unknown"),
        "modifications": modifications,
        "before": {
            "indicators": before_indicators,
            "priority_score": round(float(before_score), 2),
            "priority_class": before_class,
            "primary_intervention": before_interventions["primary"],
        },
        "after": {
            "indicators": after_indicators,
            "priority_score": round(after_score, 2),
            "priority_class": after_class,
            "primary_intervention": after_interventions["primary"],
        },
        "changes": {
            "priority_score": round(after_score - float(before_score), 2),
            "indicators": {
                k: round(after_indicators[k] - float(before_indicators[k]), 2)
                for k in before_indicators
            },
        },
    }


# ------------------------------------------------------------------ #
# Scenario Management (in-memory)
# ------------------------------------------------------------------ #

class ScenarioManager:
    """Store and compare multiple named scenarios for a zone."""

    def __init__(self) -> None:
        self._scenarios: Dict[str, Dict[str, Any]] = {}

    def save_scenario(self, name: str, result: Dict[str, Any]) -> None:
        """Save a simulation result under the given name."""
        self._scenarios[name] = result

    def get_scenario(self, name: str) -> Optional[Dict[str, Any]]:
        return self._scenarios.get(name)

    def list_scenarios(self) -> List[str]:
        return list(self._scenarios.keys())

    def compare_scenarios(self) -> pd.DataFrame:
        """Return a comparison DataFrame of all saved scenarios.

        Columns: scenario_name, priority_score_before, priority_score_after,
        priority_change, priority_class_after, etc.
        """
        rows = []
        for name, result in self._scenarios.items():
            rows.append({
                "scenario": name,
                "zone_id": result.get("zone_id", ""),
                "score_before": result["before"]["priority_score"],
                "score_after": result["after"]["priority_score"],
                "change": result["changes"]["priority_score"],
                "class_before": result["before"]["priority_class"],
                "class_after": result["after"]["priority_class"],
            })
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows).sort_values("score_after")

    def clear(self) -> None:
        self._scenarios.clear()

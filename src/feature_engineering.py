"""
EcoRestore AI — Feature Engineering
=====================================
Compute normalised environmental indicators (0–100).

Directionality: **HIGH = BAD** for all indicators.

    - Vegetation Stress        (high = vegetation is degraded)
    - Soil Degradation Risk    (high = soil is degraded)
    - Water Stress             (high = water scarcity)
    - Habitat Degradation      (high = habitat is poor)
    - Biodiversity Risk        (high = biodiversity is low)
    - Human Pressure Index     (high = strong anthropogenic impact)
    - Overall Env. Degradation (weighted mean of the above)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_clip(series: pd.Series, lo: float = 0.0, hi: float = 100.0) -> pd.Series:
    """Clip and coerce to float, replacing NaN with 50 (neutral)."""
    return series.clip(lo, hi).fillna(50.0)


def compute_vegetation_stress(df: pd.DataFrame) -> pd.Series:
    """Vegetation Stress (0–100, high = bad).

    Derived from ``vegetation_index`` (inverted) and ``forest_cover`` (inverted).
    """
    veg = df.get("vegetation_index", pd.Series(50.0, index=df.index))
    fc  = df.get("forest_cover", pd.Series(50.0, index=df.index))
    # Both are "good when high", so invert.
    stress = 0.6 * (100 - veg) + 0.4 * (100 - fc)
    return _safe_clip(stress)


def compute_soil_degradation_risk(df: pd.DataFrame) -> pd.Series:
    """Soil Degradation Risk (0–100, high = bad).

    Derived from ``soil_degradation`` (already high = bad) and ``slope``.
    """
    sd = df.get("soil_degradation", pd.Series(50.0, index=df.index))
    # Normalise slope (0–60 degrees) → 0–100
    slope_raw = df.get("slope", pd.Series(15.0, index=df.index))
    slope_norm = (slope_raw / 60.0 * 100).clip(0, 100)
    risk = 0.75 * sd + 0.25 * slope_norm
    return _safe_clip(risk)


def compute_water_stress(df: pd.DataFrame) -> pd.Series:
    """Water Stress (0–100, high = bad).

    Derived from ``water_availability`` (inverted), ``rainfall`` (inverted),
    and ``drought_index`` (already high = bad).
    """
    wa = df.get("water_availability", pd.Series(50.0, index=df.index))
    rf = df.get("rainfall", pd.Series(50.0, index=df.index))
    di = df.get("drought_index", pd.Series(50.0, index=df.index))
    stress = 0.40 * (100 - wa) + 0.25 * (100 - rf) + 0.35 * di
    return _safe_clip(stress)


def compute_habitat_degradation(df: pd.DataFrame) -> pd.Series:
    """Habitat Degradation (0–100, high = bad).

    Derived from ``habitat_quality`` (inverted).
    """
    hq = df.get("habitat_quality", pd.Series(50.0, index=df.index))
    return _safe_clip(100 - hq)


def compute_biodiversity_risk(df: pd.DataFrame) -> pd.Series:
    """Biodiversity Risk (0–100, high = bad).

    Derived from ``biodiversity_index`` (inverted).
    """
    bi = df.get("biodiversity_index", pd.Series(50.0, index=df.index))
    return _safe_clip(100 - bi)


def compute_human_pressure_index(df: pd.DataFrame) -> pd.Series:
    """Human Pressure Index (0–100, high = bad).

    Derived from ``human_pressure`` and ``land_use_change``.
    """
    hp  = df.get("human_pressure", pd.Series(50.0, index=df.index))
    luc = df.get("land_use_change", pd.Series(50.0, index=df.index))
    index = 0.65 * hp + 0.35 * luc
    return _safe_clip(index)


def compute_overall_degradation(indicators: pd.DataFrame) -> pd.Series:
    """Overall Environmental Degradation (0–100, high = bad).

    Equally weighted mean of the six indicators.
    """
    cols = [
        "vegetation_stress",
        "soil_degradation_risk",
        "water_stress",
        "habitat_degradation",
        "biodiversity_risk",
        "human_pressure_index",
    ]
    present = [c for c in cols if c in indicators.columns]
    if not present:
        return pd.Series(50.0, index=indicators.index)
    return _safe_clip(indicators[present].mean(axis=1))


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all environmental indicators and attach them to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned environmental data (must contain raw feature columns).

    Returns
    -------
    pd.DataFrame
        Original columns **plus** the seven indicator columns.
    """
    result = df.copy()
    result["vegetation_stress"] = compute_vegetation_stress(df)
    result["soil_degradation_risk"] = compute_soil_degradation_risk(df)
    result["water_stress"] = compute_water_stress(df)
    result["habitat_degradation"] = compute_habitat_degradation(df)
    result["biodiversity_risk"] = compute_biodiversity_risk(df)
    result["human_pressure_index"] = compute_human_pressure_index(df)
    result["overall_degradation"] = compute_overall_degradation(result)

    # Round for readability
    indicator_cols = [
        "vegetation_stress", "soil_degradation_risk", "water_stress",
        "habitat_degradation", "biodiversity_risk", "human_pressure_index",
        "overall_degradation",
    ]
    result[indicator_cols] = result[indicator_cols].round(2)
    return result

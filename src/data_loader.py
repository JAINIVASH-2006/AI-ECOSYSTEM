"""
EcoRestore AI — Data Loader
============================
Generates synthetic environmental datasets, loads CSV / GeoJSON files,
and validates required columns and coordinate ranges.

Synthetic Data Disclaimer:
    All data produced by ``generate_sample_dataset`` is **clearly synthetic**
    and must **never** be presented as real environmental observations.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config.config import (
    LATITUDE_RANGE,
    LONGITUDE_RANGE,
    NUMERIC_COLUMNS,
    REQUIRED_COLUMNS,
    SAMPLE_DATA_DIR,
    SAMPLE_DATA_FILE,
    SAMPLE_DATA_SIZE,
)


# ------------------------------------------------------------------ #
# Synthetic / Sample Data Generation
# ------------------------------------------------------------------ #

def generate_sample_dataset(
    n: int = SAMPLE_DATA_SIZE,
    seed: int = 42,
    save: bool = True,
) -> pd.DataFrame:
    """Generate a synthetic environmental dataset with meaningful correlations.

    Parameters
    ----------
    n : int
        Number of geographic zones to generate.
    seed : int
        Random seed for reproducibility.
    save : bool
        If *True*, persist the dataframe as CSV in ``data/sample/``.

    Returns
    -------
    pd.DataFrame
        Synthetic dataset with all required columns.

    Notes
    -----
    **SYNTHETIC DATA** — Relationships are approximated to make the demo
    realistic but they are *not* calibrated against real ecological surveys.
    """
    rng = np.random.default_rng(seed)

    # --- Geographic coordinates spread across India (approx 8–35°N, 68–97°E)
    latitudes = rng.uniform(8.0, 35.0, n)
    longitudes = rng.uniform(68.0, 97.0, n)

    # --- Base environmental features (0‒100 scale) ---
    # Generate correlated features via shared latent factors.
    degradation_factor = rng.uniform(0, 100, n)  # latent "overall degradation"
    moisture_factor = rng.uniform(0, 100, n)      # latent "water availability"

    # Vegetation index: inversely related to degradation
    vegetation_index = np.clip(
        100 - 0.4 * degradation_factor + 0.2 * moisture_factor
        + rng.normal(0, 10, n),
        0, 100
    )

    # Soil degradation: positively related to degradation factor
    soil_degradation = np.clip(
        0.5 * degradation_factor + 0.1 * (100 - moisture_factor)
        + rng.normal(0, 8, n),
        0, 100
    )

    # Rainfall: loosely related to moisture factor
    rainfall = np.clip(
        0.6 * moisture_factor + 0.1 * (100 - degradation_factor)
        + rng.normal(0, 12, n),
        0, 100
    )

    # Water availability: strongly tied to moisture factor
    water_availability = np.clip(
        0.65 * moisture_factor + 0.05 * rainfall
        + rng.normal(0, 8, n),
        0, 100
    )

    # Land use change: positively related to human pressure / degradation
    land_use_change = np.clip(
        0.35 * degradation_factor + 0.15 * (100 - vegetation_index)
        + rng.normal(0, 10, n),
        0, 100
    )

    # Habitat quality: inversely related to degradation
    habitat_quality = np.clip(
        100 - 0.45 * degradation_factor + 0.1 * vegetation_index
        + rng.normal(0, 10, n),
        0, 100
    )

    # Biodiversity index: correlated with habitat quality & vegetation
    biodiversity_index = np.clip(
        0.3 * habitat_quality + 0.25 * vegetation_index
        + 0.1 * moisture_factor + rng.normal(0, 10, n),
        0, 100
    )

    # Human pressure: positively related to degradation
    human_pressure = np.clip(
        0.4 * degradation_factor + 0.15 * land_use_change
        + rng.normal(0, 10, n),
        0, 100
    )

    # Elevation (m) — 0‒3000, loosely decreasing with latitude
    elevation = np.clip(
        rng.uniform(50, 2500, n) + 0.3 * (latitudes - 8) * 50
        + rng.normal(0, 200, n),
        0, 5000
    )

    # Slope (degrees 0‒60) — correlated with elevation
    slope = np.clip(
        0.015 * elevation + rng.normal(0, 5, n),
        0, 60
    )

    # Forest cover (%) — inversely related to degradation, positively to vegetation
    forest_cover = np.clip(
        0.35 * vegetation_index + 0.15 * moisture_factor
        - 0.2 * degradation_factor + rng.normal(0, 8, n),
        0, 100
    )

    # Drought index (0‒100, high=bad) — inversely related to moisture
    drought_index = np.clip(
        100 - 0.55 * moisture_factor + 0.15 * degradation_factor
        + rng.normal(0, 10, n),
        0, 100
    )

    # --- Build DataFrame ---
    zone_ids = [f"ECO-{i:04d}" for i in range(1, n + 1)]

    df = pd.DataFrame({
        "zone_id": zone_ids,
        "latitude": np.round(latitudes, 6),
        "longitude": np.round(longitudes, 6),
        "vegetation_index": np.round(vegetation_index, 2),
        "soil_degradation": np.round(soil_degradation, 2),
        "rainfall": np.round(rainfall, 2),
        "water_availability": np.round(water_availability, 2),
        "land_use_change": np.round(land_use_change, 2),
        "habitat_quality": np.round(habitat_quality, 2),
        "biodiversity_index": np.round(biodiversity_index, 2),
        "human_pressure": np.round(human_pressure, 2),
        "elevation": np.round(elevation, 1),
        "slope": np.round(slope, 2),
        "forest_cover": np.round(forest_cover, 2),
        "drought_index": np.round(drought_index, 2),
        "data_source": "SYNTHETIC_DEMO",  # clearly labelled
    })

    if save:
        SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(SAMPLE_DATA_FILE, index=False)

    return df


# ------------------------------------------------------------------ #
# File Loading
# ------------------------------------------------------------------ #

def load_csv(filepath: str | Path) -> pd.DataFrame:
    """Load a CSV file and return a DataFrame.

    Parameters
    ----------
    filepath : str | Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file cannot be parsed as CSV.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    try:
        df = pd.read_csv(filepath)
    except Exception as exc:
        raise ValueError(f"Could not parse CSV file: {exc}") from exc
    return df


def load_geojson(filepath: str | Path) -> pd.DataFrame:
    """Load a GeoJSON file via GeoPandas and return a DataFrame.

    Parameters
    ----------
    filepath : str | Path
        Path to the GeoJSON file.

    Returns
    -------
    pd.DataFrame
    """
    try:
        import geopandas as gpd
    except ImportError:
        raise ImportError("geopandas is required to load GeoJSON files.")

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    try:
        gdf = gpd.read_file(filepath)
        return pd.DataFrame(gdf.drop(columns="geometry", errors="ignore"))
    except Exception as exc:
        raise ValueError(f"Could not parse GeoJSON file: {exc}") from exc


# ------------------------------------------------------------------ #
# Validation
# ------------------------------------------------------------------ #

def validate_columns(df: pd.DataFrame) -> Dict[str, list]:
    """Check that the DataFrame contains all required columns.

    Returns
    -------
    dict
        ``{"missing": [...], "extra": [...], "valid": bool}``
    """
    present = set(df.columns)
    required = set(REQUIRED_COLUMNS)
    missing = sorted(required - present)
    extra = sorted(present - required - {"data_source"})
    return {
        "missing": missing,
        "extra": extra,
        "valid": len(missing) == 0,
    }


def validate_coordinates(df: pd.DataFrame) -> Dict[str, object]:
    """Validate latitude and longitude ranges.

    Returns
    -------
    dict
        ``{"invalid_lat": int, "invalid_lon": int, "invalid_rows": list, "valid": bool}``
    """
    result: Dict[str, object] = {
        "invalid_lat": 0,
        "invalid_lon": 0,
        "invalid_rows": [],
        "valid": True,
    }

    if "latitude" not in df.columns or "longitude" not in df.columns:
        result["valid"] = False
        return result

    bad_lat = ~df["latitude"].between(*LATITUDE_RANGE)
    bad_lon = ~df["longitude"].between(*LONGITUDE_RANGE)
    bad = bad_lat | bad_lon

    result["invalid_lat"] = int(bad_lat.sum())
    result["invalid_lon"] = int(bad_lon.sum())
    result["invalid_rows"] = df.index[bad].tolist()
    result["valid"] = int(bad.sum()) == 0
    return result


def validate_numeric_columns(df: pd.DataFrame) -> Dict[str, list]:
    """Check that expected numeric columns are indeed numeric.

    Returns
    -------
    dict
        ``{"non_numeric": [...], "valid": bool}``
    """
    non_numeric: List[str] = []
    for col in NUMERIC_COLUMNS:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            non_numeric.append(col)
    return {"non_numeric": non_numeric, "valid": len(non_numeric) == 0}


def get_data_summary(df: pd.DataFrame) -> Dict[str, object]:
    """Return a summary dict for display in the UI.

    Returns
    -------
    dict
        Row count, column count, missing values, dtypes, etc.
    """
    missing_per_col = df.isnull().sum().to_dict()
    total_missing = int(df.isnull().sum().sum())
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
        "missing_per_column": missing_per_col,
        "total_missing": total_missing,
        "duplicates": int(df.duplicated().sum()),
    }


# ------------------------------------------------------------------ #
# Convenience: load or generate sample data
# ------------------------------------------------------------------ #

def get_sample_data() -> pd.DataFrame:
    """Return the sample dataset, generating it first if necessary."""
    if SAMPLE_DATA_FILE.exists():
        return load_csv(SAMPLE_DATA_FILE)
    return generate_sample_dataset()

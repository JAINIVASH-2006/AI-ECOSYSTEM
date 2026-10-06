"""
EcoRestore AI — Data Preprocessing
====================================
Missing-value handling, duplicate removal, datatype coercion,
coordinate validation, outlier detection, and normalization.

Returns preprocessing statistics for UI display.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from config.config import LATITUDE_RANGE, LONGITUDE_RANGE, NUMERIC_COLUMNS


def preprocess_pipeline(
    df: pd.DataFrame,
    *,
    handle_missing: str = "median",
    remove_duplicates: bool = True,
    fix_coordinates: bool = True,
    detect_outliers: bool = True,
    normalize: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Run the full preprocessing pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Raw environmental data.
    handle_missing : str
        Strategy for missing numeric values: ``"median"``, ``"mean"``, or ``"drop"``.
    remove_duplicates : bool
        Remove exact duplicate rows.
    fix_coordinates : bool
        Clip or flag invalid coordinates.
    detect_outliers : bool
        Flag outliers using the IQR method.
    normalize : bool
        Min-max normalise numeric columns to 0–100 (in-place copy).

    Returns
    -------
    (pd.DataFrame, dict)
        Cleaned DataFrame and a statistics dictionary.
    """
    stats: Dict[str, Any] = {
        "original_rows": len(df),
        "original_columns": len(df.columns),
        "steps": [],
    }

    df = df.copy()

    # 1. Datatype coercion ------------------------------------------------
    coerced_cols: List[str] = []
    for col in NUMERIC_COLUMNS:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
            coerced_cols.append(col)
    stats["coerced_columns"] = coerced_cols
    stats["steps"].append(f"Coerced {len(coerced_cols)} columns to numeric.")

    # 2. Missing values ---------------------------------------------------
    missing_before = int(df.isnull().sum().sum())
    missing_per_col = df.isnull().sum().to_dict()
    stats["missing_before"] = missing_before
    stats["missing_per_column"] = {k: int(v) for k, v in missing_per_col.items() if v > 0}

    if handle_missing == "drop":
        df = df.dropna()
    elif handle_missing in ("median", "mean"):
        num_cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
        if handle_missing == "median":
            fill_values = df[num_cols].median()
        else:
            fill_values = df[num_cols].mean()
        df[num_cols] = df[num_cols].fillna(fill_values)

    missing_after = int(df.isnull().sum().sum())
    stats["missing_after"] = missing_after
    stats["steps"].append(
        f"Missing values: {missing_before} → {missing_after} (strategy={handle_missing})."
    )

    # 3. Duplicate removal -----------------------------------------------
    dupes = int(df.duplicated().sum())
    stats["duplicates_found"] = dupes
    if remove_duplicates and dupes > 0:
        df = df.drop_duplicates()
    stats["steps"].append(f"Duplicates removed: {dupes}.")

    # 4. Coordinate validation -------------------------------------------
    coord_stats: Dict[str, int] = {"clipped_lat": 0, "clipped_lon": 0}
    if fix_coordinates and "latitude" in df.columns and "longitude" in df.columns:
        bad_lat = ~df["latitude"].between(*LATITUDE_RANGE)
        bad_lon = ~df["longitude"].between(*LONGITUDE_RANGE)
        coord_stats["clipped_lat"] = int(bad_lat.sum())
        coord_stats["clipped_lon"] = int(bad_lon.sum())
        df["latitude"] = df["latitude"].clip(*LATITUDE_RANGE)
        df["longitude"] = df["longitude"].clip(*LONGITUDE_RANGE)
    stats["coordinate_fixes"] = coord_stats
    stats["steps"].append(
        f"Coordinates clipped: {coord_stats['clipped_lat']} lat, "
        f"{coord_stats['clipped_lon']} lon."
    )

    # 5. Outlier detection (IQR) -----------------------------------------
    outlier_counts: Dict[str, int] = {}
    if detect_outliers:
        num_cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
            if n_outliers > 0:
                outlier_counts[col] = n_outliers
    stats["outliers"] = outlier_counts
    stats["steps"].append(
        f"Outlier columns detected (IQR): {len(outlier_counts)}."
    )

    # 6. Normalization (optional) ----------------------------------------
    if normalize:
        num_cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
        for col in num_cols:
            cmin, cmax = df[col].min(), df[col].max()
            if cmax - cmin > 0:
                df[col] = 100.0 * (df[col] - cmin) / (cmax - cmin)
            else:
                df[col] = 0.0
        stats["steps"].append("Min-max normalisation applied (0–100).")

    # Final stats ---------------------------------------------------------
    stats["final_rows"] = len(df)
    stats["final_columns"] = len(df.columns)
    stats["rows_removed"] = stats["original_rows"] - stats["final_rows"]

    return df, stats

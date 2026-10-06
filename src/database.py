"""
EcoRestore AI — Database Module
=================================
SQLite persistence for zones, environmental data, predictions,
interventions, and simulations.

All raw SQL is encapsulated here — UI code must call Python functions only.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from config.config import DATABASE_PATH

# ------------------------------------------------------------------ #
# Connection Helpers
# ------------------------------------------------------------------ #

@contextmanager
def get_connection(db_path: Optional[Path] = None):
    """Context manager for SQLite connections."""
    path = db_path or DATABASE_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(db_path: Optional[Path] = None) -> None:
    """Create all tables if they don't exist."""
    with get_connection(db_path) as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS zones (
                zone_id TEXT PRIMARY KEY,
                latitude REAL,
                longitude REAL,
                elevation REAL,
                slope REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS environmental_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT NOT NULL,
                vegetation_index REAL,
                soil_degradation REAL,
                rainfall REAL,
                water_availability REAL,
                land_use_change REAL,
                habitat_quality REAL,
                biodiversity_index REAL,
                human_pressure REAL,
                forest_cover REAL,
                drought_index REAL,
                vegetation_stress REAL,
                soil_degradation_risk REAL,
                water_stress REAL,
                habitat_degradation REAL,
                biodiversity_risk REAL,
                human_pressure_index REAL,
                overall_degradation REAL,
                priority_score REAL,
                priority_class TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (zone_id) REFERENCES zones(zone_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT NOT NULL,
                model_name TEXT,
                predicted_score REAL,
                predicted_class TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (zone_id) REFERENCES zones(zone_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT NOT NULL,
                intervention_type TEXT,
                suitability_score REAL,
                rank INTEGER,
                reasons TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (zone_id) REFERENCES zones(zone_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT NOT NULL,
                scenario_name TEXT,
                modifications TEXT,
                before_score REAL,
                after_score REAL,
                before_class TEXT,
                after_class TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (zone_id) REFERENCES zones(zone_id)
            )
        """)


# ------------------------------------------------------------------ #
# Insert Operations
# ------------------------------------------------------------------ #

def save_zones(df: pd.DataFrame, db_path: Optional[Path] = None) -> int:
    """Insert zone records (upsert on zone_id)."""
    init_database(db_path)
    count = 0
    with get_connection(db_path) as conn:
        for _, row in df.iterrows():
            conn.execute(
                """INSERT OR REPLACE INTO zones (zone_id, latitude, longitude, elevation, slope)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    row.get("zone_id"),
                    row.get("latitude"),
                    row.get("longitude"),
                    row.get("elevation"),
                    row.get("slope"),
                ),
            )
            count += 1
    return count


def save_environmental_data(df: pd.DataFrame, db_path: Optional[Path] = None) -> int:
    """Insert environmental data rows."""
    init_database(db_path)
    cols = [
        "zone_id", "vegetation_index", "soil_degradation", "rainfall",
        "water_availability", "land_use_change", "habitat_quality",
        "biodiversity_index", "human_pressure", "forest_cover", "drought_index",
        "vegetation_stress", "soil_degradation_risk", "water_stress",
        "habitat_degradation", "biodiversity_risk", "human_pressure_index",
        "overall_degradation", "priority_score", "priority_class",
    ]
    available = [c for c in cols if c in df.columns]
    placeholders = ", ".join(["?"] * len(available))
    col_str = ", ".join(available)

    count = 0
    with get_connection(db_path) as conn:
        for _, row in df.iterrows():
            values = tuple(row.get(c) for c in available)
            conn.execute(
                f"INSERT INTO environmental_data ({col_str}) VALUES ({placeholders})",
                values,
            )
            count += 1
    return count


def save_prediction(
    zone_id: str,
    model_name: str,
    predicted_score: float,
    predicted_class: str,
    confidence: float,
    db_path: Optional[Path] = None,
) -> None:
    """Save a single prediction."""
    init_database(db_path)
    with get_connection(db_path) as conn:
        conn.execute(
            """INSERT INTO predictions (zone_id, model_name, predicted_score,
               predicted_class, confidence) VALUES (?, ?, ?, ?, ?)""",
            (zone_id, model_name, predicted_score, predicted_class, confidence),
        )


def save_simulation(
    zone_id: str,
    scenario_name: str,
    modifications: dict,
    before_score: float,
    after_score: float,
    before_class: str,
    after_class: str,
    details: Optional[dict] = None,
    db_path: Optional[Path] = None,
) -> None:
    """Save a simulation result."""
    init_database(db_path)
    with get_connection(db_path) as conn:
        conn.execute(
            """INSERT INTO simulations (zone_id, scenario_name, modifications,
               before_score, after_score, before_class, after_class, details)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                zone_id,
                scenario_name,
                json.dumps(modifications),
                before_score,
                after_score,
                before_class,
                after_class,
                json.dumps(details) if details else None,
            ),
        )


# ------------------------------------------------------------------ #
# Query Operations
# ------------------------------------------------------------------ #

def get_all_zones(db_path: Optional[Path] = None) -> pd.DataFrame:
    """Return all zones as a DataFrame."""
    init_database(db_path)
    with get_connection(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM zones", conn)


def get_environmental_data(db_path: Optional[Path] = None) -> pd.DataFrame:
    """Return all environmental data."""
    init_database(db_path)
    with get_connection(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM environmental_data", conn)


def get_predictions(db_path: Optional[Path] = None) -> pd.DataFrame:
    """Return all predictions."""
    init_database(db_path)
    with get_connection(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM predictions", conn)


def get_simulations(zone_id: Optional[str] = None, db_path: Optional[Path] = None) -> pd.DataFrame:
    """Return simulations, optionally filtered by zone_id."""
    init_database(db_path)
    with get_connection(db_path) as conn:
        if zone_id:
            return pd.read_sql_query(
                "SELECT * FROM simulations WHERE zone_id = ?", conn, params=(zone_id,)
            )
        return pd.read_sql_query("SELECT * FROM simulations", conn)

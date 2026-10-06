"""
EcoRestore AI — Project Configuration
======================================
Central configuration for paths, database, map defaults, and model parameters.
All configurable thresholds and scoring weights are in thresholds.py.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MAPS_DIR = OUTPUTS_DIR / "maps"
REPORTS_DIR = OUTPUTS_DIR / "reports"
PREDICTIONS_DIR = OUTPUTS_DIR / "predictions"
ASSETS_DIR = PROJECT_ROOT / "assets"

# ---------------------------------------------------------------------------
# Sample Data
# ---------------------------------------------------------------------------
SAMPLE_DATA_FILE = SAMPLE_DATA_DIR / "sample_environmental_data.csv"
SAMPLE_DATA_SIZE = 1000  # Number of synthetic zones to generate

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_PATH = PROJECT_ROOT / "eco_restore.db"

# ---------------------------------------------------------------------------
# Required Columns for Environmental Data
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "zone_id",
    "latitude",
    "longitude",
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

# Columns that must be numeric (everything except zone_id)
NUMERIC_COLUMNS = [c for c in REQUIRED_COLUMNS if c != "zone_id"]

# Coordinate bounds for validation
LATITUDE_RANGE = (-90.0, 90.0)
LONGITUDE_RANGE = (-180.0, 180.0)

# ---------------------------------------------------------------------------
# Map Defaults (India-centric for sample data)
# ---------------------------------------------------------------------------
MAP_CENTER_LAT = 22.0
MAP_CENTER_LON = 79.0
MAP_ZOOM = 5
MAP_TILES = "CartoDB positron"

# ---------------------------------------------------------------------------
# Model Parameters
# ---------------------------------------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Random Forest defaults
RF_N_ESTIMATORS = 200
RF_MAX_DEPTH = 15
RF_MIN_SAMPLES_SPLIT = 5
RF_MIN_SAMPLES_LEAF = 2

# XGBoost defaults
XGB_N_ESTIMATORS = 200
XGB_MAX_DEPTH = 8
XGB_LEARNING_RATE = 0.1
XGB_SUBSAMPLE = 0.8

# ---------------------------------------------------------------------------
# File Upload Limits
# ---------------------------------------------------------------------------
MAX_UPLOAD_SIZE_MB = 50

# ---------------------------------------------------------------------------
# Application Metadata
# ---------------------------------------------------------------------------
APP_NAME = "EcoRestore AI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "AI-Based Ecological Restoration Priority Mapping "
    "and Intervention Planning System"
)
APP_DISCLAIMER = (
    "This system provides estimated priority assessments and recommended "
    "interventions for decision-support purposes. It does not replace "
    "professional ecological expertise. All synthetic/demo data is clearly "
    "labelled and must not be treated as real environmental observations."
)

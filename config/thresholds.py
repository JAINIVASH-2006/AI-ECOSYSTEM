"""
EcoRestore AI — Thresholds & Scoring Configuration
====================================================
All configurable thresholds, scoring weights, and classification boundaries.
Modify values here — they are imported throughout the project.

Directionality Convention:
-   Environmental indicators (0–100): HIGH = BAD (high stress/degradation/risk)
-   Priority score (0–100): HIGH = NEEDS RESTORATION (critical)
-   Intervention suitability (0–100): HIGH = MORE SUITABLE
"""

# ===================================================================
# RESTORATION PRIORITY CLASSIFICATION
# ===================================================================
# Boundary values are INCLUSIVE on the lower end.
# 0–25 = LOW, 26–50 = MODERATE, 51–75 = HIGH, 76–100 = CRITICAL
PRIORITY_THRESHOLDS = {
    "LOW": (0, 25),
    "MODERATE": (26, 50),
    "HIGH": (51, 75),
    "CRITICAL": (76, 100),
}

PRIORITY_CLASSES = ["LOW", "MODERATE", "HIGH", "CRITICAL"]

PRIORITY_COLORS = {
    "LOW": "#2ecc71",        # Green
    "MODERATE": "#f39c12",   # Orange
    "HIGH": "#e74c3c",       # Red
    "CRITICAL": "#8e44ad",   # Purple
}

# ===================================================================
# BASELINE PRIORITY SCORING WEIGHTS (must sum to 1.0)
# ===================================================================
PRIORITY_WEIGHTS = {
    "soil_degradation_risk": 0.25,   # Land / soil degradation
    "vegetation_stress": 0.20,       # Vegetation stress
    "water_stress": 0.15,            # Water stress
    "habitat_degradation": 0.15,     # Habitat degradation
    "biodiversity_risk": 0.15,       # Biodiversity risk
    "human_pressure_index": 0.10,    # Human pressure
}

# ===================================================================
# ENVIRONMENTAL INDICATOR THRESHOLDS
# ===================================================================
# Used to classify indicator severity.  HIGH = BAD.
INDICATOR_SEVERITY = {
    "LOW": (0, 25),
    "MODERATE": (26, 50),
    "HIGH": (51, 75),
    "VERY_HIGH": (76, 100),
}

# ===================================================================
# INTERVENTION TYPES
# ===================================================================
INTERVENTION_TYPES = [
    "Afforestation",
    "Reforestation",
    "Soil Conservation",
    "Agroforestry",
    "Rainwater Harvesting",
    "Watershed Management",
    "Habitat Restoration",
    "Native Vegetation Restoration",
    "Erosion Control",
]

# ===================================================================
# INTERVENTION SUITABILITY THRESHOLDS
# ===================================================================
# Minimum indicator values (0–100, high=bad) to trigger high suitability.
# Format: {intervention: {indicator: weight}}
# Each intervention's suitability is a weighted sum of relevant indicators.
INTERVENTION_RULES = {
    "Afforestation": {
        "vegetation_stress": 0.40,
        "soil_degradation_risk": 0.20,
        "biodiversity_risk": 0.15,
        "water_stress": 0.10,
        "human_pressure_index": 0.15,
    },
    "Reforestation": {
        "vegetation_stress": 0.35,
        "habitat_degradation": 0.25,
        "biodiversity_risk": 0.20,
        "soil_degradation_risk": 0.10,
        "water_stress": 0.10,
    },
    "Soil Conservation": {
        "soil_degradation_risk": 0.45,
        "water_stress": 0.20,
        "vegetation_stress": 0.15,
        "human_pressure_index": 0.10,
        "habitat_degradation": 0.10,
    },
    "Agroforestry": {
        "vegetation_stress": 0.25,
        "soil_degradation_risk": 0.25,
        "human_pressure_index": 0.20,
        "water_stress": 0.15,
        "biodiversity_risk": 0.15,
    },
    "Rainwater Harvesting": {
        "water_stress": 0.50,
        "soil_degradation_risk": 0.15,
        "vegetation_stress": 0.15,
        "human_pressure_index": 0.10,
        "habitat_degradation": 0.10,
    },
    "Watershed Management": {
        "water_stress": 0.40,
        "soil_degradation_risk": 0.25,
        "vegetation_stress": 0.15,
        "habitat_degradation": 0.10,
        "biodiversity_risk": 0.10,
    },
    "Habitat Restoration": {
        "habitat_degradation": 0.40,
        "biodiversity_risk": 0.30,
        "vegetation_stress": 0.15,
        "water_stress": 0.10,
        "human_pressure_index": 0.05,
    },
    "Native Vegetation Restoration": {
        "vegetation_stress": 0.35,
        "habitat_degradation": 0.25,
        "biodiversity_risk": 0.20,
        "soil_degradation_risk": 0.10,
        "water_stress": 0.10,
    },
    "Erosion Control": {
        "soil_degradation_risk": 0.45,
        "water_stress": 0.20,
        "vegetation_stress": 0.20,
        "human_pressure_index": 0.10,
        "habitat_degradation": 0.05,
    },
}

# ===================================================================
# INTERVENTION CONDITION MODIFIERS
# ===================================================================
# Additional raw-feature conditions that boost or penalise suitability.
# Format: {intervention: [(column, operator, value, bonus_pts), ...]}
# Bonus is added AFTER the weighted sum (clamped to 0–100).
INTERVENTION_CONDITION_MODIFIERS = {
    "Afforestation": [
        ("forest_cover", "<", 30, 10),   # low forest cover  → boost
        ("slope", "<", 25, 5),           # gentle slope      → boost
    ],
    "Reforestation": [
        ("forest_cover", "<", 40, 10),
    ],
    "Soil Conservation": [
        ("slope", ">", 15, 10),
        ("soil_degradation", ">", 60, 5),
    ],
    "Agroforestry": [
        ("land_use_change", ">", 50, 10),
        ("forest_cover", "<", 40, 5),
    ],
    "Rainwater Harvesting": [
        ("rainfall", "<", 40, 10),
        ("water_availability", "<", 30, 10),
    ],
    "Watershed Management": [
        ("rainfall", "<", 50, 5),
        ("water_availability", "<", 40, 5),
    ],
    "Habitat Restoration": [
        ("habitat_quality", "<", 35, 10),
        ("biodiversity_index", "<", 35, 5),
    ],
    "Native Vegetation Restoration": [
        ("vegetation_index", "<", 35, 10),
    ],
    "Erosion Control": [
        ("slope", ">", 20, 10),
        ("soil_degradation", ">", 55, 5),
    ],
}

# ===================================================================
# MAP SETTINGS
# ===================================================================
MAP_MARKER_RADIUS = 6
MAP_MARKER_OPACITY = 0.85
MAP_FILL_OPACITY = 0.70

# Layer-specific color scales (low→high, remember high=bad for indicators)
INDICATOR_COLOR_SCALE = {
    "priority_score": ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c", "#8e44ad"],
    "vegetation_stress": ["#27ae60", "#f39c12", "#e74c3c"],
    "soil_degradation_risk": ["#27ae60", "#f39c12", "#e74c3c"],
    "water_stress": ["#3498db", "#f39c12", "#e74c3c"],
    "habitat_degradation": ["#27ae60", "#f39c12", "#e74c3c"],
    "biodiversity_risk": ["#27ae60", "#f39c12", "#e74c3c"],
    "human_pressure_index": ["#27ae60", "#f39c12", "#e74c3c"],
}

# ===================================================================
# SIMULATION PARAMETER RANGES
# ===================================================================
SIMULATION_PARAMS = {
    "vegetation_index": {"min": -50, "max": 50, "step": 5, "unit": "%"},
    "water_availability": {"min": -50, "max": 50, "step": 5, "unit": "%"},
    "soil_degradation": {"min": -50, "max": 50, "step": 5, "unit": "%"},
    "habitat_quality": {"min": -50, "max": 50, "step": 5, "unit": "%"},
    "biodiversity_index": {"min": -50, "max": 50, "step": 5, "unit": "%"},
    "human_pressure": {"min": -50, "max": 50, "step": 5, "unit": "%"},
    "forest_cover": {"min": -50, "max": 50, "step": 5, "unit": "%"},
}

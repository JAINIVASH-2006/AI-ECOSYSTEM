"""
EcoRestore AI — Thresholds & Scoring Configuration
====================================================
All configurable thresholds, scoring weights, and classification boundaries.
Modify values here — they are imported throughout the project.

Directionality Convention:
-   Environmental indicators (0–100): HIGH = BAD (high stress/degradation/risk)
-   Priority score (0–100): HIGH = NEEDS RESTORATION (critical)
-   Environmental health score (0–100): HIGH = HEALTHY / EXCELLENT
-   Intervention suitability (0–100): HIGH = MORE SUITABLE
"""

# ===================================================================
# RESTORATION PRIORITY CLASSIFICATION (5 TIERS)
# ===================================================================
PRIORITY_THRESHOLDS = {
    "VERY_LOW": (0, 20),
    "LOW": (21, 40),
    "MODERATE": (41, 60),
    "HIGH": (61, 80),
    "CRITICAL": (81, 100),
}

PRIORITY_CLASSES = ["VERY_LOW", "LOW", "MODERATE", "HIGH", "CRITICAL"]

PRIORITY_COLORS = {
    "VERY_LOW": "#059669",    # Emerald
    "LOW": "#10b981",         # Green
    "MODERATE": "#f59e0b",    # Amber
    "HIGH": "#ef4444",        # Coral Red
    "CRITICAL": "#7c3aed",    # Violet Purple
}

# ===================================================================
# BASELINE PRIORITY SCORING WEIGHTS (must sum to 1.0)
# ===================================================================
PRIORITY_WEIGHTS = {
    "soil_degradation_risk": 0.20,   # Land / soil degradation
    "vegetation_stress": 0.18,       # Vegetation stress / NDVI deficit
    "water_stress": 0.15,            # Water scarcity & drought
    "habitat_degradation": 0.14,     # Habitat loss & fragmentation
    "biodiversity_risk": 0.14,       # Biodiversity decline
    "soil_erosion_hazard": 0.07,     # Soil erosion risk
    "human_pressure_index": 0.07,    # Anthropogenic pressure
    "land_use_change_stress": 0.05,  # Land conversion & deforestation
}

# ===================================================================
# ENVIRONMENTAL HEALTH SCORE WEIGHTS (Higher = Healthier)
# ===================================================================
HEALTH_WEIGHTS = {
    "vegetation_condition": 0.20,
    "soil_quality": 0.20,
    "water_availability": 0.15,
    "biodiversity_condition": 0.15,
    "habitat_quality": 0.15,
    "human_pressure_buffer": 0.15,
}

# ===================================================================
# 10 ENVIRONMENTAL THREATS
# ===================================================================
THREAT_TYPES = [
    "Deforestation",
    "Vegetation Loss",
    "Soil Degradation",
    "Soil Erosion",
    "Water Scarcity",
    "Habitat Loss",
    "Biodiversity Decline",
    "Land Degradation",
    "Desertification Risk",
    "High Human Pressure",
]

# ===================================================================
# 11 RESTORATION INTERVENTION TYPES
# ===================================================================
INTERVENTION_TYPES = [
    "Afforestation",
    "Reforestation",
    "Agroforestry",
    "Soil Conservation",
    "Rainwater Harvesting",
    "Watershed Management",
    "Habitat Restoration",
    "Native Species Plantation",
    "Wetland Restoration",
    "Erosion Control",
    "Ecological Corridor Development",
]

# Intervention cost estimates per hectare (USD)
INTERVENTION_UNIT_COSTS = {
    "Afforestation": 1200,
    "Reforestation": 950,
    "Agroforestry": 800,
    "Soil Conservation": 650,
    "Rainwater Harvesting": 1100,
    "Watershed Management": 1400,
    "Habitat Restoration": 1300,
    "Native Species Plantation": 900,
    "Wetland Restoration": 1600,
    "Erosion Control": 750,
    "Ecological Corridor Development": 1500,
}

# ===================================================================
# INTERVENTION SUITABILITY RULES
# ===================================================================
INTERVENTION_RULES = {
    "Afforestation": {
        "vegetation_stress": 0.35,
        "soil_degradation_risk": 0.20,
        "land_use_change_stress": 0.15,
        "biodiversity_risk": 0.15,
        "water_stress": 0.15,
    },
    "Reforestation": {
        "vegetation_stress": 0.35,
        "habitat_degradation": 0.25,
        "biodiversity_risk": 0.20,
        "soil_degradation_risk": 0.10,
        "water_stress": 0.10,
    },
    "Agroforestry": {
        "soil_degradation_risk": 0.30,
        "human_pressure_index": 0.25,
        "vegetation_stress": 0.20,
        "water_stress": 0.15,
        "biodiversity_risk": 0.10,
    },
    "Soil Conservation": {
        "soil_degradation_risk": 0.40,
        "soil_erosion_hazard": 0.30,
        "water_stress": 0.15,
        "vegetation_stress": 0.15,
    },
    "Rainwater Harvesting": {
        "water_stress": 0.50,
        "soil_degradation_risk": 0.20,
        "vegetation_stress": 0.15,
        "human_pressure_index": 0.15,
    },
    "Watershed Management": {
        "water_stress": 0.35,
        "soil_erosion_hazard": 0.25,
        "soil_degradation_risk": 0.20,
        "vegetation_stress": 0.10,
        "habitat_degradation": 0.10,
    },
    "Habitat Restoration": {
        "habitat_degradation": 0.40,
        "biodiversity_risk": 0.30,
        "vegetation_stress": 0.15,
        "water_stress": 0.10,
        "human_pressure_index": 0.05,
    },
    "Native Species Plantation": {
        "biodiversity_risk": 0.35,
        "vegetation_stress": 0.30,
        "habitat_degradation": 0.20,
        "soil_degradation_risk": 0.15,
    },
    "Wetland Restoration": {
        "water_stress": 0.40,
        "biodiversity_risk": 0.25,
        "habitat_degradation": 0.20,
        "vegetation_stress": 0.15,
    },
    "Erosion Control": {
        "soil_erosion_hazard": 0.45,
        "soil_degradation_risk": 0.30,
        "water_stress": 0.15,
        "vegetation_stress": 0.10,
    },
    "Ecological Corridor Development": {
        "habitat_degradation": 0.40,
        "biodiversity_risk": 0.30,
        "human_pressure_index": 0.20,
        "vegetation_stress": 0.10,
    },
}

# ===================================================================
# INTERVENTION CONDITION MODIFIERS
# ===================================================================
INTERVENTION_CONDITION_MODIFIERS = {
    "Afforestation": [
        ("forest_cover", "<", 30, 10),
        ("slope", "<", 25, 5),
    ],
    "Reforestation": [
        ("forest_cover", "<", 50, 10),
        ("land_use_change", ">", 40, 5),
    ],
    "Soil Conservation": [
        ("slope", ">", 15, 10),
        ("soil_degradation", ">", 50, 5),
    ],
    "Agroforestry": [
        ("human_pressure", ">", 40, 10),
        ("elevation", "<", 1500, 5),
    ],
    "Rainwater Harvesting": [
        ("rainfall", "<", 45, 10),
        ("drought_index", ">", 50, 5),
    ],
    "Watershed Management": [
        ("slope", ">", 10, 5),
        ("rainfall", ">", 40, 5),
    ],
    "Habitat Restoration": [
        ("habitat_quality", "<", 40, 10),
        ("biodiversity_index", "<", 40, 5),
    ],
    "Native Species Plantation": [
        ("biodiversity_index", "<", 50, 10),
    ],
    "Wetland Restoration": [
        ("water_availability", "<", 40, 10),
    ],
    "Erosion Control": [
        ("slope", ">", 20, 10),
    ],
    "Ecological Corridor Development": [
        ("habitat_quality", "<", 50, 10),
    ],
}

INTERVENTION_OBJECTIVES = {
    "Afforestation": [
        "Increase forest cover and canopy density",
        "Reduce soil erosion via root stabilisation",
        "Improve carbon sequestration",
        "Enhance local biodiversity",
    ],
    "Reforestation": [
        "Restore degraded forest ecosystems",
        "Rebuild wildlife corridors",
        "Improve watershed protection",
        "Enhance biodiversity through native species",
    ],
    "Soil Conservation": [
        "Reduce soil erosion and land degradation",
        "Improve soil fertility",
        "Enhance water retention capacity",
        "Prevent land productivity decline",
    ],
    "Agroforestry": [
        "Integrate trees with agricultural systems",
        "Improve soil health",
        "Provide sustainable livelihoods",
        "Reduce pressure on natural forests",
    ],
    "Rainwater Harvesting": [
        "Increase water availability in dry seasons",
        "Reduce dependency on groundwater",
        "Support irrigation for plantings",
        "Improve local water table",
    ],
    "Watershed Management": [
        "Improve catchment-level water management",
        "Reduce flood risk and runoff",
        "Enhance aquifer recharge",
        "Protect downstream water quality",
    ],
    "Habitat Restoration": [
        "Rebuild critical wildlife habitats",
        "Restore ecological connectivity",
        "Support endangered species recovery",
        "Improve ecosystem resilience",
    ],
    "Native Species Plantation": [
        "Re-establish indigenous vegetation and flora",
        "Reduce invasive plant dominance",
        "Support native pollinators and birds",
    ],
    "Wetland Restoration": [
        "Rejuvenate hydrological water recharge zones",
        "Provide refuge for avifauna and amphibians",
    ],
    "Erosion Control": [
        "Stabilize vulnerable topsoil and ravines",
        "Construct contour barriers and check dams",
    ],
    "Ecological Corridor Development": [
        "Bridge fragmented natural ecosystems",
        "Enable genetic migration across reserves",
    ],
}

INTERVENTION_IMPACT_MODELS = {
    "Afforestation": {
        "vegetation_stress": -35,
        "soil_degradation_risk": -20,
        "biodiversity_risk": -20,
        "habitat_degradation": -25,
        "water_stress": -10,
    },
    "Reforestation": {
        "vegetation_stress": -30,
        "habitat_degradation": -30,
        "biodiversity_risk": -25,
        "soil_degradation_risk": -15,
    },
    "Soil Conservation": {
        "soil_degradation_risk": -40,
        "soil_erosion_hazard": -45,
        "vegetation_stress": -10,
    },
    "Agroforestry": {
        "soil_degradation_risk": -25,
        "vegetation_stress": -20,
        "human_pressure_index": -15,
        "biodiversity_risk": -10,
    },
    "Rainwater Harvesting": {
        "water_stress": -45,
        "vegetation_stress": -15,
        "soil_degradation_risk": -10,
    },
    "Watershed Management": {
        "water_stress": -35,
        "soil_erosion_hazard": -30,
        "soil_degradation_risk": -20,
        "vegetation_stress": -15,
    },
    "Habitat Restoration": {
        "habitat_degradation": -45,
        "biodiversity_risk": -40,
        "vegetation_stress": -15,
    },
    "Native Species Plantation": {
        "biodiversity_risk": -35,
        "vegetation_stress": -25,
        "habitat_degradation": -20,
    },
    "Wetland Restoration": {
        "water_stress": -35,
        "biodiversity_risk": -30,
        "habitat_degradation": -25,
    },
    "Erosion Control": {
        "soil_erosion_hazard": -45,
        "soil_degradation_risk": -30,
    },
    "Ecological Corridor Development": {
        "habitat_degradation": -40,
        "biodiversity_risk": -35,
    },
}

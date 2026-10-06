"""
EcoRestore AI — Tests
=======================
Tests for data validation, preprocessing, priority scoring,
classification, intervention engine, and simulation.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.thresholds import PRIORITY_THRESHOLDS, PRIORITY_WEIGHTS
from src.data_loader import (
    generate_sample_dataset,
    validate_columns,
    validate_coordinates,
    validate_numeric_columns,
)
from src.preprocessing import preprocess_pipeline
from src.feature_engineering import compute_all_indicators
from src.priority_engine import classify_priority, compute_priority, compute_priority_score
from src.intervention_engine import compute_intervention_suitability, get_zone_interventions
from src.simulation import simulate_zone


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def sample_df():
    """Generate a small sample DataFrame for testing."""
    return generate_sample_dataset(n=50, save=False, seed=123)


@pytest.fixture
def processed_df(sample_df):
    """Preprocessed DataFrame with indicators and priority."""
    df_clean, _ = preprocess_pipeline(sample_df)
    df_ind = compute_all_indicators(df_clean)
    return compute_priority(df_ind)


# ------------------------------------------------------------------ #
# Data Validation Tests
# ------------------------------------------------------------------ #

class TestDataValidation:
    def test_validate_columns_all_present(self, sample_df):
        result = validate_columns(sample_df)
        assert result["valid"] is True
        assert len(result["missing"]) == 0

    def test_validate_columns_missing(self, sample_df):
        df = sample_df.drop(columns=["vegetation_index", "rainfall"])
        result = validate_columns(df)
        assert result["valid"] is False
        assert "vegetation_index" in result["missing"]
        assert "rainfall" in result["missing"]

    def test_validate_coordinates_valid(self, sample_df):
        result = validate_coordinates(sample_df)
        assert result["valid"] is True
        assert result["invalid_lat"] == 0
        assert result["invalid_lon"] == 0

    def test_validate_coordinates_invalid(self):
        df = pd.DataFrame({
            "latitude": [100, -200, 20],
            "longitude": [50, 300, 80],
        })
        result = validate_coordinates(df)
        assert result["valid"] is False
        assert result["invalid_lat"] == 2
        assert result["invalid_lon"] == 1

    def test_validate_numeric_columns(self, sample_df):
        result = validate_numeric_columns(sample_df)
        assert result["valid"] is True

    def test_validate_non_numeric(self, sample_df):
        df = sample_df.copy()
        df["elevation"] = "not_a_number"
        result = validate_numeric_columns(df)
        assert result["valid"] is False
        assert "elevation" in result["non_numeric"]


# ------------------------------------------------------------------ #
# Preprocessing Tests
# ------------------------------------------------------------------ #

class TestPreprocessing:
    def test_pipeline_returns_dataframe(self, sample_df):
        df_clean, stats = preprocess_pipeline(sample_df)
        assert isinstance(df_clean, pd.DataFrame)
        assert isinstance(stats, dict)

    def test_no_missing_after_pipeline(self, sample_df):
        # Introduce missing values
        df = sample_df.copy()
        df.loc[0, "vegetation_index"] = None
        df.loc[1, "rainfall"] = None
        df_clean, stats = preprocess_pipeline(df, handle_missing="median")
        numeric_cols = [c for c in df_clean.columns if pd.api.types.is_numeric_dtype(df_clean[c])]
        assert df_clean[numeric_cols].isnull().sum().sum() == 0

    def test_duplicate_removal(self, sample_df):
        df = pd.concat([sample_df.head(5), sample_df.head(5)], ignore_index=True)
        df_clean, stats = preprocess_pipeline(df, remove_duplicates=True)
        assert stats["duplicates_found"] == 5

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        df_clean, stats = preprocess_pipeline(df)
        assert len(df_clean) == 0


# ------------------------------------------------------------------ #
# Feature Engineering Tests
# ------------------------------------------------------------------ #

class TestFeatureEngineering:
    def test_indicators_added(self, sample_df):
        df_clean, _ = preprocess_pipeline(sample_df)
        result = compute_all_indicators(df_clean)
        for col in [
            "vegetation_stress", "soil_degradation_risk", "water_stress",
            "habitat_degradation", "biodiversity_risk", "human_pressure_index",
            "overall_degradation",
        ]:
            assert col in result.columns

    def test_indicators_range(self, sample_df):
        df_clean, _ = preprocess_pipeline(sample_df)
        result = compute_all_indicators(df_clean)
        for col in [
            "vegetation_stress", "soil_degradation_risk", "water_stress",
            "habitat_degradation", "biodiversity_risk", "human_pressure_index",
        ]:
            assert result[col].min() >= 0, f"{col} has values below 0"
            assert result[col].max() <= 100, f"{col} has values above 100"


# ------------------------------------------------------------------ #
# Priority Score & Classification Tests
# ------------------------------------------------------------------ #

class TestPriorityScoring:
    def test_priority_score_range(self, processed_df):
        assert processed_df["priority_score"].min() >= 0
        assert processed_df["priority_score"].max() <= 100

    def test_priority_classes_valid(self, processed_df):
        valid = set(PRIORITY_THRESHOLDS.keys())
        assert set(processed_df["priority_class"].unique()).issubset(valid)

    def test_weights_sum_to_one(self):
        total = sum(PRIORITY_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01

    @pytest.mark.parametrize("score,expected_class", [
        (0, "LOW"),
        (25, "LOW"),
        (26, "MODERATE"),
        (50, "MODERATE"),
        (51, "HIGH"),
        (75, "HIGH"),
        (76, "CRITICAL"),
        (100, "CRITICAL"),
    ])
    def test_classification_boundaries(self, score, expected_class):
        result = classify_priority(pd.Series([score]))
        assert result.iloc[0] == expected_class, (
            f"Score {score} should be {expected_class}, got {result.iloc[0]}"
        )


# ------------------------------------------------------------------ #
# Intervention Engine Tests
# ------------------------------------------------------------------ #

class TestInterventionEngine:
    def test_returns_all_interventions(self, processed_df):
        zone = processed_df.iloc[0]
        results = compute_intervention_suitability(zone)
        assert len(results) == 9  # 9 intervention types

    def test_suitability_range(self, processed_df):
        zone = processed_df.iloc[0]
        results = compute_intervention_suitability(zone)
        for item in results:
            assert 0 <= item["score"] <= 100, (
                f"{item['intervention']} score {item['score']} out of range"
            )

    def test_has_reasons(self, processed_df):
        zone = processed_df.iloc[0]
        results = compute_intervention_suitability(zone)
        for item in results:
            assert len(item["reasons"]) > 0

    def test_recommendations_structure(self, processed_df):
        zone = processed_df.iloc[0]
        rec = get_zone_interventions(zone)
        assert "primary" in rec
        assert "secondary" in rec
        assert "supporting" in rec
        assert rec["primary"]["score"] >= rec["secondary"]["score"]


# ------------------------------------------------------------------ #
# Simulation Tests
# ------------------------------------------------------------------ #

class TestSimulation:
    def test_simulation_returns_before_after(self, processed_df):
        zone = processed_df.iloc[0]
        result = simulate_zone(zone, {"vegetation_index": 20})
        assert "before" in result
        assert "after" in result
        assert "changes" in result

    def test_positive_change_improves_vegetation(self, processed_df):
        zone = processed_df.iloc[0]
        result = simulate_zone(zone, {"vegetation_index": 30})
        # Increasing vegetation should generally reduce vegetation stress
        assert result["after"]["indicators"]["vegetation_stress"] <= (
            result["before"]["indicators"]["vegetation_stress"] + 1  # small tolerance
        )

    def test_no_modification_no_change(self, processed_df):
        zone = processed_df.iloc[0]
        result = simulate_zone(zone, {})
        assert abs(result["changes"]["priority_score"]) < 0.1


# ------------------------------------------------------------------ #
# Sample Dataset Tests
# ------------------------------------------------------------------ #

class TestSampleData:
    def test_generates_correct_size(self):
        df = generate_sample_dataset(n=100, save=False)
        assert len(df) == 100

    def test_has_required_columns(self):
        df = generate_sample_dataset(n=10, save=False)
        result = validate_columns(df)
        assert result["valid"] is True

    def test_synthetic_label_present(self):
        df = generate_sample_dataset(n=10, save=False)
        assert "data_source" in df.columns
        assert (df["data_source"] == "SYNTHETIC_DEMO").all()

    def test_values_in_range(self):
        df = generate_sample_dataset(n=500, save=False)
        for col in ["vegetation_index", "soil_degradation", "rainfall",
                     "water_availability", "habitat_quality", "biodiversity_index",
                     "human_pressure", "forest_cover", "drought_index"]:
            assert df[col].min() >= 0, f"{col} has negative values"
            assert df[col].max() <= 100, f"{col} exceeds 100"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def test_decimal_priority_boundaries():
    scores = pd.Series([0, 25, 25.01, 50, 50.5, 75, 75.01, 100])
    assert classify_priority(scores).tolist() == [
        'LOW', 'LOW', 'MODERATE', 'MODERATE', 'HIGH', 'HIGH', 'CRITICAL', 'CRITICAL'
    ]

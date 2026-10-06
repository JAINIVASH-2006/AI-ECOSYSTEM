"""
EcoRestore AI — Data Upload Page
===================================
Upload CSV / GeoJSON files with validation and summary display.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from config.config import MAX_UPLOAD_SIZE_MB
from src.data_loader import (
    generate_sample_dataset,
    get_data_summary,
    get_sample_data,
    load_csv,
    validate_columns,
    validate_coordinates,
    validate_numeric_columns,
)
from src.preprocessing import preprocess_pipeline
from src.feature_engineering import compute_all_indicators
from src.priority_engine import compute_priority
from src.intervention_engine import compute_interventions_for_dataframe


def render():
    """Render the Data Upload page."""
    st.markdown("# 📤 Data Upload")
    st.markdown("Upload your environmental data or use the built-in sample dataset.")

    tab_upload, tab_sample = st.tabs(["📁 Upload File", "🧪 Sample Dataset"])

    # ---- Upload Tab ----
    with tab_upload:
        st.markdown("### Upload Environmental Data")
        st.markdown(
            "Supported formats: **CSV**, **GeoJSON**. "
            f"Max file size: **{MAX_UPLOAD_SIZE_MB} MB**."
        )

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "geojson", "json"],
            help="Upload a CSV or GeoJSON file with environmental data.",
        )

        if uploaded_file is not None:
            try:
                # File size check
                file_size_mb = uploaded_file.size / (1024 * 1024)
                if file_size_mb > MAX_UPLOAD_SIZE_MB:
                    st.error(f"File too large ({file_size_mb:.1f} MB). Max: {MAX_UPLOAD_SIZE_MB} MB.")
                    return

                # Parse file
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith((".geojson", ".json")):
                    import geopandas as gpd
                    import io
                    content = uploaded_file.read().decode("utf-8")
                    gdf = gpd.read_file(io.StringIO(content))
                    df = pd.DataFrame(gdf.drop(columns="geometry", errors="ignore"))
                else:
                    st.error("Unsupported file format.")
                    return

                st.success(f"✅ File loaded: **{uploaded_file.name}** ({len(df)} rows, {len(df.columns)} columns)")

                # Validation
                _show_validation(df)

                # Store and process
                if st.button("🚀 Process Data", type="primary"):
                    _process_and_store(df)

            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.info("Please ensure the file is a valid CSV or GeoJSON with the expected columns.")

    # ---- Sample Data Tab ----
    with tab_sample:
        st.markdown("### Generate Sample Dataset")
        st.warning(
            "⚠️ **SYNTHETIC DATA**: This generates a demo dataset for testing. "
            "Data is clearly synthetic and must not be used for real environmental decisions."
        )

        n_zones = st.slider("Number of zones", 100, 5000, 1000, 100)

        if st.button("🧪 Generate Sample Dataset", type="primary"):
            with st.spinner("Generating synthetic environmental data..."):
                df = generate_sample_dataset(n=n_zones, save=True)
                st.success(f"✅ Generated {len(df)} synthetic zones.")
                _show_validation(df)
                _process_and_store(df)


def _show_validation(df: pd.DataFrame) -> None:
    """Display validation results for a DataFrame."""
    st.markdown("### 🔍 Data Validation")

    col1, col2, col3 = st.columns(3)

    # Column validation
    col_result = validate_columns(df)
    with col1:
        if col_result["valid"]:
            st.success("✅ All required columns present")
        else:
            st.error(f"❌ Missing columns: {', '.join(col_result['missing'])}")
        if col_result["extra"]:
            st.info(f"ℹ️ Extra columns: {', '.join(col_result['extra'][:5])}")

    # Coordinate validation
    coord_result = validate_coordinates(df)
    with col2:
        if coord_result["valid"]:
            st.success("✅ All coordinates valid")
        else:
            st.warning(
                f"⚠️ Invalid coordinates: {coord_result['invalid_lat']} lat, "
                f"{coord_result['invalid_lon']} lon"
            )

    # Numeric validation
    num_result = validate_numeric_columns(df)
    with col3:
        if num_result["valid"]:
            st.success("✅ All numeric columns valid")
        else:
            st.warning(f"⚠️ Non-numeric: {', '.join(num_result['non_numeric'])}")

    # Data summary
    summary = get_data_summary(df)
    st.markdown("### 📊 Data Summary")

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Rows", summary["rows"])
    col_b.metric("Columns", summary["columns"])
    col_c.metric("Missing Values", summary["total_missing"])
    col_d.metric("Duplicates", summary["duplicates"])

    # Missing value details
    missing = {k: v for k, v in summary["missing_per_column"].items() if v > 0}
    if missing:
        with st.expander("📋 Missing Values by Column"):
            st.dataframe(pd.DataFrame([missing]).T.rename(columns={0: "Count"}))

    # Preview
    with st.expander("👀 Data Preview (first 10 rows)"):
        st.dataframe(df.head(10), use_container_width=True)

    # Summary stats
    with st.expander("📈 Summary Statistics"):
        st.dataframe(df.describe().round(2), use_container_width=True)


def _process_and_store(df: pd.DataFrame) -> None:
    """Preprocess, compute indicators, and store in session state."""
    with st.spinner("Processing data..."):
        st.session_state.raw_data = df

        # Preprocess
        df_clean, stats = preprocess_pipeline(df)
        st.session_state.preprocess_stats = stats

        # Indicators
        df_ind = compute_all_indicators(df_clean)

        # Priority
        df_pri = compute_priority(df_ind)

        # Interventions
        df_full = compute_interventions_for_dataframe(df_pri)

        st.session_state.processed_data = df_full

    st.success("✅ Data processed successfully! Navigate to other pages to explore results.")

    # Show preprocessing stats
    with st.expander("🔧 Preprocessing Statistics"):
        for step in stats.get("steps", []):
            st.markdown(f"- {step}")
        st.markdown(f"- **Final rows**: {stats.get('final_rows', 'N/A')}")
        st.markdown(f"- **Rows removed**: {stats.get('rows_removed', 0)}")

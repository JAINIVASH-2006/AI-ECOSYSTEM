"""
EcoRestore AI — Dashboard Page
================================
Main overview with KPI cards, priority distribution, environmental charts,
and a mini interactive map.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from config.config import APP_NAME, SAMPLE_DATA_FILE
from config.thresholds import PRIORITY_CLASSES, PRIORITY_COLORS
from src.data_loader import generate_sample_dataset, get_sample_data, validate_columns
from src.preprocessing import preprocess_pipeline
from src.feature_engineering import compute_all_indicators
from src.priority_engine import compute_priority, get_priority_summary
from src.intervention_engine import compute_interventions_for_dataframe


def _load_and_process_data() -> pd.DataFrame:
    """Load, preprocess, and compute indicators + priority + interventions."""
    if "processed_data" in st.session_state and st.session_state.processed_data is not None:
        return st.session_state.processed_data

    # Generate or load sample data
    if "raw_data" not in st.session_state or st.session_state.raw_data is None:
        df = get_sample_data()
        st.session_state.raw_data = df
    else:
        df = st.session_state.raw_data

    # Preprocess
    df_clean, stats = preprocess_pipeline(df)
    st.session_state.preprocess_stats = stats

    # Feature engineering
    df_indicators = compute_all_indicators(df_clean)

    # Priority scoring
    df_priority = compute_priority(df_indicators)

    # Interventions
    df_full = compute_interventions_for_dataframe(df_priority)

    st.session_state.processed_data = df_full
    return df_full


def _kpi_card(title: str, value: str, css_class: str = "") -> str:
    # Use glass-card and KPI specifics from style.css
    return f'''
    <div class="flex-col">
        <div class="glass-card">
            <p class="kpi-title">{title}</p>
            <p class="kpi-value {css_class}">{value}</p>
        </div>
    </div>
    '''

def render():
    """Render the dashboard page."""
    st.markdown(f"# 🌍 {APP_NAME} Dashboard")
    st.markdown("*AI-Based Ecological Restoration Priority Mapping & Intervention Planning*")

    # Load data
    with st.spinner("Loading and processing environmental data..."):
        try:
            df = _load_and_process_data()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Click '📤 Data Upload' to load your environmental data.")
            return

    if df is None or df.empty:
        st.warning("No data available. Please upload or generate sample data.")
        return

    summary = get_priority_summary(df)

    # ---- KPI Cards ----
    st.markdown('<p class="section-header">📊 Key Performance Indicators</p>', unsafe_allow_html=True)
    
    # Row 1: Priority Distribution
    critical = summary.get("class_counts", {}).get("CRITICAL", 0)
    high = summary.get("class_counts", {}).get("HIGH", 0)
    moderate = summary.get("class_counts", {}).get("MODERATE", 0)
    low = summary.get("class_counts", {}).get("LOW", 0)
    
    html_grid_1 = f'''
    <div class="flex-grid">
        {_kpi_card("Total Zones", str(summary.get("total_zones", 0)))}
        {_kpi_card("Critical Zones", str(critical), "kpi-critical")}
        {_kpi_card("High Priority", str(high), "kpi-high")}
        {_kpi_card("Moderate Priority", str(moderate), "kpi-moderate")}
        {_kpi_card("Low Priority", str(low), "kpi-low")}
    </div>
    '''
    st.markdown(html_grid_1, unsafe_allow_html=True)

    # Row 2: Score Summaries
    html_grid_2 = f'''
    <div class="flex-grid">
        {_kpi_card("Average Priority Score", f"{summary.get('average_score', 0):.1f}")}
        {_kpi_card("Highest Priority Zone", str(summary.get("highest_zone", "N/A")), "kpi-critical")}
        {_kpi_card("Max Priority Score", f"{summary.get('max_score', 0):.1f}/100", "kpi-high")}
    </div>
    '''
    st.markdown(html_grid_2, unsafe_allow_html=True)

    st.markdown("---")

    # ---- Charts ----
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<p class="section-header">🎯 Priority Distribution</p>', unsafe_allow_html=True)
        class_counts = summary.get("class_counts", {})
        dist_df = pd.DataFrame([
            {"Priority Class": cls, "Count": class_counts.get(cls, 0)}
            for cls in PRIORITY_CLASSES
        ])
        fig_dist = px.bar(
            dist_df, x="Priority Class", y="Count",
            color="Priority Class",
            color_discrete_map=PRIORITY_COLORS,
            title="Zones by Priority Classification",
        )
        fig_dist.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_right:
        st.markdown('<p class="section-header">📈 Priority Score Distribution</p>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            df, x="priority_score", nbins=25,
            color_discrete_sequence=["#667eea"],
            title="Restoration Priority Score Distribution",
            labels={"priority_score": "Priority Score (0-100)"},
        )
        fig_hist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Row 2
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown('<p class="section-header">🌡️ Environmental Conditions Overview</p>', unsafe_allow_html=True)
        indicator_cols = [
            "vegetation_stress", "soil_degradation_risk", "water_stress",
            "habitat_degradation", "biodiversity_risk", "human_pressure_index",
        ]
        present_cols = [c for c in indicator_cols if c in df.columns]
        if present_cols:
            means = df[present_cols].mean().round(1)
            fig_env = go.Figure(data=[
                go.Bar(
                    x=[c.replace("_", " ").title() for c in means.index],
                    y=means.values,
                    marker_color=["#e74c3c", "#e67e22", "#3498db", "#27ae60", "#9b59b6", "#f39c12"],
                )
            ])
            fig_env.update_layout(
                title="Average Environmental Indicator Values (0-100, High = Bad)",
                yaxis_title="Average Value",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
            )
            st.plotly_chart(fig_env, use_container_width=True)

    with col_right2:
        st.markdown('<p class="section-header">🌱 Top Interventions Recommended</p>', unsafe_allow_html=True)
        if "primary_intervention" in df.columns:
            intervention_counts = df["primary_intervention"].value_counts().head(8)
            fig_int = px.pie(
                values=intervention_counts.values,
                names=intervention_counts.index,
                title="Distribution of Primary Interventions",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_int.update_layout(
                font=dict(family="Inter"),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_int, use_container_width=True)

    # ---- Mini Map ----
    st.markdown('<p class="section-header">🗺️ Restoration Priority Overview Map</p>', unsafe_allow_html=True)
    if "latitude" in df.columns and "longitude" in df.columns:
        # Use Streamlit's built-in map for quick overview
        map_df = df[["latitude", "longitude", "priority_score"]].dropna()
        st.map(map_df, latitude="latitude", longitude="longitude", size="priority_score")
        st.caption("Marker size represents priority score. Click '🗺️ Restoration Priority Map' for the full interactive map.")

    # ---- Data Source Notice ----
    if "data_source" in df.columns and (df["data_source"] == "SYNTHETIC_DEMO").any():
        st.info(
            "⚠️ **Synthetic Demo Data**: The current dataset is generated for demonstration "
            "purposes. Upload real environmental data via '📤 Data Upload' for actual analysis."
        )

"""
EcoRestore AI — Environmental Analysis Page
=============================================
Interactive analysis of vegetation, soil, water, habitat, biodiversity,
and human pressure with histograms, box plots, correlation matrix, and
risk rankings.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np


# Columns for analysis
RAW_FEATURES = [
    "vegetation_index", "soil_degradation", "rainfall", "water_availability",
    "land_use_change", "habitat_quality", "biodiversity_index",
    "human_pressure", "elevation", "slope", "forest_cover", "drought_index",
]

INDICATOR_COLS = [
    "vegetation_stress", "soil_degradation_risk", "water_stress",
    "habitat_degradation", "biodiversity_risk", "human_pressure_index",
    "overall_degradation",
]


def render():
    """Render the Environmental Analysis page."""
    st.markdown("# 📊 Environmental Analysis")
    st.markdown("Explore environmental conditions across all zones.")

    if "processed_data" not in st.session_state or st.session_state.processed_data is None:
        st.warning("⚠️ No data loaded. Go to **📤 Data Upload** first.")
        return

    df = st.session_state.processed_data

    tab_overview, tab_indicators, tab_correlation, tab_rankings = st.tabs([
        "📊 Overview", "🌡️ Indicators", "🔗 Correlation", "📋 Risk Rankings"
    ])

    # ---- Overview Tab ----
    with tab_overview:
        st.markdown("### Raw Environmental Features")

        col_select = st.selectbox(
            "Select feature to analyze",
            [c for c in RAW_FEATURES if c in df.columns],
            key="env_feature_select",
        )

        if col_select:
            col_l, col_r = st.columns(2)

            with col_l:
                fig_hist = px.histogram(
                    df, x=col_select, nbins=30,
                    color_discrete_sequence=["#667eea"],
                    title=f"Distribution of {col_select.replace('_', ' ').title()}",
                    marginal="box",
                )
                fig_hist.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            with col_r:
                fig_box = px.box(
                    df, y=col_select,
                    color_discrete_sequence=["#764ba2"],
                    title=f"Box Plot: {col_select.replace('_', ' ').title()}",
                    points="outliers",
                )
                fig_box.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                )
                st.plotly_chart(fig_box, use_container_width=True)

            # Stats
            with st.expander("📈 Summary Statistics"):
                stats = df[col_select].describe().round(2)
                st.dataframe(pd.DataFrame(stats).T, use_container_width=True)

        # Multi-feature box plot
        st.markdown("### All Environmental Features")
        avail_raw = [c for c in RAW_FEATURES if c in df.columns]
        if avail_raw:
            melt_df = df[avail_raw].melt(var_name="Feature", value_name="Value")
            fig_multi = px.box(
                melt_df, x="Feature", y="Value",
                color="Feature",
                title="Environmental Feature Distributions",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_multi.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                height=500,
            )
            st.plotly_chart(fig_multi, use_container_width=True)

    # ---- Indicators Tab ----
    with tab_indicators:
        st.markdown("### Environmental Indicators (0–100, High = Bad)")
        st.info("All indicators are normalised so that **higher values indicate worse conditions**.")

        avail_ind = [c for c in INDICATOR_COLS if c in df.columns]

        if avail_ind:
            # Radar chart of average indicators
            means = df[avail_ind].mean().round(1)
            categories = [c.replace("_", " ").title() for c in means.index]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=list(means.values) + [means.values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(102, 126, 234, 0.3)",
                line=dict(color="#667eea", width=2),
                name="Average",
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title="Average Environmental Indicators",
                font=dict(family="Inter"),
                height=450,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # Individual indicator histograms
            ind_select = st.selectbox(
                "Select indicator",
                avail_ind,
                format_func=lambda x: x.replace("_", " ").title(),
                key="indicator_select",
            )
            if ind_select:
                fig_ind = px.histogram(
                    df, x=ind_select, nbins=30,
                    color_discrete_sequence=["#e74c3c"],
                    title=f"{ind_select.replace('_', ' ').title()} Distribution",
                    marginal="rug",
                )
                fig_ind.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                )
                st.plotly_chart(fig_ind, use_container_width=True)

    # ---- Correlation Tab ----
    with tab_correlation:
        st.markdown("### Feature Correlation Matrix")

        corr_cols = [c for c in RAW_FEATURES + INDICATOR_COLS if c in df.columns]
        if len(corr_cols) > 2:
            corr_matrix = df[corr_cols].corr().round(2)

            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                title="Environmental Feature Correlation Matrix",
                aspect="auto",
            )
            fig_corr.update_layout(
                font=dict(family="Inter", size=9),
                height=700,
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Not enough numeric columns for correlation analysis.")

    # ---- Risk Rankings Tab ----
    with tab_rankings:
        st.markdown("### Environmental Risk Rankings")
        st.markdown("Zones ranked by worst environmental conditions.")

        ranking_col = st.selectbox(
            "Rank by",
            [c for c in INDICATOR_COLS + ["priority_score"] if c in df.columns],
            format_func=lambda x: x.replace("_", " ").title(),
            key="ranking_col",
        )

        if ranking_col:
            top_n = st.slider("Number of zones to show", 5, 50, 20, key="ranking_n")
            ranked = df.nlargest(top_n, ranking_col)

            display_cols = ["zone_id", ranking_col] + [
                c for c in ["priority_score", "priority_class", "latitude", "longitude"]
                if c in ranked.columns and c != ranking_col
            ]
            st.dataframe(
                ranked[display_cols].reset_index(drop=True),
                use_container_width=True,
            )

            # Bar chart of top zones
            fig_rank = px.bar(
                ranked.head(15),
                x="zone_id", y=ranking_col,
                color=ranking_col,
                color_continuous_scale="Reds",
                title=f"Top {min(15, top_n)} Zones by {ranking_col.replace('_', ' ').title()}",
            )
            fig_rank.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
            )
            st.plotly_chart(fig_rank, use_container_width=True)

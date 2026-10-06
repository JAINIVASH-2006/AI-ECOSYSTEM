"""
EcoRestore AI — Intervention Planner Page
============================================
Zone-specific intervention suitability ranking with reasons.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import pandas as pd

from src.intervention_engine import get_zone_interventions, compute_intervention_suitability


def render():
    """Render the Intervention Planner page."""
    st.markdown("# 🌱 Intervention Planner")
    st.markdown(
        "Select a zone to view recommended ecological restoration interventions "
        "with suitability scores and reasoning."
    )

    if "processed_data" not in st.session_state or st.session_state.processed_data is None:
        st.warning("⚠️ No data loaded. Go to **📤 Data Upload** first.")
        return

    df = st.session_state.processed_data

    zone_ids = df["zone_id"].tolist() if "zone_id" in df.columns else []
    if not zone_ids:
        st.info("No zones available.")
        return

    # Zone selector
    col_sel, col_info = st.columns([1, 2])

    with col_sel:
        selected_zone = st.selectbox("Select Zone", zone_ids, key="intervention_zone")

    if not selected_zone:
        return

    zone_row = df[df["zone_id"] == selected_zone].iloc[0]

    with col_info:
        score = zone_row.get("priority_score", 0)
        cls = zone_row.get("priority_class", "N/A")
        st.markdown(f"**Priority:** {score:.1f}/100 — **{cls}**")

    st.markdown("---")

    # ---- Environmental Condition Summary ----
    st.markdown('<p class="section-header">🌡️ Environmental Condition</p>', unsafe_allow_html=True)
    indicators = [
        ("Vegetation Stress", "vegetation_stress"),
        ("Soil Degradation", "soil_degradation_risk"),
        ("Water Stress", "water_stress"),
        ("Habitat Degradation", "habitat_degradation"),
        ("Biodiversity Risk", "biodiversity_risk"),
        ("Human Pressure", "human_pressure_index"),
    ]
    
    html_grid = '<div class="flex-grid">'
    for label, col in indicators:
        val = zone_row.get(col, 0)
        color = "#e74c3c" if val > 60 else "#f39c12" if val > 30 else "#10b981"
        html_grid += f'''<div class="flex-col">
<div class="glass-card" style="text-align: center; padding: 15px;">
<div style="font-size:0.75rem; color:#94a3b8; margin-bottom: 5px;">{label}</div>
<div style="font-size:1.75rem; font-weight:700; color:{color};">{val:.0f}</div>
</div>
</div>'''
    html_grid += '</div>'
    st.markdown(html_grid, unsafe_allow_html=True)

    st.markdown("---")

    # ---- Intervention Suitability ----
    st.markdown('<p class="section-header">🎯 Intervention Suitability Ranking</p>', unsafe_allow_html=True)

    all_interventions = compute_intervention_suitability(zone_row)

    # Bar chart
    int_df = pd.DataFrame(all_interventions)
    fig = px.bar(
        int_df, x="score", y="intervention",
        orientation="h",
        color="score",
        color_continuous_scale=["#27ae60", "#f1c40f", "#e67e22", "#e74c3c"],
        title="Intervention Suitability Scores (0–100)",
        labels={"score": "Suitability Score", "intervention": "Intervention"},
    )
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Detailed Recommendations ----
    st.markdown('<p class="section-header">📋 Detailed Recommendations</p>', unsafe_allow_html=True)

    rec = get_zone_interventions(zone_row)

    for rank, (label, key, emoji) in enumerate([
        ("Primary", "primary", "🥇"),
        ("Secondary", "secondary", "🥈"),
        ("Supporting", "supporting", "🥉"),
    ]):
        inter = rec.get(key)
        if inter:
            with st.expander(
                f"{emoji} **{label}: {inter['intervention']}** — Suitability: {inter['score']:.0f}/100",
                expanded=(rank == 0),
            ):
                st.markdown(f"**Suitability Score:** {inter['score']:.1f} / 100")
                st.markdown("**Why this intervention is recommended:**")
                timeline_html = '<div class="timeline">'
                for reason in inter.get("reasons", []):
                    timeline_html += f'''<div class="timeline-item">
<div class="timeline-icon"></div>
<div class="timeline-content">
<p>{reason}</p>
</div>
</div>'''
                timeline_html += '</div>'
                st.markdown(timeline_html, unsafe_allow_html=True)

                # Expected objectives
                objectives = _get_objectives(inter["intervention"])
                st.markdown("**Expected Environmental Objectives:**")
                for obj in objectives:
                    st.markdown(f"- {obj}")

    # ---- Full Ranking Table ----
    with st.expander("📊 Full Intervention Ranking"):
        table_data = []
        for item in all_interventions:
            table_data.append({
                "Intervention": item["intervention"],
                "Suitability Score": item["score"],
                "Top Reason": item["reasons"][0] if item["reasons"] else "—",
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)


def _get_objectives(intervention: str) -> list:
    """Return expected environmental objectives for an intervention type."""
    objectives = {
        "Afforestation": [
            "Increase forest cover and canopy density",
            "Reduce soil erosion through root stabilisation",
            "Improve carbon sequestration capacity",
            "Enhance local biodiversity habitat",
        ],
        "Reforestation": [
            "Restore degraded forest ecosystems",
            "Rebuild wildlife corridors and habitat connectivity",
            "Improve watershed protection",
            "Enhance biodiversity through native species recovery",
        ],
        "Soil Conservation": [
            "Reduce soil erosion and land degradation",
            "Improve soil fertility and organic matter",
            "Enhance water retention capacity",
            "Prevent further land productivity decline",
        ],
        "Agroforestry": [
            "Integrate trees with agricultural systems",
            "Improve soil health through diverse root systems",
            "Provide sustainable livelihood opportunities",
            "Reduce pressure on natural forests",
        ],
        "Rainwater Harvesting": [
            "Increase water availability during dry seasons",
            "Reduce dependency on groundwater extraction",
            "Support irrigation for restoration plantings",
            "Improve local water table levels",
        ],
        "Watershed Management": [
            "Improve catchment-level water management",
            "Reduce flood risk and water runoff",
            "Enhance aquifer recharge",
            "Protect downstream water quality",
        ],
        "Habitat Restoration": [
            "Rebuild critical wildlife habitats",
            "Restore ecological connectivity",
            "Support endangered species recovery",
            "Improve ecosystem resilience",
        ],
        "Native Vegetation Restoration": [
            "Re-establish native plant communities",
            "Reduce invasive species dominance",
            "Restore natural ecosystem processes",
            "Enhance pollinator and wildlife support",
        ],
        "Erosion Control": [
            "Stabilise slopes and reduce mass movement risk",
            "Protect topsoil from wind and water erosion",
            "Maintain agricultural land productivity",
            "Reduce sedimentation in water bodies",
        ],
    }
    return objectives.get(intervention, ["Improve overall environmental conditions."])

"""
EcoRestore AI — Priority Map Page
====================================
Full interactive Folium map with filters and zone detail panel.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from config.thresholds import (
    PRIORITY_CLASSES,
    PRIORITY_COLORS,
    PRIORITY_THRESHOLDS,
    INTERVENTION_TYPES,
)
from src.gis import create_priority_map, save_map
from src.intervention_engine import get_zone_interventions
from src.explainability import explain_zone


def _priority_badge(cls: str) -> str:
    color = PRIORITY_COLORS.get(cls, "#95a5a6")
    return (
        f'<span style="background:{color};color:#fff;padding:4px 12px;'
        f'border-radius:20px;font-weight:600;font-size:.85rem;">{cls}</span>'
    )


def render():
    """Render the Restoration Priority Map page."""
    st.markdown("# 🗺️ Restoration Priority Map")
    st.markdown("Interactive map showing ecological restoration priorities across all zones.")

    if "processed_data" not in st.session_state or st.session_state.processed_data is None:
        st.warning("⚠️ No data loaded. Go to **📤 Data Upload** first.")
        return

    df = st.session_state.processed_data

    # ---- Filters ----
    st.markdown('<p class="section-header">🔍 Filters</p>', unsafe_allow_html=True)

    filter_cols = st.columns([2, 1, 1, 1, 1])

    with filter_cols[0]:
        selected_classes = st.multiselect(
            "Priority Class",
            PRIORITY_CLASSES,
            default=PRIORITY_CLASSES,
            key="map_class_filter",
        )

    with filter_cols[1]:
        min_score = st.slider("Minimum Priority Score", 0, 100, 0, key="map_min_score")

    with filter_cols[2]:
        intervention_filter = st.selectbox(
            "Primary Intervention",
            ["All"] + INTERVENTION_TYPES,
            key="map_intervention_filter",
        )

    with filter_cols[3]:
        max_zones = st.selectbox(
            "Max zones on map",
            [100, 250, 500, 1000, "All"],
            index=2,
            key="map_max_zones",
        )

    with filter_cols[4]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset", help="Reset all filters to defaults"):
            for key in [
                "map_class_filter", "map_min_score",
                "map_intervention_filter", "map_max_zones",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Apply filters
    filtered = df.copy()
    if selected_classes:
        filtered = filtered[filtered["priority_class"].isin(selected_classes)]
    filtered = filtered[filtered["priority_score"] >= min_score]
    if intervention_filter != "All" and "primary_intervention" in filtered.columns:
        filtered = filtered[filtered["primary_intervention"] == intervention_filter]
    if max_zones != "All":
        filtered = filtered.head(int(max_zones))

    # ---- Smart conflict warning ----
    if min_score > 0 and selected_classes and len(filtered) == 0:
        max_possible = max(
            PRIORITY_THRESHOLDS.get(cls, (0, 0))[1]
            for cls in selected_classes
        )
        if min_score > max_possible:
            st.warning(
                f"⚠️ **Filter conflict:** The selected class(es) "
                f"({', '.join(selected_classes)}) have a maximum priority score of "
                f"**{max_possible}**, but the slider requires ≥ **{min_score}**. "
                f"Lower the slider or include higher-priority classes (e.g. CRITICAL). "
                f"Click **🔄 Reset** to restore defaults."
            )
        else:
            st.warning("⚠️ No zones match the selected filters. Try relaxing them.")

    st.markdown(f"**Showing {len(filtered)} zones** (filtered from {len(df)} total)")

    # ---- Map ----
    if len(filtered) == 0:
        st.info("Adjust the filters above to display zones on the map.")
        return

    with st.spinner("Building interactive map..."):
        m = create_priority_map(filtered)

    # Legend
    legend_html = " ".join([
        f'<span style="background:{c};color:#fff;padding:3px 10px;border-radius:12px;'
        f'margin-right:8px;font-size:.8rem;">{cls}</span>'
        for cls, c in PRIORITY_COLORS.items()
    ])
    st.markdown(f"**Legend:** {legend_html}", unsafe_allow_html=True)

    st_folium(m, width="100%", height=550, returned_objects=[])

    # Save map button
    col_save, _ = st.columns([1, 4])
    with col_save:
        if st.button("💾 Save Map as HTML"):
            path = save_map(m)
            st.success(f"Map saved to: `{path}`")

    # ---- Zone Detail Panel ----
    st.markdown("---")
    st.markdown('<p class="section-header">🔎 Zone Detail View</p>', unsafe_allow_html=True)

    zone_ids = filtered["zone_id"].tolist() if "zone_id" in filtered.columns else []
    if not zone_ids:
        st.info("No zones available for detail view.")
        return

    selected_zone_id = st.selectbox("Select a zone", zone_ids, key="map_zone_select")

    if selected_zone_id:
        zone_row = filtered[filtered["zone_id"] == selected_zone_id].iloc[0]

        col_info, col_indicators, col_interventions = st.columns(3)

        with col_info:
            st.markdown("#### 📍 Zone Information")
            st.markdown(f"**Zone ID:** {zone_row.get('zone_id', 'N/A')}")
            st.markdown(f"**Latitude:** {zone_row.get('latitude', 'N/A'):.4f}")
            st.markdown(f"**Longitude:** {zone_row.get('longitude', 'N/A'):.4f}")
            st.markdown(f"**Elevation:** {zone_row.get('elevation', 'N/A'):.0f} m")
            score = zone_row.get("priority_score", 0)
            cls = zone_row.get("priority_class", "N/A")
            st.markdown(f"**Priority Score:** {score:.1f} / 100")
            st.markdown(f"**Priority Class:** {_priority_badge(cls)}", unsafe_allow_html=True)

        with col_indicators:
            st.markdown("#### 🌡️ Environmental Indicators")
            indicators = {
                "Vegetation Stress": zone_row.get("vegetation_stress"),
                "Soil Degradation": zone_row.get("soil_degradation_risk"),
                "Water Stress": zone_row.get("water_stress"),
                "Habitat Degradation": zone_row.get("habitat_degradation"),
                "Biodiversity Risk": zone_row.get("biodiversity_risk"),
                "Human Pressure": zone_row.get("human_pressure_index"),
            }
            for name, val in indicators.items():
                if val is not None:
                    bar_color = "#e74c3c" if val > 60 else "#f39c12" if val > 30 else "#27ae60"
                    st.markdown(
                        f"**{name}:** {val:.1f} "
                        f'<span style="color:{bar_color};font-weight:700;">●</span>',
                        unsafe_allow_html=True,
                    )
                    st.progress(min(val / 100, 1.0))

        with col_interventions:
            st.markdown("#### 🌱 Recommended Interventions")
            interventions = get_zone_interventions(zone_row)

            for label, key in [
                ("🥇 Primary", "primary"),
                ("🥈 Secondary", "secondary"),
                ("🥉 Supporting", "supporting"),
            ]:
                inter = interventions.get(key)
                if inter:
                    st.markdown(f"**{label}:** {inter['intervention']} ({inter['score']:.0f})")
                    with st.expander(f"Why {inter['intervention']}?"):
                        for r in inter.get("reasons", []):
                            st.markdown(f"- {r}")

        # Expandable full explanation
        with st.expander("🧠 Detailed Priority Explanation"):
            explanation = explain_zone(zone_row)
            for factor in explanation["factors"]:
                st.markdown(
                    f"- **{factor['name']}**: {factor['value']:.1f} "
                    f"({factor['contribution']} contribution)"
                )

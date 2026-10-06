"""
EcoRestore AI — GIS Module
============================
Interactive map generation using Folium and GeoPandas.

Creates color-coded restoration priority maps with clickable zone popups
showing environmental profiles and intervention recommendations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import folium
import folium.plugins
import numpy as np
import pandas as pd

from config.config import MAP_CENTER_LAT, MAP_CENTER_LON, MAP_TILES, MAP_ZOOM, MAPS_DIR
from config.thresholds import (
    INDICATOR_COLOR_SCALE,
    MAP_FILL_OPACITY,
    MAP_MARKER_OPACITY,
    MAP_MARKER_RADIUS,
    PRIORITY_COLORS,
)


def _get_priority_color(priority_class: str) -> str:
    """Return a hex color for the priority class."""
    return PRIORITY_COLORS.get(priority_class, "#95a5a6")


def _get_indicator_color(value: float) -> str:
    """Return a hex color based on indicator value (0–100, high = bad)."""
    if value <= 25:
        return "#27ae60"  # green
    elif value <= 50:
        return "#f1c40f"  # yellow
    elif value <= 75:
        return "#e67e22"  # orange
    else:
        return "#e74c3c"  # red


def _build_popup_html(row: pd.Series) -> str:
    """Build rich HTML popup for a zone marker."""
    zone_id = row.get("zone_id", "N/A")
    score = row.get("priority_score", 0)
    cls = row.get("priority_class", "N/A")
    color = _get_priority_color(cls)

    indicators = {
        "Vegetation Stress": row.get("vegetation_stress", "—"),
        "Soil Degradation": row.get("soil_degradation_risk", "—"),
        "Water Stress": row.get("water_stress", "—"),
        "Habitat Degradation": row.get("habitat_degradation", "—"),
        "Biodiversity Risk": row.get("biodiversity_risk", "—"),
        "Human Pressure": row.get("human_pressure_index", "—"),
    }

    primary = row.get("primary_intervention", "N/A")
    primary_score = row.get("primary_intervention_score", "—")
    secondary = row.get("secondary_intervention", "N/A")
    supporting = row.get("supporting_intervention", "N/A")

    ind_rows = ""
    for name, val in indicators.items():
        val_f = f"{val:.1f}" if isinstance(val, (int, float)) else str(val)
        ind_color = _get_indicator_color(float(val)) if isinstance(val, (int, float)) else "#95a5a6"
        ind_rows += (
            f"<tr><td style='padding:2px 6px;'>{name}</td>"
            f"<td style='padding:2px 6px;text-align:right;color:{ind_color};font-weight:600;'>"
            f"{val_f}</td></tr>"
        )

    html = f"""
    <div style="font-family:Arial,sans-serif;width:280px;">
        <h4 style="margin:0 0 4px;color:#2c3e50;">🌍 {zone_id}</h4>
        <div style="background:{color};color:#fff;padding:4px 8px;border-radius:4px;
                    display:inline-block;font-weight:700;margin-bottom:6px;">
            {cls} — {score:.1f}/100
        </div>
        <table style="width:100%;font-size:12px;border-collapse:collapse;margin-top:4px;">
            <tr style="background:#ecf0f1;"><th colspan=2 style="padding:3px;">Environmental Indicators</th></tr>
            {ind_rows}
        </table>
        <div style="margin-top:6px;font-size:12px;">
            <b>Primary:</b> {primary} ({primary_score})<br/>
            <b>Secondary:</b> {secondary}<br/>
            <b>Supporting:</b> {supporting}
        </div>
    </div>
    """
    return html


def create_priority_map(
    df: pd.DataFrame,
    center: Optional[tuple] = None,
    zoom: int = MAP_ZOOM,
) -> folium.Map:
    """Create an interactive Folium map with priority-colored zone markers.

    Parameters
    ----------
    df : pd.DataFrame
        Processed data with lat/lon, indicators, priority, and interventions.
    center : tuple, optional
        ``(lat, lon)`` for map center.  Auto-detected from data if *None*.
    zoom : int
        Initial zoom level.

    Returns
    -------
    folium.Map
    """
    if center is None:
        if "latitude" in df.columns and "longitude" in df.columns:
            center = (df["latitude"].mean(), df["longitude"].mean())
        else:
            center = (MAP_CENTER_LAT, MAP_CENTER_LON)

    m = folium.Map(location=center, zoom_start=zoom, tiles=MAP_TILES)

    # ---- Priority Layer (default on) ----
    priority_layer = folium.FeatureGroup(name="🔴 Restoration Priority", show=True)
    cluster = folium.plugins.MarkerCluster(
        options={"maxClusterRadius": 40, "disableClusteringAtZoom": 10}
    )
    for _, row in df.iterrows():
        if pd.isna(row.get("latitude")) or pd.isna(row.get("longitude")):
            continue
        color = _get_priority_color(row.get("priority_class", "LOW"))
        popup_html = _build_popup_html(row)
        folium.CircleMarker(
            location=(row["latitude"], row["longitude"]),
            radius=MAP_MARKER_RADIUS,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=MAP_FILL_OPACITY,
            opacity=MAP_MARKER_OPACITY,
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"{row.get('zone_id', '')} — {row.get('priority_class', '')}",
        ).add_to(cluster)
    cluster.add_to(priority_layer)
    priority_layer.add_to(m)

    # ---- Indicator Layers (default off) ----
    indicator_layers = {
        "🌿 Vegetation Stress": "vegetation_stress",
        "🪨 Soil Degradation": "soil_degradation_risk",
        "💧 Water Stress": "water_stress",
        "🏞️ Habitat Condition": "habitat_degradation",
        "🦎 Biodiversity Risk": "biodiversity_risk",
        "👤 Human Pressure": "human_pressure_index",
    }

    for layer_name, col in indicator_layers.items():
        if col not in df.columns:
            continue
        fg = folium.FeatureGroup(name=layer_name, show=False)
        for _, row in df.iterrows():
            if pd.isna(row.get("latitude")) or pd.isna(row.get("longitude")):
                continue
            val = row.get(col, 50)
            color = _get_indicator_color(float(val))
            folium.CircleMarker(
                location=(row["latitude"], row["longitude"]),
                radius=MAP_MARKER_RADIUS - 1,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=MAP_FILL_OPACITY,
                opacity=MAP_MARKER_OPACITY,
                tooltip=f"{row.get('zone_id', '')} — {col.replace('_', ' ').title()}: {val:.1f}",
            ).add_to(fg)
        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def save_map(m: folium.Map, filename: str = "priority_map.html") -> Path:
    """Save a Folium map to the outputs/maps directory."""
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    path = MAPS_DIR / filename
    m.save(str(path))
    return path

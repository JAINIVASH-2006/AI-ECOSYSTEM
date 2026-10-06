"""
EcoRestore AI — Reporting Module
==================================
Generate zone reports, CSV exports, and PDF reports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from config.config import REPORTS_DIR
from src.intervention_engine import get_zone_interventions


def generate_zone_report(
    zone: pd.Series,
    simulation_result: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Generate a comprehensive report dict for a single zone.

    Parameters
    ----------
    zone : pd.Series
        Processed row with indicators, priority, and interventions.
    simulation_result : dict, optional
        What-if simulation result to include.

    Returns
    -------
    dict
        Structured report data.
    """
    interventions = get_zone_interventions(zone)

    report = {
        "zone_id": zone.get("zone_id", "Unknown"),
        "latitude": zone.get("latitude"),
        "longitude": zone.get("longitude"),
        "elevation": zone.get("elevation"),
        "environmental_indicators": {
            "Vegetation Stress": zone.get("vegetation_stress"),
            "Soil Degradation Risk": zone.get("soil_degradation_risk"),
            "Water Stress": zone.get("water_stress"),
            "Habitat Degradation": zone.get("habitat_degradation"),
            "Biodiversity Risk": zone.get("biodiversity_risk"),
            "Human Pressure Index": zone.get("human_pressure_index"),
            "Overall Degradation": zone.get("overall_degradation"),
        },
        "priority_score": zone.get("priority_score"),
        "priority_class": zone.get("priority_class"),
        "primary_intervention": interventions.get("primary"),
        "secondary_intervention": interventions.get("secondary"),
        "supporting_intervention": interventions.get("supporting"),
        "all_interventions": interventions.get("all_interventions"),
    }

    if simulation_result:
        report["simulation"] = simulation_result

    return report


def export_to_csv(
    df: pd.DataFrame,
    filename: str = "analysis_results.csv",
) -> Path:
    """Export a DataFrame to CSV in the reports directory.

    Returns
    -------
    Path
        Path to the saved CSV file.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / filename
    df.to_csv(path, index=False)
    return path


def export_zone_report_csv(
    zone: pd.Series,
    filename: Optional[str] = None,
) -> Path:
    """Export a single zone's report as a CSV row."""
    if filename is None:
        zid = zone.get("zone_id", "unknown")
        filename = f"zone_report_{zid}.csv"
    df = pd.DataFrame([zone])
    return export_to_csv(df, filename)


def generate_pdf_report(
    report: Dict[str, Any],
    filename: Optional[str] = None,
) -> Optional[Path]:
    """Generate a PDF report for a zone.

    Returns None if fpdf2 is not available.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    zid = report.get("zone_id", "unknown")
    if filename is None:
        filename = f"zone_report_{zid}.pdf"
    path = REPORTS_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "EcoRestore AI - Zone Report", ln=True, align="C")
    pdf.ln(5)

    # Zone info
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Zone: {zid}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Latitude: {report.get('latitude', 'N/A')}", ln=True)
    pdf.cell(0, 6, f"Longitude: {report.get('longitude', 'N/A')}", ln=True)
    pdf.cell(0, 6, f"Elevation: {report.get('elevation', 'N/A')}", ln=True)
    pdf.ln(4)

    # Priority
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Restoration Priority", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Priority Score: {report.get('priority_score', 'N/A')}/100", ln=True)
    pdf.cell(0, 6, f"Priority Class: {report.get('priority_class', 'N/A')}", ln=True)
    pdf.ln(4)

    # Environmental Indicators
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Environmental Indicators (0-100, High = Bad)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    indicators = report.get("environmental_indicators", {})
    for name, val in indicators.items():
        val_str = f"{val:.1f}" if isinstance(val, (int, float)) else str(val)
        pdf.cell(0, 6, f"  {name}: {val_str}", ln=True)
    pdf.ln(4)

    # Interventions
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Recommended Interventions", ln=True)
    pdf.set_font("Helvetica", "", 10)

    for label, key in [("Primary", "primary_intervention"),
                       ("Secondary", "secondary_intervention"),
                       ("Supporting", "supporting_intervention")]:
        intervention = report.get(key)
        if intervention:
            name = intervention.get("intervention", "N/A")
            score = intervention.get("score", "N/A")
            pdf.cell(0, 6, f"  {label}: {name} (Suitability: {score})", ln=True)
            reasons = intervention.get("reasons", [])
            for r in reasons[:3]:
                pdf.cell(0, 5, f"    - {r}", ln=True)
    pdf.ln(4)

    # Simulation if available
    sim = report.get("simulation")
    if sim:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "What-If Simulation Results", ln=True)
        pdf.set_font("Helvetica", "", 10)
        before = sim.get("before", {})
        after = sim.get("after", {})
        pdf.cell(
            0, 6,
            f"  Priority: {before.get('priority_score', 'N/A')} -> "
            f"{after.get('priority_score', 'N/A')}",
            ln=True,
        )
        pdf.cell(
            0, 6,
            f"  Class: {before.get('priority_class', 'N/A')} -> "
            f"{after.get('priority_class', 'N/A')}",
            ln=True,
        )

    # Disclaimer
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0, 4,
        "Disclaimer: This report provides estimated priority assessments "
        "and recommended interventions for decision-support purposes only. "
        "It does not replace professional ecological expertise.",
    )

    pdf.output(str(path))
    return path


def export_full_analysis(
    df: pd.DataFrame,
    filename: str = "full_analysis.csv",
) -> Path:
    """Export the complete analysis DataFrame."""
    return export_to_csv(df, filename)

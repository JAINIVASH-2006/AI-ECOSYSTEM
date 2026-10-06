"""
EcoRestore AI — Reports & Model Performance Page
====================================================
Zone report viewer, CSV/PDF export, and model performance display.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from src.reporting import (
    export_full_analysis,
    export_zone_report_csv,
    generate_pdf_report,
    generate_zone_report,
)
from src.database import init_database, save_environmental_data, save_zones


def render():
    """Render the Reports page."""
    st.markdown("# 📋 Reports & Export")
    st.markdown("Generate reports, export data, and manage database persistence.")

    if "processed_data" not in st.session_state or st.session_state.processed_data is None:
        st.warning("⚠️ No data loaded. Go to **📤 Data Upload** first.")
        return

    df = st.session_state.processed_data

    tab_zone, tab_export, tab_db = st.tabs([
        "📄 Zone Report", "📤 Export Data", "💾 Database"
    ])

    # ---- Zone Report Tab ----
    with tab_zone:
        st.markdown("### Individual Zone Report")

        zone_ids = df["zone_id"].tolist() if "zone_id" in df.columns else []
        if not zone_ids:
            st.info("No zones available.")
            return

        selected_zone = st.selectbox("Select Zone", zone_ids, key="report_zone")

        if selected_zone:
            zone_row = df[df["zone_id"] == selected_zone].iloc[0]

            # Get simulation result if available
            sim_result = st.session_state.get("last_simulation")
            if sim_result and sim_result.get("zone_id") != selected_zone:
                sim_result = None

            report = generate_zone_report(zone_row, sim_result)

            # Display report
            st.markdown(f"## 🌍 Zone Report: {report['zone_id']}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📍 Location")
                st.markdown(f"- **Latitude:** {report['latitude']:.4f}")
                st.markdown(f"- **Longitude:** {report['longitude']:.4f}")
                st.markdown(f"- **Elevation:** {report.get('elevation', 'N/A')}")

                st.markdown("### 🎯 Priority Assessment")
                st.markdown(f"- **Priority Score:** {report['priority_score']:.1f} / 100")
                st.markdown(f"- **Priority Class:** {report['priority_class']}")

            with col2:
                st.markdown("### 🌡️ Environmental Indicators")
                st.markdown("*(0–100, High = Bad)*")
                for name, val in report.get("environmental_indicators", {}).items():
                    if val is not None:
                        st.markdown(f"- **{name}:** {val:.1f}")

            st.markdown("### 🌱 Recommended Interventions")
            for label, key in [("Primary", "primary_intervention"),
                               ("Secondary", "secondary_intervention"),
                               ("Supporting", "supporting_intervention")]:
                inter = report.get(key)
                if inter:
                    st.markdown(
                        f"- **{label}:** {inter['intervention']} "
                        f"(Suitability: {inter['score']:.0f}/100)"
                    )

            # Export buttons
            st.markdown("---")
            col_csv, col_pdf = st.columns(2)

            with col_csv:
                if st.button("📤 Export Zone Report (CSV)", key="export_zone_csv"):
                    path = export_zone_report_csv(zone_row)
                    st.success(f"✅ CSV saved: `{path}`")

            with col_pdf:
                if st.button("📤 Export Zone Report (PDF)", key="export_zone_pdf"):
                    try:
                        path = generate_pdf_report(report)
                        if path:
                            st.success(f"✅ PDF saved: `{path}`")
                        else:
                            st.warning("PDF generation not available (fpdf2 not installed).")
                    except Exception as e:
                        st.error(f"PDF generation error: {e}")

    # ---- Export Data Tab ----
    with tab_export:
        st.markdown("### Export Full Analysis")
        st.markdown(f"Export all {len(df)} zones with indicators, priority scores, and interventions.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📤 Export Full Analysis (CSV)", type="primary"):
                path = export_full_analysis(df)
                st.success(f"✅ Full analysis exported: `{path}`")

        with col2:
            # Download as CSV directly
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download as CSV",
                data=csv_data,
                file_name="ecorestore_analysis.csv",
                mime="text/csv",
            )

        # Preview
        with st.expander("👀 Data Preview"):
            st.dataframe(df.head(20), use_container_width=True)

        st.markdown("### Export Summary Statistics")
        if st.button("📤 Export Summary Statistics"):
            summary_df = df.describe().round(2)
            path = export_full_analysis(summary_df.reset_index(), "summary_statistics.csv")
            st.success(f"✅ Summary statistics exported: `{path}`")

    # ---- Database Tab ----
    with tab_db:
        st.markdown("### SQLite Database Management")
        st.markdown("Save processed data to the SQLite database for persistence across sessions.")

        if st.button("💾 Save to Database", type="primary"):
            with st.spinner("Saving to database..."):
                try:
                    init_database()
                    n_zones = save_zones(df)
                    n_env = save_environmental_data(df)
                    st.success(f"✅ Saved {n_zones} zones and {n_env} environmental records to database.")
                except Exception as e:
                    st.error(f"Database error: {e}")

        st.markdown("### Database Info")
        try:
            from config.config import DATABASE_PATH
            if DATABASE_PATH.exists():
                size_mb = DATABASE_PATH.stat().st_size / (1024 * 1024)
                st.markdown(f"- **Database path:** `{DATABASE_PATH}`")
                st.markdown(f"- **Database size:** {size_mb:.2f} MB")
            else:
                st.info("Database not yet created. Click 'Save to Database' to create it.")
        except Exception:
            st.info("Database status unknown.")

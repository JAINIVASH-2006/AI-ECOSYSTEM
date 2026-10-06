"""
EcoRestore AI — What-If Simulation Page
==========================================
Modify environmental parameters and see before/after comparison.
Save and compare multiple scenarios.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from config.thresholds import SIMULATION_PARAMS, PRIORITY_COLORS
from src.simulation import simulate_zone, ScenarioManager


def _get_scenario_manager() -> ScenarioManager:
    """Get or create session-level scenario manager."""
    if "scenario_manager" not in st.session_state:
        st.session_state.scenario_manager = ScenarioManager()
    return st.session_state.scenario_manager


def render():
    """Render the What-If Simulation page."""
    st.markdown("# 🔬 What-If Simulation")
    st.markdown(
        "Modify environmental conditions and see how restoration priority "
        "and intervention recommendations change."
    )

    if "processed_data" not in st.session_state or st.session_state.processed_data is None:
        st.warning("⚠️ No data loaded. Go to **📤 Data Upload** first.")
        return

    df = st.session_state.processed_data

    tab_sim, tab_compare = st.tabs(["🔬 Run Simulation", "📊 Compare Scenarios"])

    # ---- Simulation Tab ----
    with tab_sim:
        zone_ids = df["zone_id"].tolist() if "zone_id" in df.columns else []
        if not zone_ids:
            st.info("No zones available.")
            return

        selected_zone = st.selectbox("Select Zone", zone_ids, key="sim_zone")
        zone_row = df[df["zone_id"] == selected_zone].iloc[0]

        st.markdown(
            f"**Current Priority:** {zone_row.get('priority_score', 0):.1f}/100 "
            f"— **{zone_row.get('priority_class', 'N/A')}**"
        )

        st.markdown("---")
        st.markdown('<p class="section-header">⚙️ Modify Environmental Parameters</p>', unsafe_allow_html=True)
        st.markdown("*Adjust sliders to simulate percentage changes in each parameter.*")

        modifications = {}
        cols = st.columns(3)

        param_list = list(SIMULATION_PARAMS.items())
        for i, (param, settings) in enumerate(param_list):
            with cols[i % 3]:
                label = param.replace("_", " ").title()
                current_val = zone_row.get(param, 50)
                pct = st.slider(
                    f"{label} ({current_val:.1f})",
                    min_value=settings["min"],
                    max_value=settings["max"],
                    value=0,
                    step=settings["step"],
                    format=f"%d%%" if settings["unit"] == "%" else f"%d{settings['unit']}",
                    key=f"sim_slider_{param}",
                )
                if pct != 0:
                    modifications[param] = pct

        st.markdown("---")

        # Show modifications summary
        if modifications:
            st.markdown("**Modifications:**")
            for param, pct in modifications.items():
                sign = "+" if pct > 0 else ""
                st.markdown(f"- {param.replace('_', ' ').title()}: {sign}{pct}%")
        else:
            st.info("Adjust sliders above to define your scenario.")

        # Run simulation
        col_run, col_save = st.columns(2)

        with col_run:
            if st.button("🚀 Run Simulation", type="primary", disabled=not modifications):
                with st.spinner("Simulating..."):
                    result = simulate_zone(zone_row, modifications)
                    st.session_state.last_simulation = result

        with col_save:
            scenario_name = st.text_input("Scenario name", value="", key="sim_name")

        # Display results
        if "last_simulation" in st.session_state and st.session_state.last_simulation:
            result = st.session_state.last_simulation
            _display_simulation_result(result)

            if scenario_name and st.button("💾 Save Scenario"):
                mgr = _get_scenario_manager()
                mgr.save_scenario(scenario_name, result)
                st.success(f"Scenario '{scenario_name}' saved!")

    # ---- Compare Tab ----
    with tab_compare:
        st.markdown("### 📊 Scenario Comparison")
        mgr = _get_scenario_manager()
        scenarios = mgr.list_scenarios()

        if not scenarios:
            st.info("No scenarios saved yet. Run simulations and save them to compare.")
            return

        st.markdown(f"**{len(scenarios)} scenarios saved**")

        comparison = mgr.compare_scenarios()
        st.dataframe(comparison, use_container_width=True, hide_index=True)

        # Comparison bar chart
        if len(comparison) > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Before",
                x=comparison["scenario"],
                y=comparison["score_before"],
                marker_color="#e74c3c",
            ))
            fig.add_trace(go.Bar(
                name="After",
                x=comparison["scenario"],
                y=comparison["score_after"],
                marker_color="#27ae60",
            ))
            fig.update_layout(
                barmode="group",
                title="Scenario Comparison: Priority Score Before vs After",
                yaxis_title="Priority Score",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Ranking
            st.markdown("### 🏆 Scenario Ranking (Best → Worst)")
            ranked = comparison.sort_values("score_after")
            for i, row in ranked.iterrows():
                change = row["change"]
                sign = "+" if change > 0 else ""
                emoji = "✅" if change < 0 else "⚠️"
                st.markdown(
                    f"{emoji} **{row['scenario']}**: {row['score_before']:.1f} → "
                    f"{row['score_after']:.1f} ({sign}{change:.1f})"
                )

        if st.button("🗑️ Clear All Scenarios"):
            mgr.clear()
            st.rerun()


def _display_simulation_result(result: dict):
    """Display before/after comparison for a simulation."""
    st.markdown("---")
    st.markdown('<p class="section-header">📊 Simulation Results</p>', unsafe_allow_html=True)

    before = result["before"]
    after = result["after"]
    changes = result["changes"]

    # Priority score comparison
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Before", f"{before['priority_score']:.1f}", delta=None)
        before_color = PRIORITY_COLORS.get(before["priority_class"], "#95a5a6")
        st.markdown(
            f'<span style="background:{before_color};color:#fff;padding:3px 10px;'
            f'border-radius:12px;font-weight:600;">{before["priority_class"]}</span>',
            unsafe_allow_html=True,
        )
    with col2:
        st.metric("After", f"{after['priority_score']:.1f}", delta=None)
        after_color = PRIORITY_COLORS.get(after["priority_class"], "#95a5a6")
        st.markdown(
            f'<span style="background:{after_color};color:#fff;padding:3px 10px;'
            f'border-radius:12px;font-weight:600;">{after["priority_class"]}</span>',
            unsafe_allow_html=True,
        )
    with col3:
        change = changes["priority_score"]
        delta_color = "green" if change < 0 else "red"
        st.metric(
            "Change",
            f"{change:+.1f}",
            delta=f"{change:+.1f} points",
            delta_color="inverse",
        )

    # Indicator comparison chart
    ind_names = list(before["indicators"].keys())
    before_vals = [before["indicators"][k] for k in ind_names]
    after_vals = [after["indicators"][k] for k in ind_names]
    display_names = [n.replace("_", " ").title() for n in ind_names]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Before",
        x=display_names,
        y=before_vals,
        marker_color="#e74c3c",
        opacity=0.8,
    ))
    fig.add_trace(go.Bar(
        name="After",
        x=display_names,
        y=after_vals,
        marker_color="#27ae60",
        opacity=0.8,
    ))
    fig.update_layout(
        barmode="group",
        title="Environmental Indicators: Before vs After",
        yaxis_title="Indicator Value (0-100, High = Bad)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed changes table
    with st.expander("📋 Detailed Changes"):
        change_data = []
        for ind in ind_names:
            b = before["indicators"][ind]
            a = after["indicators"][ind]
            c = a - b
            change_data.append({
                "Indicator": ind.replace("_", " ").title(),
                "Before": round(b, 1),
                "After": round(a, 1),
                "Change": round(c, 1),
            })
        st.dataframe(pd.DataFrame(change_data), use_container_width=True, hide_index=True)

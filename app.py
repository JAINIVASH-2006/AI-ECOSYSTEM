"""
EcoRestore AI — Main Streamlit Application
=============================================
Entry point: ``streamlit run app.py``

Provides sidebar navigation across all dashboard pages.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import APP_DESCRIPTION, APP_DISCLAIMER, APP_NAME, APP_VERSION

# Page imports (lazy to avoid import errors before deps install)
from ui.dashboard import render as render_dashboard
from ui.data_upload import render as render_data_upload
from ui.environmental_analysis import render as render_env_analysis
from ui.priority_map import render as render_priority_map
from ui.ai_prediction import render as render_ai_prediction
from ui.intervention_planner import render as render_intervention_planner
from ui.simulation import render as render_simulation
from ui.reports import render as render_reports

# ------------------------------------------------------------------ #
# Page Configuration
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ #
# Custom CSS
# ------------------------------------------------------------------ #
def load_css():
    css_path = PROJECT_ROOT / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ------------------------------------------------------------------ #
# Sidebar Navigation
# ------------------------------------------------------------------ #

PAGES = {
    "🏠 Dashboard": render_dashboard,
    "📤 Data Upload": render_data_upload,
    "📊 Environmental Analysis": render_env_analysis,
    "🗺️ Restoration Priority Map": render_priority_map,
    "🤖 AI Prediction": render_ai_prediction,
    "🌱 Intervention Planner": render_intervention_planner,
    "🔬 What-If Simulation": render_simulation,
    "📋 Reports & Model Performance": render_reports,
}

with st.sidebar:
    st.markdown(f"# 🌍 {APP_NAME}")
    st.markdown(f"*v{APP_VERSION}*")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"<small style='color:#7f8c8d;'>{APP_DISCLAIMER}</small>",
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ #
# Render Selected Page
# ------------------------------------------------------------------ #
try:
    PAGES[page]()
except Exception as e:
    st.error(f"An error occurred while rendering this page: {e}")
    st.info("Please check that all data is loaded correctly and try again.")

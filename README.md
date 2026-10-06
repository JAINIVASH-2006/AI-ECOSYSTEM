# EcoRestore v2 — web workspace

The upgraded browser app is in `frontend/`. Start with [DEPLOYMENT.md](DEPLOYMENT.md), [project review](docs/PROJECT-REVIEW.md) and [verification record](docs/VERIFICATION.md).

Features: public synthetic-data exploration, explainable priorities, Supabase account integration, protected scenario/plans pages, budget shortlisting and private field-review notes. Live Supabase provisioning and GitHub hosting are pending; see the deployment guide.

Editable UI design: https://www.figma.com/design/8eYuA3PG4OVCd2p6x6DXrH

The existing Python/Streamlit research implementation is preserved below. Its capabilities and setup are separate from the new static browser app.

---

# 🌍 EcoRestore AI

## AI-Based Ecological Restoration Priority Mapping and Intervention Planning System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Problem Statement

Ecological degradation — including deforestation, soil erosion, water scarcity, habitat loss, and biodiversity decline — threatens ecosystems worldwide. Environmental planners need data-driven tools to:

1. **Identify** areas requiring urgent ecological restoration
2. **Prioritise** zones based on multiple environmental factors
3. **Recommend** suitable restoration interventions
4. **Simulate** the impact of proposed interventions before implementation

EcoRestore AI addresses these needs by providing an integrated decision-support system that combines environmental data analysis, machine learning, GIS mapping, and what-if simulation.

---

## 🎯 Objectives

- Calculate a transparent **Restoration Priority Score (0–100)** for geographic zones
- Classify zones into **Critical / High / Moderate / Low** priority categories
- Recommend suitable **ecological restoration interventions** with suitability scores
- Visualise results on an **interactive GIS map** with clickable zone details
- Explain **why** an area received its priority score
- Provide **what-if simulation** to model restoration scenarios
- Compare **ML model performance** (Random Forest, XGBoost, baselines)
- Export analysis results as **CSV and PDF reports**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 Dashboard | KPI cards, priority distribution, environmental overview |
| 📤 Data Upload | CSV/GeoJSON upload with validation |
| 📈 Environmental Analysis | Histograms, box plots, correlation matrix, radar charts |
| 🗺️ Priority Map | Interactive Folium map with 7 layers and zone popups |
| 🤖 AI Prediction | Train & compare Random Forest, XGBoost, Logistic/Linear Regression |
| 🌱 Intervention Planner | 9 intervention types with suitability scores and reasons |
| 🔬 What-If Simulation | Modify parameters and see before/after priority changes |
| 📋 Reports | Zone reports, CSV/PDF export, database persistence |

---

## 🏗️ Architecture

```
eco_restore_ai/
├── app.py                          # Streamlit entry point
├── config/
│   ├── config.py                   # Paths, DB, map, model settings
│   └── thresholds.py               # Scoring weights, thresholds, intervention rules
├── data/
│   ├── raw/                        # User-uploaded data
│   ├── processed/                  # Processed outputs
│   └── sample/                     # Generated sample dataset
├── models/                         # Saved ML models (.joblib)
├── src/
│   ├── data_loader.py              # Data loading, validation, sample generation
│   ├── preprocessing.py            # Missing values, outliers, normalization
│   ├── feature_engineering.py      # 7 environmental indicators
│   ├── priority_engine.py          # Weighted priority scoring & classification
│   ├── model_training.py           # RF, XGBoost, baseline model training
│   ├── prediction.py               # Load models, predict new data
│   ├── explainability.py           # Feature importance, SHAP, zone explanations
│   ├── intervention_engine.py      # Rule-based intervention recommendations
│   ├── simulation.py               # What-if scenario engine
│   ├── gis.py                      # Folium map generation
│   ├── database.py                 # SQLite persistence
│   └── reporting.py                # CSV/PDF report generation
├── ui/
│   ├── dashboard.py                # Main dashboard page
│   ├── data_upload.py              # Data upload page
│   ├── environmental_analysis.py   # Environmental analysis page
│   ├── priority_map.py             # Interactive GIS map page
│   ├── ai_prediction.py            # ML prediction & model comparison
│   ├── intervention_planner.py     # Intervention recommendation page
│   ├── simulation.py               # What-if simulation page
│   └── reports.py                  # Reports & export page
├── tests/
│   └── test_core.py                # Unit tests
├── outputs/
│   ├── maps/                       # Saved HTML maps
│   ├── reports/                    # Generated reports
│   └── predictions/                # Prediction outputs
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Web Framework | Streamlit |
| ML Classification | Random Forest, XGBoost, Logistic Regression |
| ML Regression | Random Forest, XGBoost, Linear Regression |
| Data Processing | Pandas, NumPy |
| GIS/Mapping | GeoPandas, Folium, Shapely, streamlit-folium |
| Visualisation | Plotly, Matplotlib |
| Database | SQLite |
| Model Persistence | Joblib |
| PDF Generation | fpdf2 |
| Explainability | Feature importance (built-in), SHAP (optional) |

---

## 📊 Dataset Description

### Required Columns

| Column | Description | Range |
|--------|-------------|-------|
| zone_id | Unique zone identifier | String |
| latitude | Geographic latitude | -90 to 90 |
| longitude | Geographic longitude | -180 to 180 |
| vegetation_index | Vegetation health (high = good) | 0–100 |
| soil_degradation | Soil degradation level (high = bad) | 0–100 |
| rainfall | Rainfall adequacy (high = good) | 0–100 |
| water_availability | Water resource availability (high = good) | 0–100 |
| land_use_change | Extent of land use change (high = more change) | 0–100 |
| habitat_quality | Habitat condition (high = good) | 0–100 |
| biodiversity_index | Biodiversity level (high = good) | 0–100 |
| human_pressure | Anthropogenic pressure (high = bad) | 0–100 |
| elevation | Elevation in metres | 0–5000 |
| slope | Slope in degrees | 0–60 |
| forest_cover | Forest cover percentage (high = good) | 0–100 |
| drought_index | Drought severity (high = bad) | 0–100 |

### Synthetic Sample Data

The application generates **1,000 synthetic zones** with meaningful correlations for demonstration. **This data is clearly labelled as SYNTHETIC_DEMO and must not be treated as real environmental observations.**

---

## 🧪 ML Methodology

### Target Variable
The baseline weighted priority score (from `priority_engine.py`) serves as the reference target. ML models learn to approximate this formula-based score — **they do not independently discover restoration priorities**.

### Models
- **Random Forest**: Ensemble of decision trees with bagging
- **XGBoost**: Gradient-boosted trees with regularisation
- **Baseline**: Logistic Regression (classification) / Linear Regression (regression)

### Evaluation
- **Classification**: Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC, 5-fold CV
- **Regression**: MAE, RMSE, R², Actual vs Predicted, Residual Analysis, 5-fold CV

---

## 🎯 Priority Scoring Methodology

### Weighted Formula
```
Priority Score = 0.25 × Soil Degradation Risk
               + 0.20 × Vegetation Stress
               + 0.15 × Water Stress
               + 0.15 × Habitat Degradation
               + 0.15 × Biodiversity Risk
               + 0.10 × Human Pressure Index
```

### Classification
| Score | Category |
|-------|----------|
| 0–25 | LOW |
| 26–50 | MODERATE |
| 51–75 | HIGH |
| 76–100 | CRITICAL |

All weights and thresholds are configurable in `config/thresholds.py`.

---

## 🌱 Intervention Engine

9 rule-based interventions with suitability scores (0–100):

1. **Afforestation** — High vegetation stress + low forest cover
2. **Reforestation** — Degraded forest + poor habitat
3. **Soil Conservation** — High soil degradation + steep slopes
4. **Agroforestry** — Agricultural land + low tree cover
5. **Rainwater Harvesting** — Low water availability + low rainfall
6. **Watershed Management** — Water stress + soil degradation
7. **Habitat Restoration** — Poor habitat quality + low biodiversity
8. **Native Vegetation Restoration** — High vegetation stress + poor habitat
9. **Erosion Control** — High soil degradation + steep slopes

Each recommendation includes human-readable reasons.

---

## 🗺️ GIS Implementation

- **Folium** maps with color-coded circle markers
- **7 toggleable layers**: Priority, Vegetation, Soil, Water, Habitat, Biodiversity, Human Pressure
- **Clickable popups** showing zone profile, indicators, and interventions
- Maps exportable as HTML files

---

## 🔬 What-If Simulation

Users can modify environmental parameters by ±50% and see:
- Recalculated indicators and priority score
- Before/after comparison charts
- Priority class changes
- Updated intervention recommendations
- Multiple saved scenarios with ranking

---

## 🚀 Installation

```bash
# Clone the repository
git clone <repository-url>
cd eco_restore_ai

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

---

## 💻 Usage

```bash
# Run the application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

### Quick Start
1. The app loads sample synthetic data automatically on first launch
2. Navigate through pages using the sidebar
3. Upload your own CSV data via the **📤 Data Upload** page
4. Train ML models via the **🤖 AI Prediction** page

### Running Tests
```bash
python -m pytest tests/ -v
```

---

## 📁 Project Structure

See the [Architecture](#-architecture) section above for the full directory layout.

### Key Design Principles
- **Separation of concerns**: UI, ML, GIS, database, and business logic in separate modules
- **No hardcoded values**: All thresholds and weights in `config/thresholds.py`
- **No raw SQL in UI**: All database operations in `src/database.py`
- **Consistent directionality**: High indicator = Bad; High priority = Needs restoration
- **Error handling**: User-facing error messages, no raw stack traces

---

## 📈 Model Evaluation

Models are evaluated on a held-out test set (20%) with 5-fold cross-validation on the training set. The application automatically identifies the best-performing model by accuracy (classification) or R² (regression).

All metrics are displayed interactively in the **🤖 AI Prediction** page.

---

## ⚠️ Limitations

1. **Synthetic data only** — no real environmental datasets are bundled
2. **Simplified ecological relationships** — real ecosystems have far more complex interactions
3. **Formula-based priority** — ML models approximate the weighted baseline, not ground truth
4. **Static analysis** — no temporal/seasonal dynamics modelled
5. **No field validation** — results have not been validated against field surveys
6. **Rule-based interventions** — simplified suitability rules, not ecosystem-specific models

---

## 🔮 Future Enhancements

- Integration with real environmental datasets (e.g., MODIS, Sentinel, CHIRPS)
- Temporal analysis and trend detection
- Deep learning models for satellite image analysis
- Multi-objective optimisation for intervention planning
- Cost-benefit analysis module
- REST API for external system integration
- User authentication and role management
- Regional ecological zone-specific intervention models

---

## 📜 Disclaimer

This system provides **estimated priority assessments** and **recommended interventions** for **decision-support purposes only**. It does **not** replace professional ecological expertise or field surveys. All synthetic/demo data is clearly labelled and must not be treated as real environmental observations.

---

## 📝 License

MIT License — See LICENSE file for details.

---

*Built with ❤️ for ecological restoration using Python, Streamlit, and Machine Learning*

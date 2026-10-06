"""
EcoRestore AI — AI Prediction Page
=====================================
Train ML models, view predictions, feature importance, and model comparison.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from config.thresholds import PRIORITY_CLASSES
from src.model_training import train_all_models, get_best_model, FEATURE_COLUMNS
from src.prediction import predict_classification, predict_regression, get_available_models
from src.explainability import get_feature_importance, explain_zone, get_shap_explanation


def render():
    """Render the AI Prediction page."""
    st.markdown("# 🤖 AI Prediction & Model Performance")
    st.markdown(
        "Train machine learning models and analyze predictions. "
        "*Note: models learn to approximate the baseline weighted priority score — "
        "they do not independently discover restoration priorities.*"
    )

    if "processed_data" not in st.session_state or st.session_state.processed_data is None:
        st.warning("⚠️ No data loaded. Go to **📤 Data Upload** first.")
        return

    df = st.session_state.processed_data

    tab_train, tab_predict, tab_compare = st.tabs([
        "🎯 Train Models", "🔮 Predictions", "📊 Model Comparison"
    ])

    # ---- Train Tab ----
    with tab_train:
        st.markdown("### Train Classification & Regression Models")
        st.markdown(
            "This will train **Random Forest**, **XGBoost**, and baseline models "
            "on the current dataset using an 80/20 train/test split."
        )

        if st.button("🚀 Train All Models", type="primary"):
            with st.spinner("Training models... This may take a moment."):
                try:
                    results = train_all_models(df)
                    st.session_state.model_results = results
                    st.success("✅ All models trained successfully!")
                except Exception as e:
                    st.error(f"Training error: {e}")
                    return

        if "model_results" in st.session_state:
            results = st.session_state.model_results

            # Classification results
            st.markdown("### 📋 Classification Results")
            clf_results = results.get("classification", {})

            for name, info in clf_results.items():
                metrics = info["metrics"]
                with st.expander(f"**{name}** — Accuracy: {metrics['accuracy']:.4f}"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Accuracy", f"{metrics['accuracy']:.4f}")
                    col2.metric("Precision", f"{metrics['precision_weighted']:.4f}")
                    col3.metric("Recall", f"{metrics['recall_weighted']:.4f}")
                    col4.metric("F1-Score", f"{metrics['f1_weighted']:.4f}")

                    if metrics.get("roc_auc") is not None:
                        st.metric("ROC-AUC (weighted)", f"{metrics['roc_auc']:.4f}")
                    if metrics.get("cv_mean") is not None:
                        st.metric("CV Mean Accuracy", f"{metrics['cv_mean']:.4f} ± {metrics.get('cv_std', 0):.4f}")

                    # Confusion matrix
                    cm = metrics.get("confusion_matrix")
                    if cm:
                        # Use actual class labels from the fitted encoder
                        cm_labels = info.get("feature_names") and list(
                            info.get("label_encoder", {}).classes_
                            if hasattr(info.get("label_encoder", {}), "classes_")
                            else PRIORITY_CLASSES
                        )
                        # Derive from classification_report keys as fallback
                        cr = metrics.get("classification_report", {})
                        cm_labels = [
                            k for k in cr
                            if k not in ("accuracy", "macro avg", "weighted avg")
                        ] or PRIORITY_CLASSES
                        # Trim to match matrix size
                        n = len(cm)
                        cm_labels = cm_labels[:n]
                        fig_cm = px.imshow(
                            cm,
                            labels=dict(x="Predicted", y="Actual", color="Count"),
                            x=cm_labels, y=cm_labels,
                            text_auto=True,
                            color_continuous_scale="Blues",
                            title=f"{name} — Confusion Matrix",
                        )
                        fig_cm.update_layout(font=dict(family="Inter"), height=400)
                        st.plotly_chart(fig_cm, use_container_width=True)

                    # Feature importance
                    fi = metrics.get("feature_importance", {})
                    if fi:
                        fi_sorted = sorted(fi.items(), key=lambda x: x[1], reverse=True)
                        fig_fi = px.bar(
                            x=[v for _, v in fi_sorted],
                            y=[k.replace("_", " ").title() for k, _ in fi_sorted],
                            orientation="h",
                            title=f"{name} — Feature Importance",
                            labels={"x": "Importance", "y": "Feature"},
                            color_discrete_sequence=["#667eea"],
                        )
                        fig_fi.update_layout(
                            yaxis=dict(autorange="reversed"),
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter"),
                            height=400,
                        )
                        st.plotly_chart(fig_fi, use_container_width=True)

            # Regression results
            st.markdown("### 📈 Regression Results")
            reg_results = results.get("regression", {})

            for name, info in reg_results.items():
                metrics = info["metrics"]
                with st.expander(f"**{name}** — R²: {metrics['r2']:.4f}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("MAE", f"{metrics['mae']:.4f}")
                    col2.metric("RMSE", f"{metrics['rmse']:.4f}")
                    col3.metric("R²", f"{metrics['r2']:.4f}")

                    if metrics.get("cv_mean_r2") is not None:
                        st.metric("CV Mean R²", f"{metrics['cv_mean_r2']:.4f} ± {metrics.get('cv_std_r2', 0):.4f}")

                    # Actual vs Predicted
                    y_test = info.get("y_test")
                    y_pred = info.get("y_pred")
                    if y_test is not None and y_pred is not None:
                        fig_ap = go.Figure()
                        fig_ap.add_trace(go.Scatter(
                            x=y_test, y=y_pred,
                            mode="markers",
                            marker=dict(color="#667eea", opacity=0.6, size=5),
                            name="Predictions",
                        ))
                        # Perfect prediction line
                        min_val = min(min(y_test), min(y_pred))
                        max_val = max(max(y_test), max(y_pred))
                        fig_ap.add_trace(go.Scatter(
                            x=[min_val, max_val], y=[min_val, max_val],
                            mode="lines", line=dict(color="red", dash="dash"),
                            name="Perfect Prediction",
                        ))
                        fig_ap.update_layout(
                            title=f"{name} — Actual vs Predicted",
                            xaxis_title="Actual", yaxis_title="Predicted",
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter"),
                            height=400,
                        )
                        st.plotly_chart(fig_ap, use_container_width=True)

                        # Residual plot
                        residuals = y_test - y_pred
                        fig_res = px.scatter(
                            x=y_pred, y=residuals,
                            labels={"x": "Predicted", "y": "Residual"},
                            title=f"{name} — Residual Analysis",
                            color_discrete_sequence=["#e74c3c"],
                        )
                        fig_res.add_hline(y=0, line_dash="dash", line_color="gray")
                        fig_res.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter"),
                            height=350,
                        )
                        st.plotly_chart(fig_res, use_container_width=True)

    # ---- Predict Tab ----
    with tab_predict:
        st.markdown("### Predict Priority for Individual Zones")

        available = get_available_models()
        clf_models = available.get("classification", [])

        if not clf_models:
            st.info("No trained models found. Train models first in the **🎯 Train Models** tab.")
            return

        model_choice = st.selectbox("Select Model", clf_models, key="predict_model")

        zone_ids = df["zone_id"].tolist() if "zone_id" in df.columns else []
        selected_zone = st.selectbox("Select Zone", zone_ids, key="predict_zone")

        if selected_zone and st.button("🔮 Predict", type="primary"):
            zone_df = df[df["zone_id"] == selected_zone].copy()
            try:
                result = predict_classification(zone_df, model_choice)
                row = result.iloc[0]

                col1, col2, col3 = st.columns(3)
                col1.metric("Predicted Class", row.get("predicted_class", "N/A"))
                col2.metric("Confidence", f"{row.get('prediction_confidence', 0):.1%}")
                col3.metric("Baseline Score", f"{row.get('priority_score', 0):.1f}")

                # Zone explanation
                explanation = explain_zone(zone_df.iloc[0])
                st.markdown("#### Top Contributing Factors")
                for factor in explanation["factors"][:5]:
                    st.markdown(
                        f"- **{factor['name']}**: {factor['value']:.1f} "
                        f"({factor['contribution']} contribution)"
                    )
            except Exception as e:
                st.error(f"Prediction error: {e}")

    # ---- Compare Tab ----
    with tab_compare:
        st.markdown("### Model Comparison")

        if "model_results" not in st.session_state:
            st.info("Train models first to see comparison.")
            return

        results = st.session_state.model_results

        # Classification comparison table
        st.markdown("#### Classification Models")
        clf_data = []
        for name, info in results.get("classification", {}).items():
            m = info["metrics"]
            clf_data.append({
                "Model": name,
                "Accuracy": m["accuracy"],
                "Precision": m["precision_weighted"],
                "Recall": m["recall_weighted"],
                "F1-Score": m["f1_weighted"],
                "ROC-AUC": m.get("roc_auc", "N/A"),
                "CV Mean": m.get("cv_mean", "N/A"),
            })
        if clf_data:
            clf_df = pd.DataFrame(clf_data)
            st.dataframe(clf_df, use_container_width=True, hide_index=True)

            best_clf = get_best_model(results["classification"], "accuracy")
            st.success(f"🏆 Best Classification Model: **{best_clf}**")

        # Regression comparison table
        st.markdown("#### Regression Models")
        reg_data = []
        for name, info in results.get("regression", {}).items():
            m = info["metrics"]
            reg_data.append({
                "Model": name,
                "MAE": m["mae"],
                "RMSE": m["rmse"],
                "R²": m["r2"],
                "CV Mean R²": m.get("cv_mean_r2", "N/A"),
            })
        if reg_data:
            reg_df = pd.DataFrame(reg_data)
            st.dataframe(reg_df, use_container_width=True, hide_index=True)

            best_reg = get_best_model(results["regression"], "r2")
            st.success(f"🏆 Best Regression Model: **{best_reg}**")

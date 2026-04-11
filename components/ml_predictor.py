from __future__ import annotations

from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _predict_risk(open_violations: int, incident_history: int) -> tuple[str, str]:
    if open_violations > 5 or incident_history > 3:
        return "CRITICAL", "#ff4b4b"
    if open_violations > 2:
        return "HIGH", "#ff8c42"
    return "LOW", "#2ecc71"


def _confusion_matrix_from_table(ml_df: pd.DataFrame) -> tuple[list[list[int]], list[str], list[str]] | None:
    lowered = {column.lower(): column for column in ml_df.columns}

    if {"actual_label", "predicted_label"}.issubset(lowered):
        actual_col = lowered["actual_label"]
        predicted_col = lowered["predicted_label"]
        pivot = pd.crosstab(ml_df[actual_col], ml_df[predicted_col], dropna=False)
        actual_labels = [str(label) for label in pivot.index.tolist()]
        predicted_labels = [str(label) for label in pivot.columns.tolist()]
        matrix = pivot.values.tolist()
        return matrix, predicted_labels, actual_labels

    if {"tn", "fp", "fn", "tp"}.issubset(lowered):
        row = ml_df.iloc[0]
        matrix = [
            [int(row[lowered["tn"]]), int(row[lowered["fp"]])],
            [int(row[lowered["fn"]]), int(row[lowered["tp"]])],
        ]
        return matrix, ["Predicted Negative", "Predicted Positive"], ["Actual Negative", "Actual Positive"]

    return None


def _render_prediction_badge(label: str, color: str) -> None:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}33, rgba(255,255,255,0.03));
            border: 1px solid {color};
            border-radius: 16px;
            padding: 1rem 1.2rem;
            margin-top: 0.75rem;
            margin-bottom: 0.75rem;
        ">
            <div style="font-size: 0.85rem; color: #cfcfcf; letter-spacing: 0.08em;">RULE-BASED PREDICTION</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: white;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ml_predictor(
    ml_df: pd.DataFrame,
    start_card: Callable[[str, str | None], None],
    end_card: Callable[[], None],
) -> None:
    start_card("ML Predictor", "Rule-based local risk estimator plus model-monitoring outputs from Databricks.")

    left, right = st.columns([1.0, 1.15], gap="large")

    with left:
        st.markdown("#### Property Risk Simulator")
        open_violations = st.slider("Open Violations", min_value=0, max_value=10, value=2)
        incident_history = st.slider("Incident History", min_value=0, max_value=10, value=1)
        response_time = st.slider("Average Response Time (mins)", min_value=0, max_value=30, value=7)
        inspection_failures = st.slider("Inspection Failures", min_value=0, max_value=10, value=1)
        permit_issues = st.slider("Permit Issues", min_value=0, max_value=10, value=0)

        label, color = _predict_risk(open_violations=open_violations, incident_history=incident_history)
        _render_prediction_badge(label=label, color=color)

        st.caption(
            "Rule logic: CRITICAL if open violations > 5 or incident history > 3; "
            "HIGH if open violations > 2; otherwise LOW."
        )

        st.markdown(
            f"""
            **Signals captured:** open violations `{open_violations}`, incidents `{incident_history}`,
            response time `{response_time}`, inspection failures `{inspection_failures}`, permit issues `{permit_issues}`.
            """
        )

    with right:
        st.markdown("#### Confusion Matrix")
        confusion = _confusion_matrix_from_table(ml_df) if not ml_df.empty else None
        if confusion is None:
            st.info("Confusion matrix fields were not found in `sf_fire_gold.ml_risk_predictions`.")
        else:
            matrix, x_labels, y_labels = confusion
            figure = go.Figure(
                data=go.Heatmap(
                    z=matrix,
                    x=x_labels,
                    y=y_labels,
                    colorscale=[[0.0, "#1a1a1a"], [0.5, "#8b0000"], [1.0, "#ff4b4b"]],
                    text=matrix,
                    texttemplate="%{text}",
                    hoverongaps=False,
                )
            )
            figure.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(figure, use_container_width=True)

    if not ml_df.empty:
        st.markdown("#### ML Predictions Snapshot")
        st.dataframe(ml_df.head(100), use_container_width=True, hide_index=True)

    end_card()

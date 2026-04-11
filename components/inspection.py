from __future__ import annotations

from typing import Callable

import pandas as pd
import plotly.express as px
import streamlit as st


def render_inspection(
    inspection_df: pd.DataFrame,
    start_card: Callable[[str, str | None], None],
    end_card: Callable[[], None],
) -> None:
    start_card("Inspection Effectiveness", "Track inspection quality, reinspection pressure, and follow-through.")
    if inspection_df.empty:
        st.info("Inspection effectiveness data is unavailable.")
        end_card()
        return

    score_col = next((col for col in ["effectiveness_score", "inspection_effectiveness_score"] if col in inspection_df.columns), None)
    reinspection_col = next((col for col in ["reinspection_needed", "needs_reinspection"] if col in inspection_df.columns), None)
    group_col = next((col for col in ["district", "inspection_type", "inspector_id"] if col in inspection_df.columns), None)

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        if score_col and group_col:
            chart = px.bar(
                inspection_df.sort_values(score_col, ascending=False),
                x=group_col,
                y=score_col,
                color=score_col,
                template="plotly_dark",
                color_continuous_scale=["#1f1f1f", "#8b0000", "#ff4b4b"],
                title="Inspection Effectiveness Score",
            )
            chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Effectiveness score fields are not available.")

    with chart_right:
        if reinspection_col:
            donut_df = (
                inspection_df[reinspection_col]
                .fillna("UNKNOWN")
                .astype(str)
                .value_counts()
                .rename_axis("reinspection_needed")
                .reset_index(name="count")
            )
            donut = px.pie(
                donut_df,
                names="reinspection_needed",
                values="count",
                hole=0.62,
                template="plotly_dark",
                color_discrete_sequence=["#ff4b4b", "#ff8c42", "#6c757d"],
                title="Reinspection Needed",
            )
            donut.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(donut, use_container_width=True)
        else:
            st.info("Reinspection data is not available.")

    st.dataframe(inspection_df, use_container_width=True, hide_index=True)
    end_card()

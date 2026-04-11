from __future__ import annotations

from typing import Callable

import pandas as pd
import plotly.express as px
import streamlit as st


def render_district(
    district_df: pd.DataFrame,
    start_card: Callable[[str, str | None], None],
    end_card: Callable[[], None],
) -> None:
    start_card("District Risk Summary", "District-level risk performance from Gold aggregates.")
    if district_df.empty:
        st.info("District summary data is unavailable.")
        end_card()
        return

    score_col = "avg_risk_score" if "avg_risk_score" in district_df.columns else "risk_score" if "risk_score" in district_df.columns else None
    district_col = "district" if "district" in district_df.columns else district_df.columns[0]

    if score_col:
        chart = px.bar(
            district_df.sort_values(score_col, ascending=False),
            x=district_col,
            y=score_col,
            color=score_col,
            template="plotly_dark",
            color_continuous_scale=["#2d0000", "#8b0000", "#ff4b4b"],
            title="Average Risk Score by District",
        )
        chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No average risk score column was found in the district summary table.")

    st.dataframe(district_df, use_container_width=True, hide_index=True)
    end_card()

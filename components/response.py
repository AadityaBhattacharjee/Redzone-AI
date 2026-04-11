from __future__ import annotations

from typing import Callable

import pandas as pd
import plotly.express as px
import streamlit as st


def render_response(
    response_df: pd.DataFrame,
    start_card: Callable[[str, str | None], None],
    end_card: Callable[[], None],
) -> None:
    start_card("Response Optimization", "Operational response delays, bottlenecks, and supporting detail.")
    if response_df.empty:
        st.info("Response optimization data is unavailable.")
        end_card()
        return

    chart_left, chart_right = st.columns(2, gap="large")

    delay_col = next((col for col in ["avg_response_delay_mins", "response_delay_mins", "avg_response_time_minutes"] if col in response_df.columns), None)
    group_col = next((col for col in ["district", "station_area", "neighborhood"] if col in response_df.columns), None)
    bottleneck_col = next((col for col in ["bottleneck_reason", "delay_reason", "constraint_reason"] if col in response_df.columns), None)

    with chart_left:
        if delay_col and group_col:
            delay_chart = px.bar(
                response_df.sort_values(delay_col, ascending=False),
                x=group_col,
                y=delay_col,
                template="plotly_dark",
                color=delay_col,
                color_continuous_scale=["#2d0000", "#8b0000", "#ff4b4b"],
                title="Average Response Delay",
            )
            delay_chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(delay_chart, use_container_width=True)
        else:
            st.info("Average response delay fields are not available.")

    with chart_right:
        if bottleneck_col:
            bottleneck_counts = (
                response_df[bottleneck_col]
                .fillna("UNKNOWN")
                .astype(str)
                .value_counts()
                .rename_axis("bottleneck_reason")
                .reset_index(name="count")
            )
            bottleneck_chart = px.bar(
                bottleneck_counts,
                x="bottleneck_reason",
                y="count",
                template="plotly_dark",
                color="count",
                color_continuous_scale=["#330000", "#8b0000", "#ff4b4b"],
                title="Bottleneck Reasons",
            )
            bottleneck_chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(bottleneck_chart, use_container_width=True)
        else:
            st.info("Bottleneck reason data is not available.")

    st.dataframe(response_df, use_container_width=True, hide_index=True)
    end_card()

from __future__ import annotations

from typing import Callable

import pandas as pd
import plotly.express as px
import streamlit as st


def render_compliance(
    compliance_df: pd.DataFrame,
    property_df: pd.DataFrame,
    start_card: Callable[[str, str | None], None],
    end_card: Callable[[], None],
) -> None:
    start_card("Compliance Overview", "Monitor compliance bands and surface non-compliant properties.")

    if compliance_df.empty and property_df.empty:
        st.info("Compliance data is unavailable.")
        end_card()
        return

    source_df = compliance_df if not compliance_df.empty else property_df
    compliance_col = next(
        (col for col in ["compliance_band", "compliance_status", "status"] if col in source_df.columns),
        None,
    )

    chart_col, table_col = st.columns([1, 1.2], gap="large")

    with chart_col:
        if compliance_col:
            counts = (
                source_df[compliance_col]
                .fillna("UNKNOWN")
                .astype(str)
                .value_counts()
                .rename_axis(compliance_col)
                .reset_index(name="count")
            )
            chart = px.pie(
                counts,
                names=compliance_col,
                values="count",
                hole=0.62,
                template="plotly_dark",
                color_discrete_sequence=["#ff4b4b", "#ff8c42", "#6c757d", "#f5f5f5"],
                title="Compliance Band Split",
            )
            chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No compliance band column found in the selected Gold table.")

    with table_col:
        st.markdown("#### Non-Compliant Properties")
        if compliance_col:
            non_compliant = source_df[
                source_df[compliance_col].astype(str).str.upper().isin(["NON COMPLIANT", "NON_COMPLIANT", "CRITICAL"])
            ]
        else:
            non_compliant = source_df.iloc[0:0]

        if non_compliant.empty:
            st.success("No non-compliant properties matched the current filters.")
        else:
            display_cols = [
                col
                for col in ["address", "district", "compliance_band", "risk_score", "recommended_intervention_tier"]
                if col in non_compliant.columns
            ]
            st.dataframe(non_compliant[display_cols].head(50), use_container_width=True, hide_index=True)

    end_card()

from __future__ import annotations

import hashlib
from typing import Callable

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st


def _series(dataframe: pd.DataFrame, column: str) -> pd.Series:
    return dataframe[column] if column in dataframe.columns else pd.Series(dtype="object")


def _risk_counts(dataframe: pd.DataFrame) -> tuple[int, int]:
    risk_series = _series(dataframe, "risk_category").astype(str).str.upper()
    high_risk = int(risk_series.isin(["HIGH", "CRITICAL"]).sum()) if not risk_series.empty else 0
    critical_risk = int((risk_series == "CRITICAL").sum()) if not risk_series.empty else 0
    return high_risk, critical_risk


def _build_distribution_chart(dataframe: pd.DataFrame):
    if "risk_category" not in dataframe.columns or dataframe.empty:
        return None
    counts = (
        dataframe["risk_category"]
        .fillna("UNKNOWN")
        .astype(str)
        .str.upper()
        .value_counts()
        .rename_axis("risk_category")
        .reset_index(name="property_count")
    )
    return px.bar(
        counts,
        x="risk_category",
        y="property_count",
        color="risk_category",
        template="plotly_dark",
        color_discrete_sequence=["#ff4b4b", "#ff7b7b", "#ffa5a5", "#6c757d"],
        title="Risk Distribution",
    ).update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )


def _get_coordinate_seed(row: pd.Series) -> str:
    for field in ("address", "district", "property_id"):
        if field in row and pd.notna(row[field]):
            return str(row[field])
    return str(row.name)


def _deterministic_offset(seed: str, scale: float) -> float:
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return (value - 0.5) * scale


def _prepare_map_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    map_df = dataframe.copy()
    latitude_col = next((col for col in ["latitude", "lat"] if col in map_df.columns), None)
    longitude_col = next((col for col in ["longitude", "lon", "lng"] if col in map_df.columns), None)

    if latitude_col and longitude_col:
        map_df["latitude"] = pd.to_numeric(map_df[latitude_col], errors="coerce")
        map_df["longitude"] = pd.to_numeric(map_df[longitude_col], errors="coerce")
    else:
        map_df["latitude"] = [
            37.7749 + _deterministic_offset(_get_coordinate_seed(row), 0.08) for _, row in map_df.iterrows()
        ]
        map_df["longitude"] = [
            -122.4194 + _deterministic_offset(f"{_get_coordinate_seed(row)}_lon", 0.08)
            for _, row in map_df.iterrows()
        ]

    map_df["risk_score"] = pd.to_numeric(map_df.get("risk_score"), errors="coerce").fillna(0)
    map_df["point_radius"] = map_df["risk_score"].clip(lower=10).fillna(10) * 8
    map_df["risk_label"] = map_df.get("risk_category", "UNKNOWN")
    return map_df


def _render_map(dataframe: pd.DataFrame) -> None:
    map_df = _prepare_map_data(dataframe.head(500))
    if map_df.empty:
        st.info("No location data available for the current filter selection.")
        return

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[longitude, latitude]",
        get_fill_color="[255, 75, 75, 180]",
        get_radius="point_radius",
        pickable=True,
    )

    tooltip = {
        "html": "<b>{address}</b><br/>District: {district}<br/>Risk: {risk_label}<br/>Score: {risk_score}",
        "style": {"backgroundColor": "#111111", "color": "#ffffff", "border": "1px solid #ff4b4b"},
    }

    view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=11, pitch=30)
    st.pydeck_chart(
        pdk.Deck(
            map_provider="carto",
            map_style="dark_matter",
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip,
        )
    )


def render_overview(
    property_df: pd.DataFrame,
    district_df: pd.DataFrame,
    start_card: Callable[[str, str | None], None],
    end_card: Callable[[], None],
) -> None:
    total_properties = int(len(property_df))
    high_risk, critical_risk = _risk_counts(property_df)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Total Properties", f"{total_properties:,}")
    metric_cols[1].metric("High Risk", f"{high_risk:,}")
    metric_cols[2].metric("Critical Risk", f"{critical_risk:,}")

    chart_col, table_col = st.columns([1.3, 1.0], gap="large")

    with chart_col:
        start_card("Risk Distribution", "Property risk segmentation from the filtered Gold dataset.")
        chart = _build_distribution_chart(property_df)
        if chart is not None:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Risk category data is not available.")
        end_card()

    with table_col:
        start_card("Top 10 Risky Properties", "Highest scored properties for quick triage.")
        if property_df.empty:
            st.info("No properties matched the current filters.")
        else:
            display_columns = [
                column
                for column in ["address", "district", "risk_category", "risk_score", "top_risk_factor_1"]
                if column in property_df.columns
            ]
            top_df = property_df.sort_values("risk_score", ascending=False).head(10)
            st.dataframe(top_df[display_columns], use_container_width=True, hide_index=True)
        end_card()

    start_card("Risk Map", "Spatial scan of the current risk footprint across San Francisco.")
    _render_map(property_df)
    end_card()

    if not district_df.empty:
        start_card("District Snapshot", "Quick district-level summary for leadership review.")
        display_columns = [col for col in district_df.columns if col in ["district", "avg_risk_score", "risk_score", "property_count"]]
        if display_columns:
            st.dataframe(
                district_df[display_columns].sort_values(display_columns[-1], ascending=False).head(10),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.dataframe(district_df.head(10), use_container_width=True, hide_index=True)
        end_card()

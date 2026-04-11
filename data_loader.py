from __future__ import annotations

from typing import Dict

import pandas as pd
import streamlit as st

from db_connect import get_connection


MAX_ROWS = 10_000

TABLE_QUERIES = {
    "property_risk_master": f"""
        SELECT * FROM workspace.sf_fire_gold.property_risk_master LIMIT {MAX_ROWS}
    """,
    "district_risk_summary": f"""
        SELECT * FROM workspace.sf_fire_gold.district_risk_summary LIMIT {MAX_ROWS}
    """,
    "compliance_tracking": f"""
        SELECT * FROM workspace.sf_fire_gold.compliance_tracking LIMIT {MAX_ROWS}
    """,
    "response_optimization": f"""
        SELECT * FROM workspace.sf_fire_gold.response_optimization LIMIT {MAX_ROWS}
    """,
    "inspection_effectiveness": f"""
        SELECT * FROM workspace.sf_fire_gold.inspection_effectiveness LIMIT {MAX_ROWS}
    """,
    "ml_risk_predictions": f"""
        SELECT * FROM workspace.sf_fire_gold.ml_risk_predictions LIMIT {MAX_ROWS}
    """
}

def _normalize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized = dataframe.copy()
    normalized.columns = [
        str(column).strip().lower().replace(" ", "_").replace("-", "_") for column in normalized.columns
    ]
    return normalized


def _first_matching_column(dataframe: pd.DataFrame, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in dataframe.columns:
            return candidate
    return None


def _ensure_alias_columns(table_name: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()

    risk_category_col = _first_matching_column(df, ["risk_category", "risk_band", "risk_level"])
    if risk_category_col and "risk_category" not in df.columns:
        df["risk_category"] = df[risk_category_col]

    district_col = _first_matching_column(df, ["district", "fire_district", "district_name"])
    if district_col and "district" not in df.columns:
        df["district"] = df[district_col]

    risk_score_col = _first_matching_column(df, ["risk_score", "avg_risk_score", "predicted_risk_score"])
    if risk_score_col and "risk_score" not in df.columns:
        df["risk_score"] = pd.to_numeric(df[risk_score_col], errors="coerce")

    if table_name == "property_risk_master":
        address_col = _first_matching_column(df, ["address", "property_address", "site_address"])
        if address_col and "address" not in df.columns:
            df["address"] = df[address_col]

    return df


@st.cache_data(ttl=600, show_spinner=False)
def load_table(query: str) -> pd.DataFrame:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
    dataframe = pd.DataFrame(rows, columns=columns)
    return _normalize_columns(dataframe)


@st.cache_data(ttl=600, show_spinner=False)
def load_all_data() -> Dict[str, pd.DataFrame]:
    loaded = {}
    for table_name, query in TABLE_QUERIES.items():
        loaded[table_name] = _ensure_alias_columns(table_name, load_table(query))
    return loaded

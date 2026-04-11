from __future__ import annotations

import pandas as pd


def apply_global_filters(
    dataframe: pd.DataFrame,
    risk_categories: list[str] | None = None,
    districts: list[str] | None = None,
    min_risk_score: float = 0,
) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return dataframe

    filtered = dataframe.copy()

    if risk_categories and "risk_category" in filtered.columns:
        filtered = filtered[filtered["risk_category"].astype(str).isin(risk_categories)]

    if districts and "district" in filtered.columns:
        filtered = filtered[filtered["district"].astype(str).isin(districts)]

    if "risk_score" in filtered.columns:
        numeric_score = pd.to_numeric(filtered["risk_score"], errors="coerce").fillna(0)
        filtered = filtered[numeric_score >= min_risk_score]

    return filtered

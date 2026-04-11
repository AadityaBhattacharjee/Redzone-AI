from __future__ import annotations

import streamlit as st

from components.compliance import render_compliance
from components.district import render_district
from components.inspection import render_inspection
from components.ml_predictor import render_ml_predictor
from components.overview import render_overview
from components.response import render_response
from data_loader import load_all_data
from utils.filters import apply_global_filters


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="SF Fire Intelligence Dashboard",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# THEME
# -----------------------------
def apply_theme() -> None:
    st.markdown(
        """
        <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
def build_sidebar_filters(property_df):
    st.sidebar.markdown("## Control Center")

    risk_options = (
        sorted(property_df["risk_category"].dropna().astype(str).unique())
        if "risk_category" in property_df.columns
        else []
    )

    district_options = (
        sorted(property_df["district"].dropna().astype(str).unique())
        if "district" in property_df.columns
        else []
    )

    selected_risk = st.sidebar.multiselect("Risk Category", risk_options, default=risk_options)
    selected_districts = st.sidebar.multiselect("District", district_options, default=district_options)
    min_risk_score = st.sidebar.slider("Minimum Risk Score", 0, 100, 0)

    return {
        "risk_categories": selected_risk,
        "districts": selected_districts,
        "min_risk_score": min_risk_score,
    }


# -----------------------------
# CARD SYSTEM (REQUIRED)
# -----------------------------
CARD_STACK = []

def start_card(title: str, caption: str | None = None):
    container = st.container(border=True)
    CARD_STACK.append(container)
    container.__enter__()
    st.subheader(title)
    if caption:
        st.caption(caption)

def end_card():
    container = CARD_STACK.pop()
    container.__exit__(None, None, None)


# -----------------------------
# MAIN APP
# -----------------------------
def main() -> None:
    apply_theme()

    st.title("Redzone AI")

    # -----------------------------
    # LOAD DATA
    # -----------------------------
    try:
        with st.spinner("Loading Databricks data..."):
            data = load_all_data()
    except Exception as exc:
        st.error(f"Unable to load Databricks data: {exc}")
        st.stop()

    property_df = data["property_risk_master"]

    # -----------------------------
    # FILTERS
    # -----------------------------
    filters = build_sidebar_filters(property_df)

    filtered_data = {
        name: apply_global_filters(
            dataframe=df,
            risk_categories=filters["risk_categories"],
            districts=filters["districts"],
            min_risk_score=filters["min_risk_score"],
        )
        for name, df in data.items()
    }

    # -----------------------------
    # NAVIGATION
    # -----------------------------
    pages = [
        "Overview",
        "District",
        "Compliance",
        "Response",
        "Inspection",
        "ML Predictor",
    ]

    page = st.sidebar.radio("Navigate", pages)

    # -----------------------------
    # PAGES (✅ FIXED HERE)
    # -----------------------------
    if page == "Overview":
        render_overview(
            property_df=filtered_data["property_risk_master"],
            district_df=filtered_data["district_risk_summary"],
            start_card=start_card,
            end_card=end_card,
        )

    elif page == "District":
        render_district(
            district_df=filtered_data["district_risk_summary"],
            start_card=start_card,
            end_card=end_card,
        )

    elif page == "Compliance":
        render_compliance(
            compliance_df=filtered_data["compliance_tracking"],
            property_df=filtered_data["property_risk_master"],
            start_card=start_card,
            end_card=end_card,
        )

    elif page == "Response":
        render_response(
            response_df=filtered_data["response_optimization"],
            start_card=start_card,
            end_card=end_card,
        )

    elif page == "Inspection":
        render_inspection(
            inspection_df=filtered_data["inspection_effectiveness"],
            start_card=start_card,
            end_card=end_card,
        )

    else:
        render_ml_predictor(
            ml_df=filtered_data["ml_risk_predictions"],
            start_card=start_card,
            end_card=end_card,
        )


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
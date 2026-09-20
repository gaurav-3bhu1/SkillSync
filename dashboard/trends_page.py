import streamlit as st
import pandas as pd

from src.data_loader import load_jobs, load_skills
from src.hybrid_skill_extractor import HybridSkillExtractor
from src.job_skill_mapper import build_job_skill_mapping
from src.trend_engine import (
    calculate_monthly_skill_trends,
    compare_recent_vs_previous,
    get_emerging_skills,
)


@st.cache_data
def load_job_skill_data() -> pd.DataFrame:
    jobs = load_jobs()
    skills = load_skills()

    extractor = HybridSkillExtractor(
        skills,
    )
    return build_job_skill_mapping(
        jobs,
        extractor,
    )


def render():
    st.title("Skill Trends")

    st.write(
        "Track how skill demand changes over time."
    )

    job_skill_mapping = load_job_skill_data()

    roles = sorted(
        job_skill_mapping["role"]
        .dropna()
        .unique()
        .tolist()
    )

    locations = sorted(
        job_skill_mapping["location"]
        .dropna()
        .unique()
        .tolist()
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_role = st.selectbox(
            "Role",
            ["All Roles"] + roles,
            key="trend_role",
        )

    with col2:
        selected_location = st.selectbox(
            "Location",
            ["All Locations"] + locations,
            key="trend_location",
        )

    role_filter = (
        None
        if selected_role == "All Roles"
        else selected_role
    )

    location_filter = (
        None
        if selected_location == "All Locations"
        else selected_location
    )

    comparison = compare_recent_vs_previous(
        job_skill_mapping,
        role=role_filter,
        location=location_filter,
        window_days=30,
    )

    monthly = calculate_monthly_skill_trends(
        job_skill_mapping,
        role=role_filter,
        location=location_filter,
    )

    emerging = get_emerging_skills(comparison)

    if comparison.empty:
        st.warning(
            "Not enough matching data for trend analysis."
        )
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Emerging Skills",
            len(
                comparison[
                    comparison["trend"] == "Emerging"
                ]
            ),
        )

    with col2:
        st.metric(
            "Stable Skills",
            len(
                comparison[
                    comparison["trend"] == "Stable"
                ]
            ),
        )

    with col3:
        st.metric(
            "Declining Skills",
            len(
                comparison[
                    comparison["trend"] == "Declining"
                ]
            ),
        )

    st.subheader("Emerging Skills")

    if emerging.empty:
        st.info(
            "No emerging skills detected using the "
            "current prototype threshold."
        )
    else:
        emerging_display = emerging[
            [
                "skill",
                "recent_job_count",
                "recent_demand_percentage",
                "change_percentage_points",
            ]
        ].rename(
            columns={
                "skill": "Skill",
                "recent_job_count": "Recent Jobs",
                "recent_demand_percentage": "Recent Demand %",
                "change_percentage_points": "Change (pp)",
            }
        )

        st.dataframe(
            emerging_display,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Monthly Skill Demand")

    if not monthly.empty:

        chart_data = (
            monthly[
                [
                    "month",
                    "skill",
                    "demand_percentage",
                ]
            ]
            .pivot(
                index="month",
                columns="skill",
                values="demand_percentage",
            )
            .fillna(0)
        )

        st.line_chart(chart_data)

    st.subheader("Trend Classification")

    trend_display = comparison[
        [
            "skill",
            "previous_demand_percentage",
            "recent_demand_percentage",
            "change_percentage_points",
            "trend",
        ]
    ].rename(
        columns={
            "skill": "Skill",
            "previous_demand_percentage": "Previous Demand %",
            "recent_demand_percentage": "Recent Demand %",
            "change_percentage_points": "Change (pp)",
            "trend": "Trend",
        }
    )

    st.dataframe(
        trend_display,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Prototype trend classifications are based on "
        "the current curated dataset and heuristic thresholds."
    )
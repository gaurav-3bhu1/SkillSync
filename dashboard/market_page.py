import streamlit as st
import pandas as pd

from dashboard.data_service import (
    get_hybrid_job_skill_mapping,
)
from src.demand_engine import calculate_filtered_demand

def render():
    st.title("Market Intelligence")

    st.write(
        "Explore skill demand across job roles and locations."
    )

    job_skill_mapping = (
        get_hybrid_job_skill_mapping()
    )

    if job_skill_mapping.empty:
        st.warning("No job-skill data available.")
        return

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
        )

    with col2:
        selected_location = st.selectbox(
            "Location",
            ["All Locations"] + locations,
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

    demand = calculate_filtered_demand(
        job_skill_mapping,
        role=role_filter,
        location=location_filter,
    )

    if demand.empty:
        st.warning(
            "No matching job postings found "
            "for the selected filters."
        )
        return

    filtered_jobs = job_skill_mapping.copy()

    if role_filter:
        filtered_jobs = filtered_jobs[
            filtered_jobs["role"] == role_filter
        ]

    if location_filter:
        filtered_jobs = filtered_jobs[
            filtered_jobs["location"] == location_filter
        ]

    total_jobs = filtered_jobs["job_id"].nunique()

    top_skills = demand.head(10)

    st.subheader("Market Overview")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Jobs Analyzed",
            total_jobs,
        )

    with metric2:
        st.metric(
            "Skills Detected",
            demand["skill"].nunique(),
        )

    with metric3:
        top_skill = demand.iloc[0]

        st.metric(
            "Top Skill",
            top_skill["skill"],
            f'{top_skill["demand_percentage"]:.2f}% demand',
        )

    st.subheader("Top In-Demand Skills")

    chart_data = (
        top_skills[
            [
                "skill",
                "demand_percentage",
            ]
        ]
        .set_index("skill")
    )

    st.bar_chart(
        chart_data,
        horizontal=True,
    )

    st.subheader("Demand Details")

    display_data = demand[
        [
            "skill",
            "job_count",
            "demand_percentage",
        ]
    ].copy()

    display_data = display_data.rename(
        columns={
            "skill": "Skill",
            "job_count": "Jobs",
            "demand_percentage": "Demand %",
        }
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Current prototype scope: 250 curated/simulated "
        "job postings across 4 locations."
    )
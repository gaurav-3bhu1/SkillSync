import streamlit as st
import pandas as pd

from dashboard.data_service import (
    get_hybrid_job_skill_mapping,
    get_courses,
)

from src.district_planner import (
    build_district_role_profile,
    build_district_skill_profile,
    build_training_priorities,
    compare_districts,
)

from src.training_planner import (
    build_location_training_plan,
)

from src.explanation_engine import (
    explain_skill_priority,
    build_training_summary,
)

from src.explanation_engine import (
    build_training_summary,
)


def render():

    st.title(
        "District & Location Training Intelligence"
    )

    st.write(
        "Identify local job demand and training priorities "
        "using prototype location-level labour-market data."
    )

    # ------------------------------------------------------
    # SHARED DATA SERVICE
    # ------------------------------------------------------

    job_skill_mapping = (
        get_hybrid_job_skill_mapping()
    )

    courses = get_courses()

    if job_skill_mapping.empty:
        st.warning(
            "No hybrid job-skill data is available."
        )
        return

    if courses.empty:
        st.warning(
            "No course data is available."
        )
        return

    locations = sorted(
        job_skill_mapping[
            "location"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    selected_location = st.selectbox(
        "District / Location",
        locations,
        key="district_location",
    )

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    filtered_jobs = job_skill_mapping[
        job_skill_mapping["location"]
        == selected_location
    ]

    total_jobs = filtered_jobs[
        "job_id"
    ].nunique()

    role_profile = (
        build_district_role_profile(
            job_skill_mapping,
            selected_location,
        )
    )

    skill_profile = (
        build_district_skill_profile(
            job_skill_mapping,
            selected_location,
            top_k=10,
        )
    )

    priorities = (
        build_training_priorities(
            job_skill_mapping,
            courses,
            selected_location,
            top_k=10,
        )
    )

    training_plan = build_location_training_plan(
        job_skill_mapping,
        courses,
        selected_location,
    )

    # ------------------------------------------------------
    # SUMMARY METRICS
    # ------------------------------------------------------

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Jobs Analyzed",
            total_jobs,
        )

    with metric2:
        st.metric(
            "Roles Detected",
            len(role_profile),
        )

    with metric3:
        st.metric(
            "Skills Detected",
            len(
                filtered_jobs["skill"]
                .unique()
            ),
        )

    # ------------------------------------------------------
    # EXECUTIVE SUMMARY
    # ------------------------------------------------------

    st.subheader(
        f"Recommended Training Strategy for "
        f"{selected_location}"
    )

    high_priority = priorities[
        priorities["priority"].isin(
            ["CRITICAL", "HIGH"]
        )
    ]

    if high_priority.empty:

        st.info(
            "No critical or high-priority skill gaps "
            "were identified."
        )

    else:

        top_priority_skills = (
            high_priority["skill"]
            .head(5)
            .tolist()
        )

        skill_text = ", ".join(
            top_priority_skills
        )

        st.success(
            f"Prioritize training in: {skill_text}."
        )

        st.markdown(
            "**Why these skills?**"
        )

        for explanation in build_training_summary(
            priorities
        ):
            st.write(
                f"• {explanation}"
            )

        st.markdown(
            "**Why these skills?**"
        )

        for explanation in build_training_summary(
            priorities
        ):
            st.write(
                f"• {explanation}"
            )

    # ------------------------------------------------------
    # TOP ROLES
    # ------------------------------------------------------

    st.subheader(
        f"Top Roles in {selected_location}"
    )

    role_display = role_profile.rename(
        columns={
            "role": "Role",
            "job_count": "Jobs",
            "share_percentage": "Share %",
        }
    )

    st.dataframe(
        role_display,
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------
    # TOP SKILLS
    # ------------------------------------------------------

    st.subheader(
        f"Top Skills in {selected_location}"
    )

    if not skill_profile.empty:

        skill_chart = (
            skill_profile[
                [
                    "skill",
                    "demand_percentage",
                ]
            ]
            .set_index("skill")
        )

        st.bar_chart(
            skill_chart,
            horizontal=True,
        )

        skill_display = skill_profile[
            [
                "skill",
                "job_count",
                "demand_percentage",
            ]
        ].rename(
            columns={
                "skill": "Skill",
                "job_count": "Jobs",
                "demand_percentage": "Demand %",
            }
        )

        st.dataframe(
            skill_display,
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------
    # TRAINING PRIORITIES
    # ------------------------------------------------------

    st.subheader(
        f"Training Priorities for "
        f"{selected_location}"
    )

    if priorities.empty:

        st.info(
            "No training priorities could be "
            "calculated for this location."
        )

    else:

        priority_display = priorities.rename(
            columns={
                "skill": "Skill",
                "job_count": "Jobs",
                "demand_percentage": "Demand %",
                "course_count": "Courses Covering Skill",
                "priority": "Priority",
            }
        )

        st.dataframe(
            priority_display,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            "**Recommended training focus**"
        )

        for _, row in priorities.iterrows():

            if row["priority"] in [
                "CRITICAL",
                "HIGH",
            ]:

                st.write(
                    f"→ **{row['skill']}** "
                    f"({row['priority']}, "
                    f"{row['demand_percentage']:.2f}% demand, "
                    f"{row['course_count']} "
                    f"course(s) covering it)"
                )

    # ------------------------------------------------------
    # RECOMMENDED TRAINING COURSES
    # ------------------------------------------------------

    st.subheader(
        f"Recommended Training Courses for "
        f"{selected_location}"
    )

    recommended_courses = training_plan[
        "recommended_courses"
    ]

    if recommended_courses.empty:

        st.info(
            "No course recommendations could "
            "be generated."
        )

    else:

        course_display = recommended_courses.rename(
            columns={
                "course_id": "Course ID",
                "course_name": "Course",
                "skills_covered": (
                    "High-Demand Skills Covered"
                ),
                "priority_score": "Priority Score",
            }
        )

        st.dataframe(
            course_display,
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------
    # DISTRICT COMPARISON
    # ------------------------------------------------------

    st.subheader(
        "District Skill Comparison"
    )

    comparison = compare_districts(
        job_skill_mapping,
        locations,
        top_k=5,
    )

    if not comparison.empty:

        comparison_display = comparison.rename(
            columns={
                "location": "District",
                "skill": "Skill",
                "job_count": "Jobs",
                "demand_percentage": "Demand %",
            }
        )

        st.dataframe(
            comparison_display,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Prototype data is curated/simulated and is "
        "not representative of the Maharashtra "
        "labour market."
    )
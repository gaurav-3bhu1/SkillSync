import streamlit as st
import pandas as pd

from src.data_loader import (
    load_jobs,
    load_courses,
    load_skills,
)
from src.hybrid_skill_extractor import HybridSkillExtractor
from src.job_skill_mapper import build_job_skill_mapping
from src.alignment_engine import (
    calculate_course_alignment,
    prioritize_skill_gaps,
)
from src.demand_engine import calculate_filtered_demand


@st.cache_data
def load_job_skill_data() -> pd.DataFrame:
    """
    Build the normalized job-skill mapping used by
    the demand and alignment engines.
    """

    jobs = load_jobs()
    skills = load_skills()

    extractor = HybridSkillExtractor(
        skills,
    )

    return build_job_skill_mapping(
        jobs,
        extractor,
    )


@st.cache_data
def load_course_data() -> pd.DataFrame:
    """
    Load available training courses.
    """

    return load_courses()


def render():
    st.title("Course Alignment")

    st.write(
        "Compare a training course against current "
        "industry skill demand."
    )

    job_skill_mapping = load_job_skill_data()
    courses = load_course_data()

    if job_skill_mapping.empty:
        st.warning(
            "No job-skill data is available."
        )
        return

    if courses.empty:
        st.warning(
            "No course data is available."
        )
        return

    # ---------------------------------------------------------
    # FILTERS
    # ---------------------------------------------------------

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
            "Target Role",
            roles,
            key="course_role",
        )

    with col2:
        selected_location = st.selectbox(
            "Location",
            locations,
            key="course_location",
        )

    # ---------------------------------------------------------
    # COURSE SELECTION
    # ---------------------------------------------------------

    available_courses = courses.copy()

    course_labels = {
        row["course_id"]: f'{row["course_id"]} - {row["course_name"]}'
        for _, row in available_courses.iterrows()
    }

    selected_course_id = st.selectbox(
        "Training Course",
        available_courses["course_id"].tolist(),
        format_func=lambda course_id: course_labels[course_id],
        key="selected_course",
    )

    course = available_courses[
        available_courses["course_id"]
        == selected_course_id
    ].iloc[0]

    # ---------------------------------------------------------
    # COURSE INFORMATION
    # ---------------------------------------------------------

    st.subheader("Course Information")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.metric(
            "Course",
            course["course_name"],
        )

    with info2:
        st.metric(
            "Provider",
            course["provider"],
        )

    with info3:
        st.metric(
            "Course Location",
            course["location"],
        )

    st.write(
        f"**Description:** {course['description']}"
    )

    # ---------------------------------------------------------
    # COURSE SKILLS
    # ---------------------------------------------------------

    course_skills = [
        skill.strip()
        for skill in str(course["skills"]).split(";")
        if skill.strip()
    ]

    st.subheader("Course Skills")

    st.write(
        ", ".join(course_skills)
    )

    # ---------------------------------------------------------
    # INDUSTRY DEMAND
    # ---------------------------------------------------------

    demand = calculate_filtered_demand(
        job_skill_mapping,
        role=selected_role,
        location=selected_location,
    )

    if demand.empty:
        st.warning(
            "No matching job postings were found "
            "for this role and location."
        )
        return

    # ---------------------------------------------------------
    # ALIGNMENT ENGINE
    # ---------------------------------------------------------

    alignment = calculate_course_alignment(
        course_skills=course_skills,
        demand_df=demand,
        top_k=10,
    )

    alignment_score = float(
        alignment["alignment_score"]
    )

    covered_skills = alignment[
        "covered_skills"
    ]

    missing_skills = alignment[
        "missing_skills"
    ]

    # ---------------------------------------------------------
    # ALIGNMENT SCORE
    # ---------------------------------------------------------

    st.subheader("Industry Alignment")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Alignment Score",
            f"{alignment_score:.2f}%",
        )

    with metric2:
        st.metric(
            "Skills Covered",
            len(covered_skills),
        )

    with metric3:
        st.metric(
            "Skills Missing",
            len(missing_skills),
        )

    # ---------------------------------------------------------
    # SKILL COVERAGE
    # ---------------------------------------------------------

    left, right = st.columns(2)

    with left:
        st.subheader("Covered Skills")

        if covered_skills:
            for skill in covered_skills:
                st.success(skill)
        else:
            st.info(
                "No high-demand skills are covered "
                "by this course."
            )

    with right:
        st.subheader("Missing Skills")

        if missing_skills:
            for skill in missing_skills:
                st.error(skill)
        else:
            st.success(
                "The course covers all selected "
                "high-demand skills."
            )

    # ---------------------------------------------------------
    # PRIORITIZED GAPS
    # ---------------------------------------------------------

    st.subheader(
        "Prioritized Skill Gaps"
    )

    gaps = prioritize_skill_gaps(
        missing_skills,
        demand,
    )

    if gaps.empty:
        st.success(
            "No curriculum gaps detected."
        )
    else:
        gap_display = gaps[
            [
                "skill",
                "job_count",
                "demand_percentage",
                "priority",
            ]
        ].rename(
            columns={
                "skill": "Skill",
                "job_count": "Jobs",
                "demand_percentage": "Demand %",
                "priority": "Priority",
            }
        )

        st.dataframe(
            gap_display,
            use_container_width=True,
            hide_index=True,
        )

    # ---------------------------------------------------------
    # CURRICULUM RECOMMENDATIONS
    # ---------------------------------------------------------

    st.subheader(
        "Curriculum Recommendations"
    )

    if gaps.empty:
        st.info(
            "No curriculum updates are required "
            "for the selected demand profile."
        )
    else:
        for _, row in gaps.iterrows():

            st.write(
                f"→ **Add {row['skill']}** "
                f"({row['priority']} priority, "
                f"{row['demand_percentage']:.2f}% demand)"
            )

    # ---------------------------------------------------------
    # INDUSTRY DEMAND PROFILE
    # ---------------------------------------------------------

    st.subheader(
        "Industry Demand Profile"
    )

    demand_display = demand[
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
        demand_display,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Prototype data is curated/simulated and is "
        "not representative of the Maharashtra labour market."
    )
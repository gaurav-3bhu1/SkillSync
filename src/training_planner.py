from __future__ import annotations

import pandas as pd

from src.district_planner import build_training_priorities
from src.district_planner import build_district_role_profile


def recommend_courses_for_location(
    job_skill_df: pd.DataFrame,
    courses: pd.DataFrame,
    location: str,
    top_k_skills: int = 10,
    top_k_courses: int = 5,
) -> pd.DataFrame:
    """
    Recommend courses for a location based on how well
    their skills cover local high-demand skills.

    This is a prototype recommendation heuristic.
    """

    priorities = build_training_priorities(
        job_skill_df,
        courses,
        location,
        top_k=top_k_skills,
    )

    if priorities.empty:
        return pd.DataFrame(
            columns=[
                "course_id",
                "course_name",
                "skills_covered",
                "priority_score",
            ]
        )

    important_skills = priorities[
        priorities["priority"].isin(
            ["CRITICAL", "HIGH", "MEDIUM"]
        )
    ].copy()

    if important_skills.empty:
        important_skills = priorities.copy()

    important_skill_set = {
        skill.strip().casefold()
        for skill in important_skills["skill"]
    }

    rows = []

    for _, course in courses.iterrows():

        course_skills = {
            skill.strip().casefold()
            for skill in str(course["skills"]).split(";")
            if skill.strip()
        }

        matched = (
            course_skills
            & important_skill_set
        )

        if not matched:
            continue

        score = 0.0

        matched_skill_names = []

        for _, priority_row in important_skills.iterrows():

            skill = str(
                priority_row["skill"]
            )

            if skill.strip().casefold() not in matched:
                continue

            demand = float(
                priority_row["demand_percentage"]
            )

            priority = priority_row["priority"]

            weight = {
                "CRITICAL": 4.0,
                "HIGH": 3.0,
                "MEDIUM": 2.0,
                "LOW": 1.0,
            }.get(priority, 1.0)

            score += demand * weight
            matched_skill_names.append(
                skill
            )

        rows.append(
            {
                "course_id": course["course_id"],
                "course_name": course["course_name"],
                "skills_covered": ", ".join(
                    matched_skill_names
                ),
                "priority_score": round(
                    score,
                    2,
                ),
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return pd.DataFrame(
            columns=[
                "course_id",
                "course_name",
                "skills_covered",
                "priority_score",
            ]
        )

    return (
        result
        .sort_values(
            "priority_score",
            ascending=False,
        )
        .head(top_k_courses)
        .reset_index(drop=True)
    )


def build_location_training_plan(
    job_skill_df: pd.DataFrame,
    courses: pd.DataFrame,
    location: str,
) -> dict:
    """
    Build a single structured training plan for a location.
    """

    priorities = build_training_priorities(
        job_skill_df,
        courses,
        location,
        top_k=10,
    )

    role_profile = build_district_role_profile(
        job_skill_df,
        location,
        top_k=5,
    )

    courses_recommended = (
        recommend_courses_for_location(
            job_skill_df,
            courses,
            location,
            top_k_skills=10,
            top_k_courses=5,
        )
    )

    return {
        "location": location,
        "top_roles": role_profile,
        "skill_priorities": priorities,
        "recommended_courses": courses_recommended,
    }
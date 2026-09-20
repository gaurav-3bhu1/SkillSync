from __future__ import annotations

from typing import List

import pandas as pd

from src.demand_engine import calculate_filtered_demand


def build_district_skill_profile(
    job_skill_df: pd.DataFrame,
    location: str,
    top_k: int = 10,
) -> pd.DataFrame:
    """
    Build the top skill-demand profile for a location.
    """

    demand = calculate_filtered_demand(
        job_skill_df,
        location=location,
    )

    if demand.empty:
        return demand

    return demand.head(top_k).copy()


def build_district_role_profile(
    job_skill_df: pd.DataFrame,
    location: str,
    top_k: int = 10,
) -> pd.DataFrame:
    """
    Count unique jobs by normalized role for a district.
    """

    df = job_skill_df[
        job_skill_df["location"].astype(str).str.strip().str.casefold()
        == location.strip().casefold()
    ].copy()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "role",
                "job_count",
                "share_percentage",
            ]
        )

    role_counts = (
        df.groupby("role")["job_id"]
        .nunique()
        .reset_index(name="job_count")
    )

    total_jobs = df["job_id"].nunique()

    role_counts["share_percentage"] = (
        role_counts["job_count"]
        / total_jobs
        * 100
    ).round(2)

    return (
        role_counts
        .sort_values(
            ["job_count", "role"],
            ascending=[False, True],
        )
        .head(top_k)
        .reset_index(drop=True)
    )


def compare_districts(
    job_skill_df: pd.DataFrame,
    locations: List[str],
    top_k: int = 10,
) -> pd.DataFrame:
    """
    Compare skill demand across multiple districts/locations.
    """

    rows = []

    for location in locations:

        demand = calculate_filtered_demand(
            job_skill_df,
            location=location,
        )

        if demand.empty:
            continue

        for _, row in demand.head(top_k).iterrows():
            rows.append(
                {
                    "location": location,
                    "skill": row["skill"],
                    "job_count": row["job_count"],
                    "demand_percentage": row[
                        "demand_percentage"
                    ],
                }
            )

    return pd.DataFrame(rows)


def build_training_priorities(
    job_skill_df: pd.DataFrame,
    courses: pd.DataFrame,
    location: str,
    top_k: int = 10,
) -> pd.DataFrame:
    """
    Identify high-demand skills that appear weakly represented
    in the available course portfolio.

    This is a prototype training-priority heuristic.

    A skill receives:

        HIGH    >= 50% demand
        MEDIUM  >= 25% demand
        LOW     < 25% demand

    Course coverage is the number of courses that explicitly
    list the skill.
    """

    demand = build_district_skill_profile(
        job_skill_df,
        location,
        top_k=top_k,
    )

    if demand.empty:
        return pd.DataFrame(
            columns=[
                "skill",
                "job_count",
                "demand_percentage",
                "course_count",
                "priority",
            ]
        )

    course_rows = []

    for _, course in courses.iterrows():

        raw_skills = str(
            course["skills"]
        )

        course_skills = {
            skill.strip().casefold()
            for skill in raw_skills.split(";")
            if skill.strip()
        }

        for skill in course_skills:
            course_rows.append(
                {
                    "skill": skill,
                    "course_id": course["course_id"],
                }
            )

    course_skill_df = pd.DataFrame(
        course_rows
    )

    coverage = (
        course_skill_df.groupby("skill")["course_id"]
        .nunique()
        .reset_index(name="course_count")
        if not course_skill_df.empty
        else pd.DataFrame(
            columns=["skill", "course_count"]
        )
    )

    demand["skill_key"] = (
        demand["skill"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    coverage["skill_key"] = (
        coverage["skill"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    result = demand.merge(
        coverage[
            ["skill_key", "course_count"]
        ],
        on="skill_key",
        how="left",
    )

    result["course_count"] = (
        result["course_count"]
        .fillna(0)
        .astype(int)
    )

    def classify_priority(row):
        demand_pct = row["demand_percentage"]
        course_count = row["course_count"]

        if demand_pct >= 50 and course_count == 0:
            return "CRITICAL"

        if demand_pct >= 50:
            return "HIGH"

        if demand_pct >= 25 and course_count <= 1:
            return "HIGH"

        if demand_pct >= 25:
            return "MEDIUM"

        return "LOW"

    result["priority"] = result.apply(
        classify_priority,
        axis=1,
    )

    return result[
        [
            "skill",
            "job_count",
            "demand_percentage",
            "course_count",
            "priority",
        ]
    ]
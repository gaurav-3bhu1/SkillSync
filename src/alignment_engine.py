from __future__ import annotations

from typing import Iterable

import pandas as pd


def _normalize_skill_set(
    skills: Iterable[str],
) -> set[str]:
    """
    Convert skill names to a normalized lowercase set
    for comparison.
    """

    return {
        str(skill).strip().lower()
        for skill in skills
        if str(skill).strip()
    }


def calculate_course_alignment(
    course_skills: Iterable[str],
    demand_df: pd.DataFrame,
    top_k: int = 10,
) -> dict:
    """
    Compare course skills against the most demanded skills
    for a selected role/location.

    Alignment is demand-weighted:

        demand covered by course
        ------------------------
        total relevant demand
        × 100

    This is a prototype metric, not an official SIH metric.
    """

    if demand_df.empty:
        return {
            "alignment_score": 0.0,
            "covered_skills": [],
            "missing_skills": [],
            "demand_profile": [],
        }

    required_df = (
        demand_df
        .sort_values(
            "demand_percentage",
            ascending=False,
        )
        .head(top_k)
        .copy()
    )

    course_skill_set = _normalize_skill_set(
        course_skills
    )

    covered = []
    missing = []

    for _, row in required_df.iterrows():

        skill = str(row["skill"]).strip()

        if skill.lower() in course_skill_set:
            covered.append(skill)
        else:
            missing.append(skill)

    total_demand = required_df[
        "demand_percentage"
    ].sum()

    covered_demand = required_df[
        required_df["skill"].str.lower().isin(
            course_skill_set
        )
    ]["demand_percentage"].sum()

    if total_demand == 0:
        alignment_score = 0.0
    else:
        alignment_score = (
            covered_demand / total_demand
        ) * 100

    return {
        "alignment_score": round(
            alignment_score,
            2,
        ),
        "covered_skills": covered,
        "missing_skills": missing,
        "demand_profile": required_df.to_dict(
            orient="records"
        ),
    }

def prioritize_skill_gaps(
    missing_skills: list[str],
    demand_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Rank missing skills by industry demand.

    Prototype rule:
        >= 60% -> HIGH
        >= 30% -> MEDIUM
        < 30%  -> LOW

    These thresholds are implementation choices for the prototype.
    """

    if not missing_skills:
        return pd.DataFrame(
            columns=[
                "skill",
                "demand_percentage",
                "priority",
            ]
        )

    missing_set = {
        skill.lower()
        for skill in missing_skills
    }

    gaps = demand_df[
        demand_df["skill"]
        .str.lower()
        .isin(missing_set)
    ].copy()

    def priority(
        demand: float,
    ) -> str:

        if demand >= 60:
            return "HIGH"

        if demand >= 30:
            return "MEDIUM"

        return "LOW"

    gaps["priority"] = gaps[
        "demand_percentage"
    ].apply(priority)

    return gaps.sort_values(
        "demand_percentage",
        ascending=False,
    ).reset_index(drop=True)
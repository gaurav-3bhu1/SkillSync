from __future__ import annotations

import pandas as pd


def explain_skill_priority(
    priority_row: pd.Series,
) -> str:
    """
    Generate a human-readable explanation for
    a training-priority recommendation.
    """

    skill = priority_row["skill"]
    demand = float(
        priority_row["demand_percentage"]
    )
    job_count = int(
        priority_row["job_count"]
    )
    course_count = int(
        priority_row["course_count"]
    )
    priority = priority_row["priority"]

    if course_count == 0:

        coverage_text = (
            "No available course currently covers "
            "this skill."
        )

    elif course_count == 1:

        coverage_text = (
            "Only one available course currently "
            "covers this skill."
        )

    else:

        coverage_text = (
            f"{course_count} available courses "
            "cover this skill."
        )

    return (
        f"{skill} is classified as {priority} priority "
        f"because it appears in {job_count} local jobs "
        f"({demand:.2f}% demand). "
        f"{coverage_text}"
    )


def explain_course_gap(
    skill: str,
    demand_df: pd.DataFrame,
    course_skills: list[str],
) -> str:
    """
    Explain why a skill is considered a course gap.
    """

    match = demand_df[
        demand_df["skill"].astype(str).str.casefold()
        == skill.casefold()
    ]

    if match.empty:

        return (
            f"{skill} is missing from the course, "
            "but no matching demand record was found."
        )

    row = match.iloc[0]

    demand = float(
        row["demand_percentage"]
    )

    job_count = int(
        row["job_count"]
    )

    if skill in course_skills:

        return (
            f"{skill} is already covered by the course."
        )

    return (
        f"{skill} is missing from the course but "
        f"appears in {job_count} jobs "
        f"({demand:.2f}% demand) in the selected "
        f"market."
    )


def build_training_summary(
    priorities: pd.DataFrame,
) -> list[str]:
    """
    Build concise recommendation explanations.
    """

    if priorities.empty:
        return []

    explanations = []

    for _, row in priorities.iterrows():

        if row["priority"] not in [
            "CRITICAL",
            "HIGH",
        ]:
            continue

        explanations.append(
            explain_skill_priority(
                row
            )
        )

    return explanations
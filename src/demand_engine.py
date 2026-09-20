from __future__ import annotations

import pandas as pd


def calculate_skill_demand(
    job_skill_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate overall skill demand.

    Demand % =
        jobs requiring skill
        --------------------
        total jobs
        × 100

    We count unique job IDs so that a job mentioning a skill
    multiple times does not artificially increase demand.
    """

    if job_skill_df.empty:
        return pd.DataFrame(
            columns=[
                "skill",
                "job_count",
                "demand_percentage",
            ]
        )

    total_jobs = job_skill_df["job_id"].nunique()

    demand = (
        job_skill_df.groupby("skill")["job_id"]
        .nunique()
        .reset_index(name="job_count")
    )

    demand["demand_percentage"] = (
        demand["job_count"] / total_jobs * 100
    ).round(2)

    demand = demand.sort_values(
        "demand_percentage",
        ascending=False,
    )

    return demand


def calculate_filtered_demand(
    job_skill_df: pd.DataFrame,
    role: str | None = None,
    location: str | None = None,
) -> pd.DataFrame:
    """
    Calculate skill demand for an optional role and/or location.
    """

    filtered = job_skill_df.copy()

    if role:
        filtered = filtered[
            filtered["role"] == role
        ]

    if location:
        filtered = filtered[
            filtered["location"] == location
        ]

    return calculate_skill_demand(filtered)
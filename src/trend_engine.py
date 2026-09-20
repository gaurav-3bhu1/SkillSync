from __future__ import annotations

from typing import Optional

import pandas as pd


def _prepare_data(
    job_skill_df: pd.DataFrame,
    role: Optional[str] = None,
    location: Optional[str] = None,
) -> pd.DataFrame:
    """
    Prepare job-skill data for trend analysis.

    Filters by role/location when supplied and converts posted_date
    into a proper datetime column.
    """

    df = job_skill_df.copy()

    if role and role.strip():
        role_value = role.strip().casefold()

        df = df[
            df["role"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == role_value
        ]

    if location and location.strip():
        location_value = location.strip().casefold()

        df = df[
            df["location"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == location_value
        ]

    if df.empty:
        return df

    df["posted_date"] = pd.to_datetime(
        df["posted_date"],
        errors="coerce",
    )

    df = df.dropna(subset=["posted_date"])

    return df


def calculate_monthly_skill_trends(
    job_skill_df: pd.DataFrame,
    role: Optional[str] = None,
    location: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calculate monthly skill demand.

    For each month and skill:

        job_count = unique jobs requiring the skill

        demand_percentage =
            jobs requiring skill / total unique jobs in month * 100
    """

    df = _prepare_data(
        job_skill_df,
        role=role,
        location=location,
    )

    columns = [
        "month",
        "skill",
        "job_count",
        "total_jobs",
        "demand_percentage",
    ]

    if df.empty:
        return pd.DataFrame(columns=columns)

    df["month"] = df["posted_date"].dt.to_period("M").astype(str)

    skill_counts = (
        df.groupby(["month", "skill"])["job_id"]
        .nunique()
        .reset_index(name="job_count")
    )

    total_jobs = (
        df.groupby("month")["job_id"]
        .nunique()
        .reset_index(name="total_jobs")
    )

    trends = skill_counts.merge(
        total_jobs,
        on="month",
        how="left",
    )

    trends["demand_percentage"] = (
        trends["job_count"]
        / trends["total_jobs"]
        * 100
    )

    trends["demand_percentage"] = trends[
        "demand_percentage"
    ].round(2)

    trends = trends.sort_values(
        ["month", "demand_percentage"],
        ascending=[True, False],
    ).reset_index(drop=True)

    return trends[columns]


def compare_recent_vs_previous(
    job_skill_df: pd.DataFrame,
    role: Optional[str] = None,
    location: Optional[str] = None,
    window_days: int = 30,
) -> pd.DataFrame:
    """
    Compare skill demand in the most recent period against
    the immediately preceding period.

    The latest date in the dataset is used as the endpoint
    of the recent period.

    Returns:

        skill
        previous_job_count
        recent_job_count
        previous_demand_percentage
        recent_demand_percentage
        change_percentage_points
        growth_percentage
        trend
    """

    if window_days <= 0:
        raise ValueError("window_days must be greater than 0")

    df = _prepare_data(
        job_skill_df,
        role=role,
        location=location,
    )

    columns = [
        "skill",
        "previous_job_count",
        "recent_job_count",
        "previous_demand_percentage",
        "recent_demand_percentage",
        "change_percentage_points",
        "growth_percentage",
        "trend",
    ]

    if df.empty:
        return pd.DataFrame(columns=columns)

    latest_date = df["posted_date"].max().normalize()

    recent_start = (
        latest_date
        - pd.Timedelta(days=window_days - 1)
    )

    previous_end = recent_start - pd.Timedelta(days=1)

    previous_start = (
        previous_end
        - pd.Timedelta(days=window_days - 1)
    )

    recent_df = df[
        df["posted_date"].between(
            recent_start,
            latest_date,
        )
    ]

    previous_df = df[
        df["posted_date"].between(
            previous_start,
            previous_end,
        )
    ]

    recent_total_jobs = recent_df["job_id"].nunique()
    previous_total_jobs = previous_df["job_id"].nunique()

    all_skills = sorted(
        set(recent_df["skill"].dropna())
        | set(previous_df["skill"].dropna())
    )

    rows = []

    for skill in all_skills:

        previous_job_count = previous_df[
            previous_df["skill"] == skill
        ]["job_id"].nunique()

        recent_job_count = recent_df[
            recent_df["skill"] == skill
        ]["job_id"].nunique()

        if previous_total_jobs > 0:
            previous_demand = (
                previous_job_count
                / previous_total_jobs
                * 100
            )
        else:
            previous_demand = 0.0

        if recent_total_jobs > 0:
            recent_demand = (
                recent_job_count
                / recent_total_jobs
                * 100
            )
        else:
            recent_demand = 0.0

        change_pp = recent_demand - previous_demand

        if previous_demand > 0:
            growth_percentage = (
                (recent_demand - previous_demand)
                / previous_demand
                * 100
            )
        else:
            growth_percentage = None

        # Prototype classification rule.
        #
        # "Emerging" means the skill is gaining at least
        # 10 percentage points and has at least 2 recent jobs.
        #
        # These thresholds are prototype choices and should
        # later be validated against real labour-market data.

        if recent_job_count >= 2 and change_pp >= 10:
            trend = "Emerging"

        elif previous_job_count >= 2 and change_pp <= -10:
            trend = "Declining"

        else:
            trend = "Stable"

        rows.append(
            {
                "skill": skill,
                "previous_job_count": previous_job_count,
                "recent_job_count": recent_job_count,
                "previous_demand_percentage": round(
                    previous_demand,
                    2,
                ),
                "recent_demand_percentage": round(
                    recent_demand,
                    2,
                ),
                "change_percentage_points": round(
                    change_pp,
                    2,
                ),
                "growth_percentage": (
                    round(growth_percentage, 2)
                    if growth_percentage is not None
                    else None
                ),
                "trend": trend,
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return pd.DataFrame(columns=columns)

    trend_order = {
        "Emerging": 0,
        "Stable": 1,
        "Declining": 2,
    }

    result["_trend_order"] = result["trend"].map(
        trend_order
    )

    result = result.sort_values(
        ["_trend_order", "change_percentage_points"],
        ascending=[True, False],
    )

    result = result.drop(
        columns=["_trend_order"]
    ).reset_index(drop=True)

    return result[columns]


def get_emerging_skills(
    comparison_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return only emerging skills, ranked by
    percentage-point growth.
    """

    if comparison_df.empty:
        return comparison_df.copy()

    emerging = comparison_df[
        comparison_df["trend"] == "Emerging"
    ].copy()

    return emerging.sort_values(
        "change_percentage_points",
        ascending=False,
    ).reset_index(drop=True)
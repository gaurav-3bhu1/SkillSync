from __future__ import annotations

from pathlib import Path
import re

import pandas as pd


JOB_SKILL_PATH = Path(
    "data/processed/job_skill_normalized.csv"
)

TRAINING_SKILL_PATH = Path(
    "data/processed/training_skill_normalized.csv"
)

OUTPUT_PATH = Path(
    "data/processed/skill_demand_supply.csv"
)


def parse_percentage(value) -> float:
    """
    Extract percentage from values such as:

        Low (15%)
        Medium (48%)
        High (82%)

    Returns NaN when no percentage exists.
    """

    if pd.isna(value):
        return float("nan")

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        str(value),
    )

    if not match:
        return float("nan")

    return float(match.group(1))


def build_skill_demand(jobs: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate job-market demand at skill level.

    One job contributes at most one unit of demand to a
    given skill.
    """

    jobs = jobs.copy()

    # ---------------------------------------------------------
    # Basic cleanup
    # ---------------------------------------------------------

    jobs["job_id"] = jobs["job_id"].astype(str)
    jobs["skill_id"] = jobs["skill_id"].astype(str)

    jobs["salary_monthly_inr"] = pd.to_numeric(
        jobs["salary_monthly_inr"],
        errors="coerce",
    )

    jobs["automation_risk_pct"] = jobs[
        "automation_risk_index"
    ].apply(parse_percentage)

    # ---------------------------------------------------------
    # Remove duplicate job-skill pairs.
    # ---------------------------------------------------------

    jobs = jobs.drop_duplicates(
        subset=["job_id", "skill_id"]
    )

    grouped = jobs.groupby(
        [
            "skill_id",
            "skill",
            "skill_family",
            "skill_sector",
        ],
        dropna=False,
    )

    demand = grouped.agg(
        demand_job_count=(
            "job_id",
            "nunique",
        ),
        demand_role_count=(
            "role",
            "nunique",
        ),
        demand_district_count=(
            "location",
            "nunique",
        ),
        demand_industry_count=(
            "industry",
            "nunique",
        ),
        avg_salary_monthly_inr=(
            "salary_monthly_inr",
            "mean",
        ),
        avg_automation_risk_pct=(
            "automation_risk_pct",
            "mean",
        ),
    ).reset_index()

    # ---------------------------------------------------------
    # Demand trend distribution
    # ---------------------------------------------------------

    trend_counts = (
        jobs.groupby(
            ["skill_id", "demand_trend"]
        )
        .size()
        .unstack(
            fill_value=0
        )
    )

    for trend in [
        "Emerging",
        "Stable",
        "Declining",
    ]:
        if trend not in trend_counts.columns:
            trend_counts[trend] = 0

    trend_counts = trend_counts[
        ["Emerging", "Stable", "Declining"]
    ]

    trend_counts.columns = [
        "emerging_job_count",
        "stable_job_count",
        "declining_job_count",
    ]

    demand = demand.merge(
        trend_counts,
        left_on="skill_id",
        right_index=True,
        how="left",
    )

    # ---------------------------------------------------------
    # Trend shares
    # ---------------------------------------------------------

    demand["emerging_share"] = (
        demand["emerging_job_count"]
        / demand["demand_job_count"]
    )

    demand["stable_share"] = (
        demand["stable_job_count"]
        / demand["demand_job_count"]
    )

    demand["declining_share"] = (
        demand["declining_job_count"]
        / demand["demand_job_count"]
    )

    def classify_trend(row):

        emerging = row["emerging_share"]
        declining = row["declining_share"]

        if emerging >= 0.50:
            return "EMERGING"

        if declining >= 0.50:
            return "DECLINING"

        return "MIXED_STABLE"

    demand["skill_demand_trend_signal"] = (
        demand.apply(
            classify_trend,
            axis=1,
        )
    )

    return demand


def build_skill_supply(training: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate training supply at skill level.

    ONLY skills_taught rows count as supply.

    Because course intake applies to the whole course rather
    than each skill independently, annual intake is divided
    across the number of taught skills to create an
    allocated_skill_seats proxy.
    """

    training = training.copy()

    # ---------------------------------------------------------
    # Only actual taught skills count as supply.
    # ---------------------------------------------------------

    supply = training[
        (training["source"] == "skills_taught")
        & (
            training["counts_as_supply"]
            .astype(str)
            .str.lower()
            == "true"
        )
    ].copy()

    if supply.empty:
        raise ValueError(
            "No skills_taught rows available for supply calculation."
        )

    # ---------------------------------------------------------
    # Numeric fields
    # ---------------------------------------------------------

    supply["annual_intake_seats"] = pd.to_numeric(
        supply["annual_intake_seats"],
        errors="coerce",
    ).fillna(0)

    supply["placement_rate_pct"] = pd.to_numeric(
        supply["placement_rate_pct"],
        errors="coerce",
    ).fillna(0)

    # ---------------------------------------------------------
    # Identify training program.
    # ---------------------------------------------------------

    supply["program_key"] = (
        supply["iti_id"].astype(str)
        + "::"
        + supply["course_name"].astype(str)
    )

    supply["skill_id"] = supply[
        "skill_id"
    ].astype(str)

    # Avoid duplicate program-skill rows.
    supply = supply.drop_duplicates(
        subset=["program_key", "skill_id"]
    )

    # ---------------------------------------------------------
    # Number of skills taught by each program.
    # ---------------------------------------------------------

    skill_counts = (
        supply.groupby("program_key")
        .size()
        .rename("taught_skill_count")
    )

    supply = supply.join(
        skill_counts,
        on="program_key",
    )

    supply["allocated_skill_seats"] = (
        supply["annual_intake_seats"]
        / supply["taught_skill_count"]
    )

    # ---------------------------------------------------------
    # Placement-adjusted proxy.
    #
    # This is NOT actual placements.
    # ---------------------------------------------------------

    supply["effective_placed_seat_proxy"] = (
        supply["allocated_skill_seats"]
        * supply["placement_rate_pct"]
        / 100.0
    )

    # ---------------------------------------------------------
    # Aggregate by skill.
    # ---------------------------------------------------------

    grouped = supply.groupby(
        [
            "skill_id",
            "skill",
            "skill_family",
            "skill_sector",
        ],
        dropna=False,
    )

    result = grouped.agg(
        training_program_count=(
            "program_key",
            "nunique",
        ),
        training_iti_count=(
            "iti_id",
            "nunique",
        ),
        training_district_count=(
            "location",
            "nunique",
        ),
        allocated_skill_seats=(
            "allocated_skill_seats",
            "sum",
        ),
        effective_placed_seat_proxy=(
            "effective_placed_seat_proxy",
            "sum",
        ),
    ).reset_index()

    # ---------------------------------------------------------
    # Weighted average placement rate.
    # ---------------------------------------------------------

    supply["placement_weight"] = (
        supply["allocated_skill_seats"]
    )

    weighted_placement = (
        supply.assign(
            placement_weighted=(
                supply["placement_rate_pct"]
                * supply["allocated_skill_seats"]
            )
        )
        .groupby("skill_id")
        .agg(
            placement_weighted_total=(
                "placement_weighted",
                "sum",
            ),
            placement_weight_total=(
                "placement_weight",
                "sum",
            ),
        )
    )

    weighted_placement["weighted_avg_placement_rate_pct"] = (
        weighted_placement[
            "placement_weighted_total"
        ]
        / weighted_placement[
            "placement_weight_total"
        ]
    )

    result = result.merge(
        weighted_placement[
            [
                "weighted_avg_placement_rate_pct"
            ]
        ],
        left_on="skill_id",
        right_index=True,
        how="left",
    )

    # ---------------------------------------------------------
    # Source-provided mismatch flag.
    #
    # This is reported separately from SkillSync's own signal.
    # ---------------------------------------------------------

    mismatch = (
        supply.groupby("skill_id")[
            "mismatch_flag"
        ]
        .agg(
            lambda values: " | ".join(
                sorted(
                    set(
                        str(v)
                        for v in values
                        if str(v).strip()
                    )
                )
            )
        )
        .rename(
            "source_mismatch_flags"
        )
    )

    result = result.merge(
        mismatch,
        left_on="skill_id",
        right_index=True,
        how="left",
    )

    return result


def classify_training_capacity(
    demand_jobs: float,
    allocated_skill_seats: float,
) -> str:

    if demand_jobs <= 0:
        return "NO_DEMAND"

    if allocated_skill_seats <= 0:
        return "NO_RECORDED_TRAINING_SUPPLY"

    ratio = (
        allocated_skill_seats
        / demand_jobs
    )

    if ratio < 0.25:
        return "VERY_LOW_SUPPLY_RELATIVE_TO_DEMAND"

    if ratio < 0.50:
        return "LOW_SUPPLY_RELATIVE_TO_DEMAND"

    if ratio < 1.00:
        return "MODERATE_SUPPLY_RELATIVE_TO_DEMAND"

    if ratio < 2.00:
        return "HIGHER_SUPPLY_RELATIVE_TO_DEMAND"

    return "HIGH_SUPPLY_RELATIVE_TO_DEMAND"


def build_demand_supply_table(
    demand: pd.DataFrame,
    supply: pd.DataFrame,
) -> pd.DataFrame:

    result = demand.merge(
        supply,
        on=[
            "skill_id",
            "skill",
            "skill_family",
            "skill_sector",
        ],
        how="outer",
    )

    # ---------------------------------------------------------
    # Fill missing sides.
    # ---------------------------------------------------------

    numeric_columns = [
        "demand_job_count",
        "demand_role_count",
        "demand_district_count",
        "demand_industry_count",
        "avg_salary_monthly_inr",
        "avg_automation_risk_pct",
        "emerging_job_count",
        "stable_job_count",
        "declining_job_count",
        "emerging_share",
        "stable_share",
        "declining_share",
        "training_program_count",
        "training_iti_count",
        "training_district_count",
        "allocated_skill_seats",
        "effective_placed_seat_proxy",
        "weighted_avg_placement_rate_pct",
    ]

    for column in numeric_columns:
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

            result[column] = result[column].fillna(0)

    result["source_mismatch_flags"] = (
        result[
            "source_mismatch_flags"
        ].fillna("")
    )

    # ---------------------------------------------------------
    # Demand / supply proxy.
    # ---------------------------------------------------------

    result["skill_seat_proxy_per_job"] = 0.0

    demand_mask = (
        result["demand_job_count"] > 0
    )

    result.loc[
        demand_mask,
        "skill_seat_proxy_per_job",
    ] = (
        result.loc[
            demand_mask,
            "allocated_skill_seats",
        ]
        / result.loc[
            demand_mask,
            "demand_job_count",
        ]
    )

    result["jobs_per_allocated_skill_seat"] = 0.0

    supply_mask = (
        result["allocated_skill_seats"] > 0
    )

    result.loc[
        supply_mask,
        "jobs_per_allocated_skill_seat",
    ] = (
        result.loc[
            supply_mask,
            "demand_job_count",
        ]
        / result.loc[
            supply_mask,
            "allocated_skill_seats",
        ]
    )

    # ---------------------------------------------------------
    # Training-capacity signal.
    #
    # Heuristic only.
    # ---------------------------------------------------------

    result[
        "training_capacity_signal"
    ] = result.apply(
        lambda row: classify_training_capacity(
            row["demand_job_count"],
            row["allocated_skill_seats"],
        ),
        axis=1,
    )

    return result


def main():

    print("=" * 80)
    print("SkillSync - Demand-Supply Mismatch Engine")
    print("=" * 80)

    # ==========================================================
    # LOAD
    # ==========================================================

    jobs = pd.read_csv(
        JOB_SKILL_PATH
    )

    training = pd.read_csv(
        TRAINING_SKILL_PATH
    )

    print(
        f"\nNormalized job-skill rows: "
        f"{len(jobs)}"
    )

    print(
        f"Normalized training-skill rows: "
        f"{len(training)}"
    )

    # ==========================================================
    # BUILD DEMAND
    # ==========================================================

    demand = build_skill_demand(
        jobs
    )

    print(
        f"Unique demanded skills: "
        f"{len(demand)}"
    )

    # ==========================================================
    # BUILD SUPPLY
    # ==========================================================

    supply = build_skill_supply(
        training
    )

    print(
        f"Unique supplied skills: "
        f"{len(supply)}"
    )

    # ==========================================================
    # MERGE
    # ==========================================================

    result = build_demand_supply_table(
        demand,
        supply,
    )

    # Sort by job demand.
    result = result.sort_values(
        [
            "demand_job_count",
            "allocated_skill_seats",
        ],
        ascending=[
            False,
            False,
        ],
    ).reset_index(drop=True)

    # ==========================================================
    # WRITE
    # ==========================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    print(
        f"\nCombined skills: "
        f"{len(result)}"
    )

    print("\nTraining capacity signals:")
    print("-" * 80)

    signal_counts = (
        result[
            "training_capacity_signal"
        ]
        .value_counts()
    )

    for signal, count in signal_counts.items():
        print(
            f"{signal}: {count}"
        )

    print(
        "\nTop 25 skills by job demand:"
    )
    print("-" * 80)

    display_columns = [
        "skill",
        "skill_family",
        "skill_sector",
        "demand_job_count",
        "training_program_count",
        "training_iti_count",
        "allocated_skill_seats",
        "skill_seat_proxy_per_job",
        "training_capacity_signal",
    ]

    print(
        result[
            display_columns
        ]
        .head(25)
        .to_string(
            index=False
        )
    )

    print(
        f"\nOutput written to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
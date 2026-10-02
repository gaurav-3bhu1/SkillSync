from __future__ import annotations

from pathlib import Path

import pandas as pd


JOB_SKILL_PATH = Path(
    "data/processed/job_skill_normalized.csv"
)

TRAINING_SKILL_PATH = Path(
    "data/processed/training_skill_normalized.csv"
)

OUTPUT_PATH = Path(
    "data/processed/district_skill_alignment.csv"
)


SCARCITY_SEATS_PER_JOB_THRESHOLD = 0.25
HIGH_DEMAND_PERCENTILE = 0.75


def build_district_demand(
    jobs: pd.DataFrame,
) -> pd.DataFrame:

    jobs = jobs.copy()

    jobs["job_id"] = jobs["job_id"].astype(str)
    jobs["skill_id"] = jobs["skill_id"].astype(str)
    jobs["location"] = jobs["location"].astype(str)

    jobs["salary_monthly_inr"] = pd.to_numeric(
        jobs["salary_monthly_inr"],
        errors="coerce",
    )

    jobs["automation_risk_pct"] = (
        jobs["automation_risk_index"]
        .astype(str)
        .str.extract(r"(\d+(?:\.\d+)?)")[0]
        .astype(float)
    )

    # A job should contribute at most once to a skill.
    jobs = jobs.drop_duplicates(
        subset=[
            "job_id",
            "skill_id",
        ]
    )

    grouped = jobs.groupby(
        [
            "location",
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
    # Trend distribution
    # ---------------------------------------------------------

    trend_counts = (
        jobs.groupby(
            [
                "location",
                "skill_id",
                "demand_trend",
            ]
        )
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for column in [
        "Emerging",
        "Stable",
        "Declining",
    ]:
        if column not in trend_counts.columns:
            trend_counts[column] = 0

    trend_counts = trend_counts.rename(
        columns={
            "Emerging": "emerging_job_count",
            "Stable": "stable_job_count",
            "Declining": "declining_job_count",
        }
    )

    demand = demand.merge(
        trend_counts[
            [
                "location",
                "skill_id",
                "emerging_job_count",
                "stable_job_count",
                "declining_job_count",
            ]
        ],
        on=[
            "location",
            "skill_id",
        ],
        how="left",
    )

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

    # ---------------------------------------------------------
    # Total jobs in each district
    # ---------------------------------------------------------

    district_totals = (
        jobs.groupby("location")["job_id"]
        .nunique()
        .rename("district_total_jobs")
        .reset_index()
    )

    demand = demand.merge(
        district_totals,
        on="location",
        how="left",
    )

    # This is the share of postings in that district that mention
    # this skill. Because each posting can mention several skills,
    # skill shares do not sum to 100%.
    demand["skill_demand_share_of_district_jobs"] = (
        demand["demand_job_count"]
        / demand["district_total_jobs"]
    )

    def classify_trend(row):

        if row["emerging_share"] >= 0.50:
            return "EMERGING"

        if row["declining_share"] >= 0.50:
            return "DECLINING"

        return "MIXED_STABLE"

    demand["district_skill_trend_signal"] = (
        demand.apply(
            classify_trend,
            axis=1,
        )
    )

    return demand


def build_district_training_supply(
    training: pd.DataFrame,
) -> pd.DataFrame:

    training = training.copy()

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
            "No skills_taught rows available."
        )

    supply["annual_intake_seats"] = pd.to_numeric(
        supply["annual_intake_seats"],
        errors="coerce",
    ).fillna(0)

    supply["placement_rate_pct"] = pd.to_numeric(
        supply["placement_rate_pct"],
        errors="coerce",
    ).fillna(0)

    supply["program_key"] = (
        supply["iti_id"].astype(str)
        + "::"
        + supply["course_name"].astype(str)
    )

    supply = supply.drop_duplicates(
        subset=[
            "program_key",
            "skill_id",
        ]
    )

    skill_counts = (
        supply.groupby("program_key")
        .size()
        .rename("taught_skill_count")
    )

    supply = supply.join(
        skill_counts,
        on="program_key",
    )

    # Seat allocation proxy.
    supply["allocated_skill_seats"] = (
        supply["annual_intake_seats"]
        / supply["taught_skill_count"]
    )

    supply["effective_placed_seat_proxy"] = (
        supply["allocated_skill_seats"]
        * supply["placement_rate_pct"]
        / 100.0
    )

    grouped = supply.groupby(
        [
            "location",
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
        training_district_coverage=(
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
    # Weighted placement rate
    # ---------------------------------------------------------

    supply["placement_weighted"] = (
        supply["placement_rate_pct"]
        * supply["allocated_skill_seats"]
    )

    placement = (
        supply.groupby(
            [
                "location",
                "skill_id",
            ]
        )
        .agg(
            placement_weighted_total=(
                "placement_weighted",
                "sum",
            ),
            placement_weight_total=(
                "allocated_skill_seats",
                "sum",
            ),
        )
        .reset_index()
    )

    placement[
        "weighted_avg_placement_rate_pct"
    ] = (
        placement["placement_weighted_total"]
        / placement["placement_weight_total"]
    )

    result = result.merge(
        placement[
            [
                "location",
                "skill_id",
                "weighted_avg_placement_rate_pct",
            ]
        ],
        on=[
            "location",
            "skill_id",
        ],
        how="left",
    )

    # ---------------------------------------------------------
    # Preserve source mismatch flags separately.
    # ---------------------------------------------------------

    flags = (
        supply.groupby(
            [
                "location",
                "skill_id",
            ]
        )["mismatch_flag"]
        .agg(
            lambda values: " | ".join(
                sorted(
                    set(
                        str(value)
                        for value in values
                        if str(value).strip()
                    )
                )
            )
        )
        .reset_index()
        .rename(
            columns={
                "mismatch_flag":
                    "source_mismatch_flags"
            }
        )
    )

    result = result.merge(
        flags,
        on=[
            "location",
            "skill_id",
        ],
        how="left",
    )

    return result


def classify_supply_status(
    demand_jobs: float,
    allocated_seats: float,
) -> str:

    if allocated_seats <= 0:
        return "NO_RECORDED_TRAINING_SUPPLY"

    if demand_jobs <= 0:
        return "SUPPLY_WITHOUT_RECORDED_DEMAND"

    seats_per_job = (
        allocated_seats / demand_jobs
    )

    if seats_per_job < 0.25:
        return "VERY_LOW_CAPACITY"

    if seats_per_job < 0.50:
        return "LOW_CAPACITY"

    if seats_per_job < 1.00:
        return "MODERATE_CAPACITY"

    return "ADEQUATE_OR_HIGH_CAPACITY"


def add_priority_classification(
    alignment: pd.DataFrame,
) -> pd.DataFrame:

    alignment = alignment.copy()

    # Determine what counts as high demand *within each district*.
    # This avoids using one absolute threshold for Pune and a tiny
    # district where the job market is much smaller.
    district_thresholds = (
        alignment[alignment["demand_job_count"] > 0]
        .groupby("location")["demand_job_count"]
        .quantile(HIGH_DEMAND_PERCENTILE)
        .rename(
            "high_demand_threshold_within_district"
        )
    )

    alignment = alignment.merge(
        district_thresholds,
        left_on="location",
        right_index=True,
        how="left",
    )

    alignment[
        "high_demand_within_district"
    ] = (
        alignment["demand_job_count"]
        >= alignment[
            "high_demand_threshold_within_district"
        ]
    )

    # ---------------------------------------------------------
    # Priority classification
    # ---------------------------------------------------------
    #
    # HIGH_PRIORITY:
    #   high local demand + very low/low capacity
    #
    # DEMAND_WITH_CAPACITY:
    #   high local demand but capacity is not low
    #
    # LOCAL_GAP:
    #   lower local demand but no/very low training capacity
    #
    # MONITOR:
    #   remaining combinations
    #

    def classify(row):

        high_demand = bool(
            row["high_demand_within_district"]
        )

        scarce = row[
            "supply_status"
        ] in {
            "NO_RECORDED_TRAINING_SUPPLY",
            "VERY_LOW_CAPACITY",
        }

        low = row[
            "supply_status"
        ] == "LOW_CAPACITY"

        if high_demand and (scarce or low):
            return "HIGH_PRIORITY"

        if high_demand:
            return "DEMAND_WITH_CAPACITY"

        if scarce:
            return "LOCAL_GAP"

        return "MONITOR"

    alignment["priority_band"] = (
        alignment.apply(
            classify,
            axis=1,
        )
    )

    return alignment


def build_district_alignment(
    jobs: pd.DataFrame,
    training: pd.DataFrame,
) -> pd.DataFrame:

    demand = build_district_demand(
        jobs
    )

    supply = build_district_training_supply(
        training
    )

    alignment = demand.merge(
        supply,
        on=[
            "location",
            "skill_id",
            "skill",
            "skill_family",
            "skill_sector",
        ],
        how="outer",
    )

    numeric_columns = [
        "demand_job_count",
        "demand_role_count",
        "demand_industry_count",
        "avg_salary_monthly_inr",
        "avg_automation_risk_pct",
        "emerging_job_count",
        "stable_job_count",
        "declining_job_count",
        "emerging_share",
        "stable_share",
        "declining_share",
        "district_total_jobs",
        "skill_demand_share_of_district_jobs",
        "training_program_count",
        "training_iti_count",
        "training_district_coverage",
        "allocated_skill_seats",
        "effective_placed_seat_proxy",
        "weighted_avg_placement_rate_pct",
    ]

    for column in numeric_columns:
        if column in alignment.columns:
            alignment[column] = pd.to_numeric(
                alignment[column],
                errors="coerce",
            ).fillna(0)

    alignment["source_mismatch_flags"] = (
        alignment["source_mismatch_flags"]
        .fillna("")
    )

    alignment["skill_seat_proxy_per_job"] = 0.0
    alignment["jobs_per_allocated_skill_seat"] = 0.0

    demand_mask = (
        alignment["demand_job_count"] > 0
    )

    supply_mask = (
        alignment["allocated_skill_seats"] > 0
    )

    alignment.loc[
        demand_mask,
        "skill_seat_proxy_per_job",
    ] = (
        alignment.loc[
            demand_mask,
            "allocated_skill_seats",
        ]
        / alignment.loc[
            demand_mask,
            "demand_job_count",
        ]
    )

    alignment.loc[
        supply_mask,
        "jobs_per_allocated_skill_seat",
    ] = (
        alignment.loc[
            supply_mask,
            "demand_job_count",
        ]
        / alignment.loc[
            supply_mask,
            "allocated_skill_seats",
        ]
    )

    alignment["supply_status"] = alignment.apply(
        lambda row: classify_supply_status(
            row["demand_job_count"],
            row["allocated_skill_seats"],
        ),
        axis=1,
    )

    alignment = add_priority_classification(
        alignment
    )

    return alignment


def main():

    print("=" * 80)
    print("SkillSync - District Skill Alignment")
    print("=" * 80)

    jobs = pd.read_csv(
        JOB_SKILL_PATH
    )

    training = pd.read_csv(
        TRAINING_SKILL_PATH
    )

    print(
        f"\nJob-skill rows: {len(jobs)}"
    )

    print(
        f"Training-skill rows: {len(training)}"
    )

    alignment = build_district_alignment(
        jobs,
        training,
    )

    alignment = alignment.sort_values(
        [
            "location",
            "demand_job_count",
        ],
        ascending=[
            True,
            False,
        ],
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    alignment.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nDistricts: "
        f"{alignment['location'].nunique()}"
    )

    print(
        f"District-skill rows: "
        f"{len(alignment)}"
    )

    print("\nPriority bands:")
    print("-" * 80)

    for band, count in (
        alignment["priority_band"]
        .value_counts()
        .items()
    ):
        print(
            f"{band}: {count}"
        )

    print("\nTop HIGH_PRIORITY district-skill pairs:")
    print("-" * 80)

    high = alignment[
        alignment["priority_band"]
        == "HIGH_PRIORITY"
    ].sort_values(
        [
            "demand_job_count",
            "jobs_per_allocated_skill_seat",
        ],
        ascending=[
            False,
            False,
        ],
    )

    columns = [
        "location",
        "skill",
        "skill_sector",
        "demand_job_count",
        "district_total_jobs",
        "training_program_count",
        "training_iti_count",
        "allocated_skill_seats",
        "skill_seat_proxy_per_job",
        "jobs_per_allocated_skill_seat",
        "supply_status",
    ]

    print(
        high[columns]
        .head(30)
        .to_string(index=False)
    )

    print(
        f"\nOutput written to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
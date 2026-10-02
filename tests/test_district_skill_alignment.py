from pathlib import Path

import pandas as pd

from src.district_skill_alignment import (
    build_district_alignment,
)


JOB_PATH = Path(
    "data/processed/job_skill_normalized.csv"
)

TRAINING_PATH = Path(
    "data/processed/training_skill_normalized.csv"
)


def test_district_skill_alignment():

    jobs = pd.read_csv(
        JOB_PATH
    )

    training = pd.read_csv(
        TRAINING_PATH
    )

    result = build_district_alignment(
        jobs,
        training,
    )

    assert not result.empty

    # ---------------------------------------------------------
    # District coverage
    # ---------------------------------------------------------
    #
    # The job dataset contains 35 districts.
    # The combined alignment table may contain additional
    # training-only districts because the engine uses an
    # OUTER merge.
    # ---------------------------------------------------------

    job_districts = set(
        jobs["location"].dropna().unique()
    )

    result_districts = set(
        result["location"].dropna().unique()
    )

    assert len(job_districts) == 35

    # Every job-market district must survive the merge.
    assert job_districts.issubset(
        result_districts
    )

    # ---------------------------------------------------------
    # Core integrity
    # ---------------------------------------------------------

    assert result[
        "skill_id"
    ].notna().all()

    assert (
        result[
            "demand_job_count"
        ] >= 0
    ).all()

    assert (
        result[
            "allocated_skill_seats"
        ] >= 0
    ).all()

    # ---------------------------------------------------------
    # District total jobs
    # ---------------------------------------------------------
    #
    # Rows representing actual job demand must have a
    # positive district total.
    #
    # Training-only districts are allowed to have zero job
    # demand because the merge is intentionally OUTER.
    # ---------------------------------------------------------

    demand_rows = result[
        result["demand_job_count"] > 0
    ]

    assert (
        demand_rows[
            "district_total_jobs"
        ] > 0
    ).all()

    # ---------------------------------------------------------
    # Supply statuses
    # ---------------------------------------------------------

    valid_supply_statuses = {
        "NO_RECORDED_TRAINING_SUPPLY",
        "SUPPLY_WITHOUT_RECORDED_DEMAND",
        "VERY_LOW_CAPACITY",
        "LOW_CAPACITY",
        "MODERATE_CAPACITY",
        "ADEQUATE_OR_HIGH_CAPACITY",
    }

    assert set(
        result[
            "supply_status"
        ].unique()
    ).issubset(
        valid_supply_statuses
    )

    # ---------------------------------------------------------
    # Priority bands
    # ---------------------------------------------------------

    valid_priority_bands = {
        "HIGH_PRIORITY",
        "DEMAND_WITH_CAPACITY",
        "LOCAL_GAP",
        "MONITOR",
    }

    assert set(
        result[
            "priority_band"
        ].unique()
    ).issubset(
        valid_priority_bands
    )

    # ---------------------------------------------------------
    # No-supply rows
    # ---------------------------------------------------------

    no_supply = result[
        result[
            "supply_status"
        ]
        == "NO_RECORDED_TRAINING_SUPPLY"
    ]

    assert (
        no_supply[
            "allocated_skill_seats"
        ] == 0
    ).all()

    # ---------------------------------------------------------
    # Training-only rows
    # ---------------------------------------------------------
    #
    # If a district has supply but no recorded job demand,
    # the engine should explicitly classify it rather than
    # pretending demand exists.
    # ---------------------------------------------------------

    training_only = result[
        (
            result[
                "demand_job_count"
            ] == 0
        )
        &
        (
            result[
                "allocated_skill_seats"
            ] > 0
        )
    ]

    assert (
        training_only[
            "supply_status"
        ] == "SUPPLY_WITHOUT_RECORDED_DEMAND"
    ).all()

    print(
        "District skill alignment tests passed."
    )


if __name__ == "__main__":
    test_district_skill_alignment()
from pathlib import Path

import pandas as pd

from src.demand_supply_engine import (
    build_skill_demand,
    build_skill_supply,
    build_demand_supply_table,
)


JOB_PATH = Path(
    "data/processed/job_skill_normalized.csv"
)

TRAINING_PATH = Path(
    "data/processed/training_skill_normalized.csv"
)


def test_demand_supply_engine():

    jobs = pd.read_csv(
        JOB_PATH
    )

    training = pd.read_csv(
        TRAINING_PATH
    )

    demand = build_skill_demand(
        jobs
    )

    supply = build_skill_supply(
        training
    )

    combined = build_demand_supply_table(
        demand,
        supply,
    )

    # ---------------------------------------------------------
    # Basic integrity
    # ---------------------------------------------------------

    assert not combined.empty

    assert combined[
        "skill_id"
    ].notna().all()

    assert (
        combined[
            "demand_job_count"
        ] >= 0
    ).all()

    assert (
        combined[
            "allocated_skill_seats"
        ] >= 0
    ).all()

    assert (
        combined[
            "training_program_count"
        ] >= 0
    ).all()

    # ---------------------------------------------------------
    # Training supply must only come from skills_taught.
    # ---------------------------------------------------------

    assert (
        training.loc[
            training["source"] == "skills_gap",
            "counts_as_supply",
        ]
        .astype(str)
        .str.lower()
        .eq("false")
        .all()
    )

    # ---------------------------------------------------------
    # Demand count must not exceed unique jobs.
    # ---------------------------------------------------------

    unique_jobs = jobs[
        "job_id"
    ].nunique()

    assert (
        combined[
            "demand_job_count"
        ] <= unique_jobs
    ).all()

    # ---------------------------------------------------------
    # Capacity signals must be known.
    # ---------------------------------------------------------

    valid_signals = {
        "NO_DEMAND",
        "NO_RECORDED_TRAINING_SUPPLY",
        "VERY_LOW_SUPPLY_RELATIVE_TO_DEMAND",
        "LOW_SUPPLY_RELATIVE_TO_DEMAND",
        "MODERATE_SUPPLY_RELATIVE_TO_DEMAND",
        "HIGHER_SUPPLY_RELATIVE_TO_DEMAND",
        "HIGH_SUPPLY_RELATIVE_TO_DEMAND",
    }

    assert set(
        combined[
            "training_capacity_signal"
        ].unique()
    ).issubset(
        valid_signals
    )

    print(
        "Demand-supply engine tests passed."
    )


if __name__ == "__main__":
    test_demand_supply_engine()
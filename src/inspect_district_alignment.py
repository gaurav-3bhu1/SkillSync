from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/processed/district_skill_alignment.csv"
)


def main():

    print("=" * 80)
    print("SkillSync - District Alignment Inspector")
    print("=" * 80)

    df = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"\nDistricts: "
        f"{df['location'].nunique()}"
    )

    print(
        f"District-skill rows: "
        f"{len(df)}"
    )

    # ---------------------------------------------------------
    # District summary
    # ---------------------------------------------------------

    district_summary = (
        df.groupby("location")
        .agg(
            demand_jobs=(
                "demand_job_count",
                "sum",
            ),
            training_programs=(
                "training_program_count",
                "sum",
            ),
            training_iti_count=(
                "training_iti_count",
                "sum",
            ),
            allocated_skill_seats=(
                "allocated_skill_seats",
                "sum",
            ),
            high_priority_skills=(
                "priority_band",
                lambda values: (
                    values == "HIGH_PRIORITY"
                ).sum(),
            ),
            local_gap_skills=(
                "priority_band",
                lambda values: (
                    values == "LOCAL_GAP"
                ).sum(),
            ),
        )
        .sort_values(
            "demand_jobs",
            ascending=False,
        )
    )

    print("\nDistrict summary:")
    print("-" * 80)

    print(
        district_summary.head(20)
        .to_string()
    )

    # ---------------------------------------------------------
    # Districts with demand but no training record
    # ---------------------------------------------------------

    demand_without_supply = df[
        (
            df["demand_job_count"] > 0
        )
        & (
            df["allocated_skill_seats"] == 0
        )
    ].sort_values(
        "demand_job_count",
        ascending=False,
    )

    print(
        "\nTop district-skill gaps with recorded demand "
        "but no recorded training supply:"
    )

    print("-" * 80)

    columns = [
        "location",
        "skill",
        "skill_sector",
        "demand_job_count",
        "district_total_jobs",
        "demand_role_count",
    ]

    print(
        demand_without_supply[
            columns
        ]
        .head(30)
        .to_string(index=False)
    )

    # ---------------------------------------------------------
    # Top local priorities
    # ---------------------------------------------------------

    high = df[
        df["priority_band"]
        == "HIGH_PRIORITY"
    ].sort_values(
        [
            "location",
            "demand_job_count",
        ],
        ascending=[
            True,
            False,
        ],
    )

    print(
        "\nTop HIGH_PRIORITY skills by selected districts:"
    )

    print("-" * 80)

    for district in [
        "Pune",
        "Thane",
        "Nashik",
        "Nagpur",
        "Chhatrapati Sambhaji Nagar",
    ]:

        subset = high[
            high["location"] == district
        ].head(5)

        print(f"\n{district}")

        if subset.empty:
            print("  No HIGH_PRIORITY rows.")
            continue

        for _, row in subset.iterrows():
            print(
                f"  {row['skill']} | "
                f"demand={row['demand_job_count']} | "
                f"seats={row['allocated_skill_seats']:.1f} | "
                f"status={row['supply_status']}"
            )


if __name__ == "__main__":
    main()
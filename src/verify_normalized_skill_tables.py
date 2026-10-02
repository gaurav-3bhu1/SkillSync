from pathlib import Path
import csv
from collections import Counter


JOB_PATH = Path(
    "data/processed/job_skill_normalized.csv"
)

TRAINING_PATH = Path(
    "data/processed/training_skill_normalized.csv"
)


def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def main():

    print("=" * 80)
    print("SkillSync - Normalized Skill Table Verification")
    print("=" * 80)

    jobs = load_csv(JOB_PATH)
    training = load_csv(TRAINING_PATH)

    print("\nJOB TABLE")
    print("-" * 80)

    print(
        f"Rows: {len(jobs)}"
    )

    print(
        f"Unique jobs: "
        f"{len(set(row['job_id'] for row in jobs))}"
    )

    job_status = Counter(
        row["resolution_status"]
        for row in jobs
    )

    for status, count in job_status.items():
        print(
            f"  {status}: {count}"
        )

    print("\nTRAINING TABLE")
    print("-" * 80)

    print(
        f"Rows: {len(training)}"
    )

    print(
        f"Unique ITIs: "
        f"{len(set(row['iti_id'] for row in training))}"
    )

    source_counts = Counter(
        row["source"]
        for row in training
    )

    print("\nSources:")

    for source, count in source_counts.items():
        print(
            f"  {source}: {count}"
        )

    # This is the important safety check.
    gap_supply_errors = [
        row
        for row in training
        if row["source"] == "skills_gap"
        and row["counts_as_supply"].lower() == "true"
    ]

    print(
        f"\nSkills-gap rows incorrectly counted "
        f"as supply: {len(gap_supply_errors)}"
    )

    if gap_supply_errors:
        raise SystemExit(
            "ERROR: skills_gap rows must not count as supply."
        )

    taught_rows = [
        row
        for row in training
        if row["source"] == "skills_taught"
        and row["counts_as_supply"].lower() == "true"
    ]

    print(
        f"Skills-taught rows counted as supply: "
        f"{len(taught_rows)}"
    )

    print("\nSample normalized job skills:")
    print("-" * 80)

    for row in jobs[:10]:
        print(
            f"{row['raw_skill']} "
            f"-> {row['skill']} "
            f"[{row['skill_id']}]"
        )

    print("\nSample normalized training skills:")
    print("-" * 80)

    for row in taught_rows[:10]:
        print(
            f"{row['raw_skill']} "
            f"-> {row['skill']} "
            f"[{row['skill_id']}]"
        )

    print("\nVerification passed.")


if __name__ == "__main__":
    main()
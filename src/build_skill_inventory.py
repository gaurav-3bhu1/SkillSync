from collections import Counter
from pathlib import Path
import csv

from src.external_data_adapter import (
    load_external_jobs,
    standardize_jobs,
    load_external_training_supply,
    standardize_training_supply,
)


OUTPUT_PATH = Path("data/processed/skill_inventory.csv")


def normalize_display(value: str) -> str:
    """Light normalization for comparing raw skill strings."""
    return " ".join(str(value).strip().split())


def collect_skills():
    jobs_raw = load_external_jobs()
    jobs = standardize_jobs(jobs_raw)

    training_raw = load_external_training_supply()
    training = standardize_training_supply(training_raw)

    required_counter = Counter()
    taught_counter = Counter()
    gap_counter = Counter()

    for _, row in jobs.iterrows():
        for skill in row["required_skills"]:
            skill = normalize_display(skill)
            if skill:
                required_counter[skill] += 1

    for _, row in training.iterrows():
        for skill in row["skills_taught"]:
            skill = normalize_display(skill)
            if skill:
                taught_counter[skill] += 1

        for skill in row["skills_gap"]:
            skill = normalize_display(skill)
            if skill:
                gap_counter[skill] += 1

    all_skills = (
        set(required_counter)
        | set(taught_counter)
        | set(gap_counter)
    )

    rows = []

    for skill in all_skills:
        rows.append(
            {
                "raw_skill": skill,
                "job_demand_count": required_counter.get(skill, 0),
                "training_taught_count": taught_counter.get(skill, 0),
                "training_gap_count": gap_counter.get(skill, 0),
                "total_mentions": (
                    required_counter.get(skill, 0)
                    + taught_counter.get(skill, 0)
                    + gap_counter.get(skill, 0)
                ),
            }
        )

    rows.sort(
        key=lambda x: (
            -x["job_demand_count"],
            -x["training_gap_count"],
            -x["training_taught_count"],
            x["raw_skill"].lower(),
        )
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "raw_skill",
                "job_demand_count",
                "training_taught_count",
                "training_gap_count",
                "total_mentions",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return jobs, training, rows


def main():
    print("=" * 70)
    print("SkillSync - Multi-Sector Skill Inventory")
    print("=" * 70)

    jobs, training, rows = collect_skills()

    print(f"\nJobs analyzed: {len(jobs)}")
    print(f"Training records analyzed: {len(training)}")
    print(f"Unique skill strings: {len(rows)}")

    print("\nTop 40 skill strings by job demand:")
    print("-" * 70)

    job_sorted = sorted(
        rows,
        key=lambda x: (-x["job_demand_count"], x["raw_skill"].lower())
    )

    for i, row in enumerate(job_sorted[:40], start=1):
        print(
            f"{i:2}. "
            f"{row['raw_skill']} | "
            f"jobs={row['job_demand_count']} | "
            f"taught={row['training_taught_count']} | "
            f"gap={row['training_gap_count']}"
        )

    print(f"\nInventory written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
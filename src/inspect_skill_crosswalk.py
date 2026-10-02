from pathlib import Path
import csv
from collections import Counter


CROSSWALK_PATH = Path(
    "data/processed/skill_crosswalk.csv"
)


def main():
    print("=" * 80)
    print("SkillSync - Skill Crosswalk Inspection")
    print("=" * 80)

    with CROSSWALK_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        rows = list(csv.DictReader(f))

    status_counts = Counter(
        row["resolution_status"]
        for row in rows
    )

    sector_counts = Counter(
        row["top_job_sector"]
        for row in rows
        if row["top_job_sector"]
    )

    print(f"\nTotal skills: {len(rows)}")

    print("\nResolution status:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

    print("\nTop sectors represented:")
    for sector, count in sector_counts.most_common():
        print(f"  {sector}: {count}")

    print("\nSemantic review candidates:")
    print("-" * 80)

    semantic = [
        row
        for row in rows
        if row["resolution_status"] == "SEMANTIC_REVIEW"
    ]

    semantic.sort(
        key=lambda row: (
            -int(row["job_demand_count"]),
            row["raw_skill"].lower(),
        )
    )

    for row in semantic:
        print(
            f"{row['raw_skill']} "
            f"-> {row['candidate_canonical_skill']} "
            f"(confidence={row['confidence']}, "
            f"jobs={row['job_demand_count']})"
        )


if __name__ == "__main__":
    main()
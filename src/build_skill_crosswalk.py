from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import csv

from src.external_data_adapter import (
    load_external_jobs,
    standardize_jobs,
)


AUDIT_PATH = Path("data/processed/skill_normalization_audit.csv")
OUTPUT_PATH = Path("data/processed/skill_crosswalk.csv")


def load_audit():
    with AUDIT_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def build_skill_context(jobs):
    """
    Build sector/industry context for every raw job skill.
    """
    skill_sector_counts = defaultdict(Counter)

    for _, row in jobs.iterrows():
        sector = str(row["industry"]).strip()

        for skill in row["required_skills"]:
            skill = str(skill).strip()

            if skill:
                skill_sector_counts[skill][sector] += 1

    return skill_sector_counts


def main():
    print("=" * 80)
    print("SkillSync - Operational Skill Crosswalk")
    print("=" * 80)

    jobs_raw = load_external_jobs()
    jobs = standardize_jobs(jobs_raw)

    audit_rows = load_audit()
    skill_context = build_skill_context(jobs)

    provisional_counter = 0
    crosswalk = []

    for row in audit_rows:
        raw_skill = row["raw_skill"]

        status = row["review_status"]
        method = row["method"]

        sectors = skill_context.get(
            raw_skill,
            Counter(),
        )

        if sectors:
            ordered_sectors = sorted(
                sectors.items(),
                key=lambda item: (-item[1], item[0]),
            )

            top_sector = ordered_sectors[0][0]

            sector_distribution = " | ".join(
                f"{sector}:{count}"
                for sector, count in ordered_sectors
            )

        else:
            top_sector = ""
            sector_distribution = ""

        # -----------------------------------------------------
        # EXACT MATCH
        # -----------------------------------------------------
        if status == "AUTO_ACCEPT":
            operational_skill = row["canonical_skill"]
            operational_id = row["skill_id"]
            resolution_status = "EXACT_RESOLVED"
            aggregation_status = "READY"

        # -----------------------------------------------------
        # SEMANTIC MATCH
        # -----------------------------------------------------
        elif status == "REVIEW_REQUIRED":
            operational_skill = row["canonical_skill"]
            operational_id = row["skill_id"]
            resolution_status = "SEMANTIC_REVIEW"
            aggregation_status = "REVIEW"

        # -----------------------------------------------------
        # UNMATCHED
        # -----------------------------------------------------
        else:
            provisional_counter += 1

            operational_skill = raw_skill
            operational_id = f"PRV{provisional_counter:03d}"

            resolution_status = "PROVISIONAL_RAW"
            aggregation_status = "READY_PROVISIONAL"

        crosswalk.append(
            {
                "raw_skill": raw_skill,

                "job_demand_count": row["job_demand_count"],
                "training_taught_count": row["training_taught_count"],
                "training_gap_count": row["training_gap_count"],

                "candidate_canonical_skill": row["canonical_skill"],
                "candidate_skill_id": row["skill_id"],
                "candidate_skill_family": row["skill_family"],
                "candidate_sector": row["sector"],

                "normalization_method": method,
                "confidence": row["confidence"],

                "operational_skill": operational_skill,
                "operational_skill_id": operational_id,

                "resolution_status": resolution_status,
                "aggregation_status": aggregation_status,

                "top_job_sector": top_sector,
                "job_sector_distribution": sector_distribution,
            }
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "raw_skill",
                "job_demand_count",
                "training_taught_count",
                "training_gap_count",
                "candidate_canonical_skill",
                "candidate_skill_id",
                "candidate_skill_family",
                "candidate_sector",
                "normalization_method",
                "confidence",
                "operational_skill",
                "operational_skill_id",
                "resolution_status",
                "aggregation_status",
                "top_job_sector",
                "job_sector_distribution",
            ],
        )

        writer.writeheader()
        writer.writerows(crosswalk)

    exact = sum(
        1
        for row in crosswalk
        if row["resolution_status"] == "EXACT_RESOLVED"
    )

    semantic = sum(
        1
        for row in crosswalk
        if row["resolution_status"] == "SEMANTIC_REVIEW"
    )

    provisional = sum(
        1
        for row in crosswalk
        if row["resolution_status"] == "PROVISIONAL_RAW"
    )

    print(f"\nRaw skill strings: {len(crosswalk)}")
    print(f"Exact resolved: {exact}")
    print(f"Semantic review: {semantic}")
    print(f"Provisional raw: {provisional}")

    print("\nOperational coverage:")
    print(
        f"  Ready: "
        f"{exact + provisional}"
    )
    print(
        f"  Review: "
        f"{semantic}"
    )

    print("\nTop 20 provisional skills by job demand:")
    print("-" * 80)

    provisional_rows = [
        row
        for row in crosswalk
        if row["resolution_status"] == "PROVISIONAL_RAW"
    ]

    provisional_rows.sort(
        key=lambda row: (
            -int(row["job_demand_count"]),
            row["raw_skill"].lower(),
        )
    )

    for i, row in enumerate(provisional_rows[:20], start=1):
        print(
            f"{i:2}. "
            f"{row['raw_skill']} | "
            f"jobs={row['job_demand_count']} | "
            f"sector={row['top_job_sector']} | "
            f"id={row['operational_skill_id']}"
        )

    print(
        f"\nCrosswalk written to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
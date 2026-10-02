from pathlib import Path
import csv

from src.skill_normalizer import normalize_skill


INPUT_PATH = Path("data/processed/skill_inventory.csv")
OUTPUT_PATH = Path("data/processed/skill_normalization_audit.csv")


def load_inventory():
    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def main():
    print("=" * 80)
    print("SkillSync - Skill Normalization Audit")
    print("=" * 80)

    rows = load_inventory()

    audit_rows = []

    for row in rows:
        raw_skill = row["raw_skill"]

        result = normalize_skill(raw_skill)

        method = result.method

        if method == "exact_alias":
            review_status = "AUTO_ACCEPT"

        elif method == "semantic_candidate":
            review_status = "REVIEW_REQUIRED"

        else:
            review_status = "NEW_TAXONOMY_REQUIRED"

        audit_rows.append(
            {
                "raw_skill": raw_skill,
                "job_demand_count": row["job_demand_count"],
                "training_taught_count": row["training_taught_count"],
                "training_gap_count": row["training_gap_count"],
                "canonical_skill": result.canonical_skill or "",
                "skill_id": result.skill_id or "",
                "skill_family": result.skill_family or "",
                "sector": result.sector or "",
                "method": method,
                "confidence": f"{result.confidence:.4f}",
                "review_status": review_status,
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

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
                "canonical_skill",
                "skill_id",
                "skill_family",
                "sector",
                "method",
                "confidence",
                "review_status",
            ],
        )

        writer.writeheader()
        writer.writerows(audit_rows)

    auto = sum(
        1 for r in audit_rows
        if r["review_status"] == "AUTO_ACCEPT"
    )

    review = sum(
        1 for r in audit_rows
        if r["review_status"] == "REVIEW_REQUIRED"
    )

    new_taxonomy = sum(
        1 for r in audit_rows
        if r["review_status"] == "NEW_TAXONOMY_REQUIRED"
    )

    print(f"\nRaw skill strings: {len(audit_rows)}")
    print(f"Exact matches: {auto}")
    print(f"Semantic candidates: {review}")
    print(f"Needs new taxonomy entry: {new_taxonomy}")

    print("\nHighest-demand skills requiring review:")
    print("-" * 80)

    needs_attention = [
        r
        for r in audit_rows
        if r["review_status"] != "AUTO_ACCEPT"
    ]

    needs_attention.sort(
        key=lambda r: (
            -int(r["job_demand_count"]),
            r["raw_skill"].lower(),
        )
    )

    for i, row in enumerate(needs_attention[:50], start=1):
        print(
            f"{i:2}. "
            f"{row['raw_skill']} | "
            f"jobs={row['job_demand_count']} | "
            f"method={row['method']} | "
            f"candidate={row['canonical_skill'] or 'NONE'} | "
            f"confidence={row['confidence']} | "
            f"status={row['review_status']}"
        )

    print(
        f"\nAudit written to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
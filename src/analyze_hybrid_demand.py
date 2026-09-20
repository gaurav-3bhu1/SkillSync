from src.data_loader import load_jobs, load_skills
from src.hybrid_skill_extractor import HybridSkillExtractor
from src.hybrid_job_skill_mapper import (
    build_hybrid_job_skill_mapping,
)
from src.demand_engine import calculate_filtered_demand


def main():

    jobs = load_jobs()
    skills = load_skills()

    extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
        semantic_top_k=3,
    )

    mapping = build_hybrid_job_skill_mapping(
        jobs,
        extractor,
    )

    output_path = (
        "data/processed/"
        "job_skill_mapping_hybrid.csv"
    )

    mapping.to_csv(
        output_path,
        index=False,
    )

    print("=" * 70)
    print("SkillSync - Hybrid Demand Analysis")
    print("=" * 70)

    print(
        f"\nJobs analyzed: "
        f"{jobs['job_id'].nunique()}"
    )

    print(
        f"Job-skill rows: "
        f"{len(mapping)}"
    )

    semantic_rows = mapping[
        mapping["source"] == "semantic"
    ]

    print(
        f"Semantic skill additions: "
        f"{len(semantic_rows)}"
    )

    print("\nSemantic additions:")

    if semantic_rows.empty:

        print("  None")

    else:

        print(
            semantic_rows[
                [
                    "job_id",
                    "title",
                    "skill",
                    "confidence",
                ]
            ].to_string(index=False)
        )

    print("\n" + "=" * 70)
    print("BACKEND DEVELOPER - PUNE")
    print("=" * 70)

    demand = calculate_filtered_demand(
        mapping,
        role="Backend Developer",
        location="Pune",
    )

    if demand.empty:

        print("No matching jobs found.")

    else:

        print(
            demand.to_string(index=False)
        )

    print(
        f"\nSaved hybrid mapping to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()
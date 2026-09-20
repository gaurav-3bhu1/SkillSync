from src.data_loader import load_jobs, load_skills
from src.skill_extractor import SkillExtractor
from src.hybrid_skill_extractor import HybridSkillExtractor


def main():

    jobs = load_jobs()
    skills = load_skills()

    exact_extractor = SkillExtractor(skills)

    hybrid_extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
        semantic_top_k=3,
    )

    total_jobs = 0
    jobs_with_semantic_additions = 0
    total_semantic_additions = 0

    print("=" * 80)
    print("SkillSync - Hybrid Semantic Audit")
    print("=" * 80)

    for _, job in jobs.iterrows():

        total_jobs += 1

        text = (
            str(job["title"])
            + ". "
            + str(job["description"])
        )

        exact_skills = set(
            exact_extractor.extract(text)
        )

        hybrid_results = (
            hybrid_extractor.extract_with_metadata(text)
        )

        semantic_additions = [
            item
            for item in hybrid_results
            if (
                item["source"] == "semantic"
                and item["skill"] not in exact_skills
            )
        ]

        if not semantic_additions:
            continue

        jobs_with_semantic_additions += 1
        total_semantic_additions += len(
            semantic_additions
        )

        print("\n" + "-" * 80)

        print(
            f"Job ID: {job['job_id']}"
        )

        print(
            f"Title: {job['title']}"
        )

        print(
            f"Location: {job['location']}"
        )

        print("\nExact skills:")

        if exact_skills:
            print(
                "  "
                + ", ".join(
                    sorted(exact_skills)
                )
            )
        else:
            print("  None")

        print("\nSemantic additions:")

        for item in semantic_additions:
            print(
                f"  {item['skill']:<25}"
                f"score={item['confidence']:.4f}"
            )

    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)

    print(
        f"Total jobs analyzed: "
        f"{total_jobs}"
    )

    print(
        f"Jobs with semantic additions: "
        f"{jobs_with_semantic_additions}"
    )

    print(
        f"Total semantic additions: "
        f"{total_semantic_additions}"
    )

    if total_jobs > 0:
        percentage = (
            jobs_with_semantic_additions
            / total_jobs
            * 100
        )
    else:
        percentage = 0.0

    print(
        f"Jobs affected: "
        f"{percentage:.2f}%"
    )


if __name__ == "__main__":
    main()
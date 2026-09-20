from src.data_loader import load_jobs, load_skills
from src.hybrid_skill_extractor import HybridSkillExtractor


def main():

    jobs = load_jobs()
    skills = load_skills()

    extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
        semantic_top_k=3,
    )

    print("=" * 70)
    print("SkillSync - Hybrid Skill Extraction")
    print("=" * 70)

    for _, job in jobs.head(10).iterrows():

        text = (
            str(job["title"])
            + ". "
            + str(job["description"])
        )

        results = extractor.extract_with_metadata(
            text
        )

        print("\n" + "-" * 70)

        print(
            f"Job ID: {job['job_id']}"
        )

        print(
            f"Title: {job['title']}"
        )

        print(
            f"Location: {job['location']}"
        )

        print("\nExtracted skills:")

        for result in results:

            print(
                f"  {result['skill']:<25}"
                f"{result['source']:<10}"
                f"{result['confidence']:.4f}"
            )


if __name__ == "__main__":
    main()
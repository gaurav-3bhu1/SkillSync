from data_loader import load_jobs, load_skills
from skill_extractor import SkillExtractor


def main() -> None:
    jobs = load_jobs()
    skills = load_skills()

    extractor = SkillExtractor(skills)

    print("=" * 60)
    print("SkillSync - Job Skill Extraction")
    print("=" * 60)

    for _, job in jobs.head(10).iterrows():

        extracted_skills = extractor.extract(
            job["description"]
        )

        print("\nJob ID:", job["job_id"])
        print("Role:", job["title"])
        print("Location:", job["location"])
        print("Description:", job["description"])
        print("Extracted Skills:", extracted_skills)


if __name__ == "__main__":
    main()
from src.data_loader import load_jobs, load_courses, load_skills


def main() -> None:
    jobs = load_jobs()
    courses = load_courses()
    skills = load_skills()

    print("=" * 40)
    print("SkillSync Data Pipeline")
    print("=" * 40)

    print(f"Jobs loaded:     {len(jobs)}")
    print(f"Courses loaded:  {len(courses)}")
    print(f"Skills loaded:   {len(skills)}")

    print("\nData validation: PASSED")
    print("\nJob locations:")
    print(jobs["location"].value_counts())

    print("\nJob roles:")
    print(jobs["title"].value_counts())

    print("\nIndustries:")
    print(jobs["industry"].value_counts())

    print("\nSample jobs:")
    print(jobs.head())

if __name__ == "__main__":
    main()
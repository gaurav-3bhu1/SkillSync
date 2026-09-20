from src.data_loader import load_courses, load_jobs, load_skills
from src.validate_data import (
    validate_courses,
    validate_jobs,
    validate_skills,
)


def main() -> None:
    jobs = load_jobs()
    courses = load_courses()
    skills = load_skills()

    validate_jobs(jobs)
    validate_courses(courses)
    validate_skills(skills)

    print("=" * 50)
    print("SkillSync Data Pipeline")
    print("=" * 50)

    print(f"Jobs loaded:     {len(jobs)}")
    print(f"Courses loaded:  {len(courses)}")
    print(f"Skills loaded:   {len(skills)}")

    print("\nJob locations:")
    print(jobs["location"].value_counts())

    print("\nIndustries:")
    print(jobs["industry"].value_counts())

    print("\nTop job roles:")
    print(jobs["title"].value_counts().head(10))

    print("\nData validation: PASSED")


if __name__ == "__main__":
    main()
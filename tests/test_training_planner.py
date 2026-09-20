import pandas as pd

from src.training_planner import (
    recommend_courses_for_location,
    build_location_training_plan,
)


def build_jobs():

    return pd.DataFrame(
        [
            {
                "job_id": "J001",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Java",
            },
            {
                "job_id": "J001",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Docker",
            },
            {
                "job_id": "J002",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Java",
            },
            {
                "job_id": "J002",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Spring Boot",
            },
            {
                "job_id": "J003",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "AWS",
            },
        ]
    )


def build_courses():

    return pd.DataFrame(
        [
            {
                "course_id": "C001",
                "course_name": "Java Backend Development",
                "provider": "Test Academy",
                "location": "Pune",
                "description": "Backend development",
                "skills": "Java;SQL;PostgreSQL",
            },
            {
                "course_id": "C002",
                "course_name": "Cloud and DevOps",
                "provider": "Test Academy",
                "location": "Pune",
                "description": "Cloud deployment",
                "skills": "Docker;AWS;Linux",
            },
        ]
    )


def test_recommend_courses():

    jobs = build_jobs()
    courses = build_courses()

    result = recommend_courses_for_location(
        jobs,
        courses,
        "Pune",
    )

    print("\nRecommended courses:")
    print(result)

    assert not result.empty

    assert "C002" in set(
        result["course_id"]
    )


def test_build_training_plan():

    jobs = build_jobs()
    courses = build_courses()

    plan = build_location_training_plan(
        jobs,
        courses,
        "Pune",
    )

    assert plan["location"] == "Pune"
    assert not plan[
        "skill_priorities"
    ].empty

    assert not plan[
        "recommended_courses"
    ].empty


if __name__ == "__main__":

    test_recommend_courses()
    test_build_training_plan()

    print(
        "\nTraining planner tests passed."
    )
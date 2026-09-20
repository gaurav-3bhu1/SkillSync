import pandas as pd

from src.district_planner import (
    build_district_role_profile,
    build_district_skill_profile,
    build_training_priorities,
    compare_districts,
)


def build_test_jobs():

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
                "role": "Data Analyst",
                "location": "Mumbai",
                "skill": "Python",
            },
            {
                "job_id": "J004",
                "role": "Data Analyst",
                "location": "Mumbai",
                "skill": "Python",
            },
        ]
    )


def build_test_courses():

    return pd.DataFrame(
        [
            {
                "course_id": "C001",
                "course_name": "Java Backend Development",
                "provider": "Test Academy",
                "location": "Pune",
                "description": "Backend course",
                "skills": "Java;SQL;PostgreSQL",
            },
            {
                "course_id": "C002",
                "course_name": "DevOps Fundamentals",
                "provider": "Test Academy",
                "location": "Pune",
                "description": "DevOps course",
                "skills": "Docker;AWS;Linux",
            },
        ]
    )


def test_district_skill_profile():

    jobs = build_test_jobs()

    result = build_district_skill_profile(
        jobs,
        "Pune",
    )

    print("\nDistrict skill profile:")
    print(result)

    assert not result.empty

    assert result.iloc[0]["skill"] == "Java"
    assert result.iloc[0]["job_count"] == 2


def test_district_role_profile():

    jobs = build_test_jobs()

    result = build_district_role_profile(
        jobs,
        "Pune",
    )

    print("\nDistrict role profile:")
    print(result)

    assert not result.empty

    assert (
        result.iloc[0]["role"]
        == "Backend Developer"
    )

    assert (
        result.iloc[0]["job_count"]
        == 2
    )


def test_compare_districts():

    jobs = build_test_jobs()

    result = compare_districts(
        jobs,
        ["Pune", "Mumbai"],
    )

    print("\nDistrict comparison:")
    print(result)

    assert set(
        result["location"]
    ) == {
        "Pune",
        "Mumbai",
    }


def test_training_priorities():

    jobs = build_test_jobs()
    courses = build_test_courses()

    result = build_training_priorities(
        jobs,
        courses,
        "Pune",
    )

    print("\nTraining priorities:")
    print(result)

    assert not result.empty

    docker = result[
        result["skill"] == "Docker"
    ].iloc[0]

    assert docker["course_count"] == 1


if __name__ == "__main__":

    test_district_skill_profile()
    test_district_role_profile()
    test_compare_districts()
    test_training_priorities()

    print(
        "\nDistrict planner tests passed."
    )
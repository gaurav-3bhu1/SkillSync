import pandas as pd

from src.alignment_engine import (
    calculate_course_alignment,
    prioritize_skill_gaps,
)


def main() -> None:

    demand = pd.DataFrame(
        [
            {
                "skill": "Java",
                "job_count": 8,
                "demand_percentage": 80.0,
            },
            {
                "skill": "Spring Boot",
                "job_count": 6,
                "demand_percentage": 60.0,
            },
            {
                "skill": "Docker",
                "job_count": 5,
                "demand_percentage": 50.0,
            },
            {
                "skill": "SQL",
                "job_count": 4,
                "demand_percentage": 40.0,
            },
        ]
    )

    course_skills = [
        "Java",
        "SQL",
    ]

    result = calculate_course_alignment(
        course_skills,
        demand,
    )

    print("\nAlignment result:")
    print(result)

    assert result["covered_skills"] == [
        "Java",
        "SQL",
    ]

    assert set(result["missing_skills"]) == {
        "Spring Boot",
        "Docker",
    }

    gaps = prioritize_skill_gaps(
        result["missing_skills"],
        demand,
    )

    print("\nSkill gaps:")
    print(gaps)

    assert gaps.iloc[0]["skill"] == "Spring Boot"
    assert gaps.iloc[0]["priority"] == "HIGH"

    print("\nAlignment engine tests passed.")


if __name__ == "__main__":
    main()
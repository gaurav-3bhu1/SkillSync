import pandas as pd

from src.course_skill_mapper import build_course_skill_mapping


def main() -> None:

    courses = pd.DataFrame(
        [
            {
                "course_id": "C001",
                "course_name": "Java Backend Development",
                "provider": "Test Academy",
                "location": "Pune",
                "description": "Backend development",
                "skills": "Java;SQL;PostgreSQL",
            }
        ]
    )

    result = build_course_skill_mapping(courses)

    print(result)

    assert len(result) == 3

    assert set(result["skill"]) == {
        "Java",
        "SQL",
        "PostgreSQL",
    }

    print("\nCourse skill mapping tests passed.")


if __name__ == "__main__":
    main()
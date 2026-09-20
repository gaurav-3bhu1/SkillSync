from pathlib import Path
import sys

import pandas as pd

# Allow importing from src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.skill_extractor import SkillExtractor


def load_test_skills() -> pd.DataFrame:
    path = PROJECT_ROOT / "data" / "raw" / "skills.csv"

    return pd.read_csv(path)


def main() -> None:
    skills = load_test_skills()

    extractor = SkillExtractor(skills)

    test_cases = [
        (
            "Looking for a Java developer with SpringBoot, "
            "Postgres, Docker and AWS.",
            ["Java", "Spring Boot", "PostgreSQL", "Docker", "AWS"],
        ),
        (
            "Frontend developer with ReactJS, JavaScript, HTML and CSS.",
            ["React", "JavaScript", "HTML", "CSS"],
        ),
        (
            "Backend developer using Node.js, REST API, MongoDB and Git.",
            ["Node.js", "REST API", "MongoDB", "Git"],
        ),
    ]

    for text, expected in test_cases:

        actual = extractor.extract(text)

        print("\nTEXT:")
        print(text)

        print("\nEXPECTED:")
        print(expected)

        print("\nACTUAL:")
        print(actual)

        print("\nMATCH:")
        print(set(actual) == set(expected))


if __name__ == "__main__":
    main()
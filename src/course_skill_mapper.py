from __future__ import annotations

from typing import List

import pandas as pd


def build_course_skill_mapping(
    courses: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert the semicolon-separated skills stored in courses.csv
    into a long-format course-skill table.

    Example:

    C001 | Java Backend Development | Java
    C001 | Java Backend Development | SQL
    C001 | Java Backend Development | PostgreSQL
    """

    rows: List[dict] = []

    for _, course in courses.iterrows():

        raw_skills = str(course["skills"])

        skills = [
            skill.strip()
            for skill in raw_skills.split(";")
            if skill.strip()
        ]

        for skill in skills:
            rows.append(
                {
                    "course_id": course["course_id"],
                    "course_name": course["course_name"],
                    "provider": course["provider"],
                    "location": course["location"],
                    "skill": skill,
                }
            )

    return pd.DataFrame(rows)
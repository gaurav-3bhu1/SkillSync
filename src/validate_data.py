from typing import Iterable

import pandas as pd


def validate_no_empty(
    df: pd.DataFrame,
    columns: Iterable[str],
    dataset_name: str,
) -> None:
    errors = []

    for column in columns:
        if df[column].isna().any():
            errors.append(f"{dataset_name}: {column} contains missing values.")

        if df[column].astype(str).str.strip().eq("").any():
            errors.append(f"{dataset_name}: {column} contains empty strings.")

    if errors:
        raise ValueError("\n".join(errors))


def validate_unique(
    df: pd.DataFrame,
    column: str,
    dataset_name: str,
) -> None:
    if df[column].duplicated().any():
        duplicates = df.loc[df[column].duplicated(), column].tolist()
        raise ValueError(
            f"{dataset_name}: duplicate {column} values found: {duplicates}"
        )


def validate_jobs(jobs: pd.DataFrame) -> None:
    validate_no_empty(
        jobs,
        [
            "job_id",
            "title",
            "location",
            "industry",
            "description",
            "posted_date",
        ],
        "jobs",
    )

    validate_unique(jobs, "job_id", "jobs")


def validate_courses(courses: pd.DataFrame) -> None:
    validate_no_empty(
        courses,
        [
            "course_id",
            "course_name",
            "provider",
            "location",
            "description",
            "skills",
        ],
        "courses",
    )

    validate_unique(courses, "course_id", "courses")


def validate_skills(skills: pd.DataFrame) -> None:
    validate_no_empty(
        skills,
        [
            "skill_id",
            "skill_name",
            "category",
            "aliases",
        ],
        "skills",
    )

    validate_unique(skills, "skill_id", "skills")
    validate_unique(skills, "skill_name", "skills")
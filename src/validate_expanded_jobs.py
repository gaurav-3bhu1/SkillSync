from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_loader import load_skills
from src.role_normalizer import normalize_role
from src.skill_extractor import SkillExtractor
from src.job_skill_mapper import build_job_skill_mapping


BASE_DIR = Path(__file__).resolve().parent.parent

JOBS_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "jobs_expanded.csv"
)


def main():

    print("=" * 70)
    print("SkillSync - Expanded Dataset Validation")
    print("=" * 70)

    if not JOBS_PATH.exists():
        raise FileNotFoundError(
            f"Missing file: {JOBS_PATH}"
        )

    jobs = pd.read_csv(
        JOBS_PATH
    )

    required_columns = {
        "job_id",
        "title",
        "location",
        "industry",
        "description",
        "posted_date",
    }

    missing_columns = (
        required_columns
        - set(jobs.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing columns: "
            f"{sorted(missing_columns)}"
        )

    print(
        f"\nTotal jobs: {len(jobs)}"
    )

    # ------------------------------------------------------
    # ID VALIDATION
    # ------------------------------------------------------

    duplicate_ids = jobs[
        jobs["job_id"].duplicated(
            keep=False
        )
    ]

    print(
        f"Duplicate job IDs: "
        f"{len(duplicate_ids)}"
    )

    if not duplicate_ids.empty:
        raise ValueError(
            "Duplicate job IDs detected."
        )

    # ------------------------------------------------------
    # MISSING VALUES
    # ------------------------------------------------------

    missing_counts = (
        jobs[
            [
                "job_id",
                "title",
                "location",
                "industry",
                "description",
                "posted_date",
            ]
        ]
        .isna()
        .sum()
    )

    print("\nMissing values:")
    print(
        missing_counts.to_string()
    )

    if missing_counts.sum() > 0:
        raise ValueError(
            "Missing values detected."
        )

    # ------------------------------------------------------
    # DATE VALIDATION
    # ------------------------------------------------------

    jobs["posted_date"] = pd.to_datetime(
        jobs["posted_date"],
        errors="coerce",
    )

    if jobs["posted_date"].isna().any():
        raise ValueError(
            "Invalid posted_date values found."
        )

    print(
        f"\nDate range: "
        f"{jobs['posted_date'].min().date()} "
        f"to "
        f"{jobs['posted_date'].max().date()}"
    )

    # ------------------------------------------------------
    # LOCATION DISTRIBUTION
    # ------------------------------------------------------

    print(
        "\nJobs by location:"
    )

    print(
        jobs["location"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # ------------------------------------------------------
    # CANONICAL ROLE DISTRIBUTION
    # ------------------------------------------------------

    jobs["canonical_role"] = (
        jobs["title"]
        .apply(normalize_role)
    )

    print(
        "\nJobs by canonical role:"
    )

    print(
        jobs["canonical_role"]
        .value_counts()
        .to_string()
    )

    # ------------------------------------------------------
    # MONTH DISTRIBUTION
    # ------------------------------------------------------

    print(
        "\nJobs by month:"
    )

    print(
        jobs["posted_date"]
        .dt.to_period("M")
        .value_counts()
        .sort_index()
        .to_string()
    )

    # ------------------------------------------------------
    # SKILL EXTRACTION COVERAGE
    # ------------------------------------------------------

    skills = load_skills()

    extractor = SkillExtractor(
        skills
    )

    mapping = build_job_skill_mapping(
        jobs.drop(
            columns=["canonical_role"]
        ),
        extractor,
    )

    skill_counts = (
        mapping.groupby("job_id")
        .size()
    )

    print(
        "\nSkill extraction coverage:"
    )

    print(
        f"Jobs with extracted skills: "
        f"{skill_counts.index.nunique()}"
    )

    print(
        f"Minimum skills/job: "
        f"{skill_counts.min()}"
    )

    print(
        f"Average skills/job: "
        f"{skill_counts.mean():.2f}"
    )

    print(
        f"Maximum skills/job: "
        f"{skill_counts.max()}"
    )

    jobs_without_skills = (
        set(jobs["job_id"])
        - set(skill_counts.index)
    )

    if jobs_without_skills:
        raise ValueError(
            "Some jobs produced no extracted skills: "
            f"{sorted(jobs_without_skills)}"
        )

    # ------------------------------------------------------
    # TOP SKILLS
    # ------------------------------------------------------

    print(
        "\nTop extracted skills:"
    )

    print(
        mapping.groupby("skill")["job_id"]
        .nunique()
        .sort_values(
            ascending=False
        )
        .head(20)
        .to_string()
    )

    print(
        "\nDataset validation PASSED."
    )


if __name__ == "__main__":
    main()
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.canonical_schema import (
    JOB_COLUMNS,
    TRAINING_COLUMNS,
)


BASE_DIR = Path(__file__).resolve().parent.parent

EXTERNAL_DIR = (
    BASE_DIR
    / "data"
    / "external"
)

JOBS_PATH = (
    EXTERNAL_DIR
    / "maharashtra_job_market_demand_10k.csv"
)

TRAINING_PATH = (
    EXTERNAL_DIR
    / "maharashtra_iti_courses_supply.csv"
)


# ---------------------------------------------------------
# DISTRICT NORMALIZATION
# ---------------------------------------------------------

DISTRICT_ALIASES = {
    "Aurangabad": "Chhatrapati Sambhaji Nagar",
    "Dharashiv (Osmanabad)": "Dharashiv",
    "Osmanabad": "Dharashiv",
}


def normalize_district(
    value: str,
) -> str:

    value = str(value).strip()

    return DISTRICT_ALIASES.get(
        value,
        value,
    )


# ---------------------------------------------------------
# SKILL PARSING
# ---------------------------------------------------------

def parse_job_skills(
    value: str,
) -> list[str]:
    """
    Job dataset uses:
        skill A | skill B | skill C
    """

    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split("|")
        if item.strip()
    ]


def parse_course_skills(
    value: str,
) -> list[str]:
    """
    ITI dataset uses semicolon-separated skills.
    """

    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split(";")
        if item.strip()
    ]


# ---------------------------------------------------------
# JOB DATA
# ---------------------------------------------------------

def load_external_jobs() -> pd.DataFrame:

    if not JOBS_PATH.exists():
        raise FileNotFoundError(
            f"Missing external jobs file: "
            f"{JOBS_PATH}"
        )

    df = pd.read_csv(
        JOBS_PATH
    )

    required = {
        "job_id",
        "job_title",
        "sector",
        "district",
        "industrial_cluster",
        "required_micro_skills",
        "nsqf_level",
        "proficiency_demanded",
        "experience_required_years",
        "education_required",
        "salary_monthly_inr",
        "company_name",
        "employment_type",
        "posting_source",
        "demand_trend",
        "automation_risk_index",
        "job_description_snippet",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "External job dataset is missing "
            f"columns: {sorted(missing)}"
        )

    return df


def standardize_jobs(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert the external Maharashtra job dataset
    into the canonical SkillSync job schema.

    This function does NOT yet map micro-skills
    into the existing 45-skill taxonomy.
    That will happen in the skill-taxonomy phase.
    """

    result = pd.DataFrame(
        {
            "job_id": df["job_id"],
            "title": df["job_title"],
            "role": df["job_title"],
            "location": df["district"].apply(
                normalize_district
            ),
            "industry": df["sector"],
            "industrial_cluster": (
                df["industrial_cluster"]
            ),
            "description": (
                df["job_description_snippet"]
            ),
            "required_skills": (
                df["required_micro_skills"]
                .apply(parse_job_skills)
            ),
            "nsqf_level": df["nsqf_level"],
            "proficiency": (
                df["proficiency_demanded"]
            ),
            "experience_years": (
                df["experience_required_years"]
            ),
            "education": (
                df["education_required"]
            ),
            "salary_monthly_inr": (
                df["salary_monthly_inr"]
            ),
            "company_name": (
                df["company_name"]
            ),
            "employment_type": (
                df["employment_type"]
            ),
            "posting_source": (
                df["posting_source"]
            ),
            "demand_trend": (
                df["demand_trend"]
            ),
            "automation_risk_index": (
                df["automation_risk_index"]
            ),
        }
    )

    return result[
        JOB_COLUMNS
    ]


# ---------------------------------------------------------
# TRAINING SUPPLY
# ---------------------------------------------------------

def load_external_training_supply() -> pd.DataFrame:

    if not TRAINING_PATH.exists():
        raise FileNotFoundError(
            f"Missing ITI supply file: "
            f"{TRAINING_PATH}"
        )

    df = pd.read_csv(
        TRAINING_PATH
    )

    required = {
        "iti_id",
        "iti_name",
        "district",
        "industrial_cluster",
        "tier",
        "iti_type",
        "course_name",
        "sector",
        "nsqf_level",
        "duration_months",
        "annual_intake_seats",
        "placement_rate_pct",
        "skills_taught",
        "skills_gap",
        "demand_alignment",
        "mismatch_flag",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "ITI supply dataset is missing "
            f"columns: {sorted(missing)}"
        )

    return df


def standardize_training_supply(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert external ITI records into the
    canonical SkillSync training schema.
    """

    result = pd.DataFrame(
        {
            "iti_id": df["iti_id"],
            "iti_name": df["iti_name"],
            "location": df["district"].apply(
                normalize_district
            ),
            "industrial_cluster": (
                df["industrial_cluster"]
            ),
            "tier": df["tier"],
            "iti_type": df["iti_type"],
            "course_name": (
                df["course_name"]
            ),
            "industry": df["sector"],
            "nsqf_level": (
                df["nsqf_level"]
            ),
            "duration_months": (
                df["duration_months"]
            ),
            "annual_intake_seats": (
                df["annual_intake_seats"]
            ),
            "placement_rate_pct": (
                df["placement_rate_pct"]
            ),
            "skills_taught": (
                df["skills_taught"]
                .apply(parse_course_skills)
            ),
            "skills_gap": (
                df["skills_gap"]
                .apply(parse_course_skills)
            ),
            "demand_alignment": (
                df["demand_alignment"]
            ),
            "mismatch_flag": (
                df["mismatch_flag"]
            ),
        }
    )

    return result[
        TRAINING_COLUMNS
    ]
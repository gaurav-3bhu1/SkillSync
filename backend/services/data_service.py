from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"


def _load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {path}"
        )

    return pd.read_csv(path)


def load_job_skills() -> pd.DataFrame:
    return _load_csv("job_skill_normalized.csv")


def load_training_skills() -> pd.DataFrame:
    return _load_csv("training_skill_normalized.csv")


def load_demand_supply() -> pd.DataFrame:
    return _load_csv("skill_demand_supply.csv")


def load_district_alignment() -> pd.DataFrame:
    return _load_csv("district_skill_alignment.csv")


def load_skill_inventory() -> pd.DataFrame:
    return _load_csv("skill_inventory.csv")


def get_market_summary(
    district: str | None = None,
    sector: str | None = None,
) -> dict:

    jobs = load_job_skills()

    if district:
        jobs = jobs[
            jobs["location"].astype(str).str.lower()
            == district.lower()
        ]

    if sector and "sector" in jobs.columns:
        jobs = jobs[
            jobs["sector"].astype(str).str.lower()
            == sector.lower()
        ]

    if jobs.empty:
        return {
            "job_count": 0,
            "skill_count": 0,
            "top_skills": [],
        }

    grouped = (
        jobs.groupby("skill")
        .agg(
            job_count=("job_id", "nunique")
        )
        .reset_index()
        .sort_values(
            "job_count",
            ascending=False,
        )
    )

    total_jobs = jobs["job_id"].nunique()

    grouped["demand_percentage"] = (
        grouped["job_count"]
        / total_jobs
        * 100
    )

    return {
        "job_count": int(total_jobs),
        "skill_count": int(grouped["skill"].nunique()),
        "top_skills": grouped.head(20).to_dict(
            orient="records"
        ),
    }


def get_districts() -> list[str]:
    jobs = load_job_skills()

    return sorted(
        jobs["location"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


def get_sectors() -> list[str]:
    jobs = load_job_skills()

    column = (
        "sector"
        if "sector" in jobs.columns
        else "skill_sector"
    )

    return sorted(
        jobs[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
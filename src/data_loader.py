from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"


def load_jobs() -> pd.DataFrame:
    path = DATA_DIR / "jobs.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    required_columns = {
        "job_id",
        "title",
        "location",
        "industry",
        "description",
        "posted_date",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"jobs.csv is missing columns: {sorted(missing)}")

    return df


def load_courses() -> pd.DataFrame:
    path = DATA_DIR / "courses.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    required_columns = {
        "course_id",
        "course_name",
        "provider",
        "location",
        "description",
        "skills",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"courses.csv is missing columns: {sorted(missing)}")

    return df


def load_skills() -> pd.DataFrame:
    path = DATA_DIR / "skills.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    required_columns = {
        "skill_id",
        "skill_name",
        "category",
        "aliases",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"skills.csv is missing columns: {sorted(missing)}")

    return df
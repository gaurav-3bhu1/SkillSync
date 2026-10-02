from fastapi import APIRouter, Query
import math

from backend.services.data_service import load_demand_supply


router = APIRouter(
    prefix="/api/skills",
    tags=["Skills"],
)


def clean_value(value):
    if value is None:
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

    return value


@router.get("/trends")
def skill_trends(
    sector: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    df = load_demand_supply()

    if sector:
        df = df[
            df["skill_sector"].astype(str).str.lower()
            == sector.lower()
        ]

    if df.empty:
        return {
            "skills": []
        }

    result = (
        df.sort_values(
            "demand_job_count",
            ascending=False,
        )
        .head(limit)
    )

    columns = [
        "skill_id",
        "skill",
        "skill_family",
        "skill_sector",
        "demand_job_count",
        "demand_role_count",
        "demand_district_count",
        "avg_salary_monthly_inr",
        "emerging_share",
        "stable_share",
        "declining_share",
        "skill_demand_trend_signal",
        "training_program_count",
        "training_iti_count",
        "allocated_skill_seats",
        "effective_placed_seat_proxy",
        "training_capacity_signal",
    ]

    available_columns = [
        column
        for column in columns
        if column in result.columns
    ]

    result = result[available_columns]

    records = result.to_dict(
        orient="records"
    )

    # Convert pandas NaN / infinity values
    # into JSON-safe null values.
    cleaned_records = []

    for record in records:
        cleaned_record = {
            key: clean_value(value)
            for key, value in record.items()
        }

        cleaned_records.append(
            cleaned_record
        )

    return {
        "skills": cleaned_records
    }
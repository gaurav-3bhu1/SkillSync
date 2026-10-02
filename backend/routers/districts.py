from fastapi import APIRouter, Query, HTTPException
import pandas as pd

from backend.services.data_service import (
    load_district_alignment,
)

router = APIRouter(
    prefix="/api/districts",
    tags=["District Intelligence"],
)


def clean_value(value):
    """Convert pandas/NumPy values into JSON-safe values."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


@router.get("/{district}")
def district_intelligence(
    district: str,
    limit: int = Query(default=20, ge=1, le=100),
):
    df = load_district_alignment()

    matches = df[
        df["location"]
        .astype(str)
        .str.strip()
        .str.lower()
        == district.strip().lower()
    ].copy()

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No district data found for '{district}'.",
        )

    matches = matches.sort_values(
        by=[
            "high_demand_within_district",
            "demand_job_count",
            "skill",
        ],
        ascending=[False, False, True],
    )

    skills = []

    for _, row in matches.head(limit).iterrows():
        skills.append(
            {
                "skill_id": clean_value(row["skill_id"]),
                "skill": clean_value(row["skill"]),
                "skill_family": clean_value(
                    row["skill_family"]
                ),
                "skill_sector": clean_value(
                    row["skill_sector"]
                ),
                "demand_job_count": clean_value(
                    row["demand_job_count"]
                ),
                "district_total_jobs": clean_value(
                    row["district_total_jobs"]
                ),
                "demand_share_pct": clean_value(
                    row[
                        "skill_demand_share_of_district_jobs"
                    ]
                ),
                "trend_signal": clean_value(
                    row["district_skill_trend_signal"]
                ),
                "training_program_count": clean_value(
                    row["training_program_count"]
                ),
                "training_iti_count": clean_value(
                    row["training_iti_count"]
                ),
                "allocated_skill_seats": clean_value(
                    row["allocated_skill_seats"]
                ),
                "effective_placed_seat_proxy": clean_value(
                    row["effective_placed_seat_proxy"]
                ),
                "supply_status": clean_value(
                    row["supply_status"]
                ),
                "priority_band": clean_value(
                    row["priority_band"]
                ),
            }
        )

    return {
        "district": district,
        "total_skills": int(len(matches)),
        "skills": skills,
    }
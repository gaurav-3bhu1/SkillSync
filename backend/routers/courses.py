from fastapi import APIRouter, Query

from backend.schemas.courses import CourseAlignmentResponse
from backend.services.data_service import (
    load_training_skills,
    load_demand_supply,
    load_district_alignment,
)


router = APIRouter(
    prefix="/api/courses",
    tags=["Course Alignment"],
)


def clean_value(value):
    if value is None:
        return None

    try:
        if value != value:
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        return value.item()

    return value


@router.get(
    "/alignment",
    response_model=CourseAlignmentResponse,
)
def course_alignment(
    district: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    training = load_training_skills()
    demand = load_demand_supply()

    # Only rows that actually count as training supply.
    if "counts_as_supply" in training.columns:
        training = training[
            training["counts_as_supply"].astype(bool)
        ].copy()

    if district:
        training = training[
            training["location"]
            .astype(str)
            .str.strip()
            .str.lower()
            == district.strip().lower()
        ].copy()

    if training.empty:
        return {
            "total_courses": 0,
            "courses": [],
        }

    # Keep one record per course + skill.
    course_skills = training[
        [
            "course_name",
            "skill_id",
            "skill",
        ]
    ].drop_duplicates()

    # Demand information for each canonical skill.
    demand_columns = [
        "skill_id",
        "skill",
        "demand_job_count",
        "training_program_count",
        "allocated_skill_seats",
        "training_capacity_signal",
    ]

    demand_lookup = demand[
        [c for c in demand_columns if c in demand.columns]
    ].drop_duplicates("skill_id")

    merged = course_skills.merge(
        demand_lookup,
        on="skill_id",
        how="left",
        suffixes=("", "_demand"),
    )

    # Convert missing demand to zero.
    merged["demand_job_count"] = (
        merged["demand_job_count"]
        .fillna(0)
    )

    # A skill is considered high-demand when it has
    # recorded job demand and belongs to the top demand
    # half of the skills represented in this course.
    course_rows = []

    for course_name, group in merged.groupby(
        "course_name"
    ):
        skills = (
            group["skill"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        demand_values = group[
            "demand_job_count"
        ].astype(float)

        demand_score = float(
            demand_values.sum()
        )

        # Skills with recorded demand.
        high_demand = (
            group[group["demand_job_count"] > 0]
            .sort_values(
                "demand_job_count",
                ascending=False,
            )["skill"]
            .dropna()
            .astype(str)
            .head(5)
            .tolist()
        )

        # Skills with no recorded job demand.
        gaps = (
            group[group["demand_job_count"] <= 0]
            ["skill"]
            .dropna()
            .astype(str)
            .head(5)
            .tolist()
        )

        course_training = training[
            training["course_name"]
            == course_name
        ]

        iti_count = int(
            course_training["iti_id"]
            .nunique()
            if "iti_id" in course_training.columns
            else course_training["iti_name"]
            .nunique()
        )

        if "placement_rate_pct" in course_training.columns:
            placement = course_training[
                "placement_rate_pct"
            ].astype(float)

            average_placement = (
                float(placement.mean())
                if not placement.empty
                else None
            )
        else:
            average_placement = None

        allocated_seats = 0.0

        if "allocated_skill_seats" in group.columns:
            allocated_seats = float(
                group["allocated_skill_seats"]
                .fillna(0)
                .sum()
            )

        course_rows.append(
            {
                "course_name": str(course_name),
                "iti_count": iti_count,
                "skill_count": len(skills),
                "demand_score": demand_score,
                "average_placement_rate_pct":
                    clean_value(average_placement),
                "allocated_skill_seats":
                    allocated_seats,
                "high_demand_skills":
                    high_demand,
                "skill_gaps":
                    gaps,
            }
        )

    # Most industry-demand-aligned courses first.
    course_rows.sort(
        key=lambda x: x["demand_score"],
        reverse=True,
    )

    return {
        "total_courses": len(course_rows),
        "courses": course_rows[:limit],
    }
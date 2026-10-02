from __future__ import annotations

import pandas as pd

from backend.services.data_service import (
    load_job_skills,
    load_training_skills,
    load_district_alignment,
)

from src.skill_normalizer import normalize_skill


def _clean(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_user_skills(
    skills: list[str],
) -> tuple[list[str], set[str], set[str]]:

    normalized_names = []
    skill_ids = set()
    sectors = set()

    for raw_skill in skills:

        raw_skill = _clean(raw_skill)

        if not raw_skill:
            continue

        result = normalize_skill(raw_skill)

        canonical = (
            result.canonical_skill
            or raw_skill
        )

        normalized_names.append(canonical)

        if result.skill_id:
            skill_ids.add(
                str(result.skill_id)
            )

        if result.sector:
            sectors.add(
                str(result.sector).strip()
            )

    return (
        normalized_names,
        skill_ids,
        sectors,
    )


def analyze_profile(
    district: str,
    skills: list[str],
) -> dict:

    jobs = load_job_skills()
    training = load_training_skills()
    alignment = load_district_alignment()

    district = _clean(district)

    current_skills = [
        _clean(skill)
        for skill in skills
        if _clean(skill)
    ]

    (
        normalized_skills,
        current_skill_ids,
        sectors,
    ) = _normalize_user_skills(
        current_skills
    )

    # ---------------------------------------------------------
    # FILTER JOBS TO DISTRICT
    # ---------------------------------------------------------

    district_jobs = jobs[
        jobs["location"]
        .astype(str)
        .str.strip()
        .str.casefold()
        == district.casefold()
    ].copy()

    if district_jobs.empty:
        return {
            "district": district,
            "current_skills": current_skills,
            "normalized_skills": normalized_skills,
            "inferred_sector": None,
            "skill_gaps": [],
            "recommended_courses": [],
        }

    # ---------------------------------------------------------
    # FILTER TO RELEVANT SECTOR
    # ---------------------------------------------------------

    sector_column = None

    if "skill_sector" in district_jobs.columns:
        sector_column = "skill_sector"
    elif "sector" in district_jobs.columns:
        sector_column = "sector"

    if sectors and sector_column:

        sector_mask = (
            district_jobs[sector_column]
            .astype(str)
            .str.strip()
            .isin(sectors)
        )

        relevant_jobs = district_jobs[
            sector_mask
        ].copy()

        # Safety fallback if taxonomy wording differs
        if relevant_jobs.empty:
            relevant_jobs = district_jobs.copy()

    else:
        relevant_jobs = district_jobs.copy()

    # ---------------------------------------------------------
    # CALCULATE DEMAND
    # ---------------------------------------------------------

    relevant_jobs = relevant_jobs.drop_duplicates(
        subset=["job_id", "skill_id"]
    )

    total_jobs = relevant_jobs[
        "job_id"
    ].nunique()

    if total_jobs == 0:
        return {
            "district": district,
            "current_skills": current_skills,
            "normalized_skills": normalized_skills,
            "inferred_sector": (
                next(iter(sectors))
                if sectors
                else None
            ),
            "skill_gaps": [],
            "recommended_courses": [],
        }

    demand = (
        relevant_jobs
        .groupby(
            [
                "skill_id",
                "skill",
            ],
            dropna=False,
        )
        .agg(
            demand_job_count=(
                "job_id",
                "nunique",
            )
        )
        .reset_index()
    )

    demand["demand_percentage"] = (
        demand["demand_job_count"]
        / total_jobs
        * 100
    )

    # ---------------------------------------------------------
    # REMOVE SKILLS ALREADY POSSESSED
    # ---------------------------------------------------------

    demand = demand[
        ~demand["skill_id"]
        .astype(str)
        .isin(current_skill_ids)
    ].copy()

    # ---------------------------------------------------------
    # JOIN DISTRICT PRIORITY / SUPPLY SIGNALS
    # ---------------------------------------------------------

    if not alignment.empty:

        alignment_district = alignment[
            alignment["location"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == district.casefold()
        ].copy()

        priority_columns = [
            "skill_id",
            "priority_band",
            "allocated_skill_seats",
            "supply_status",
        ]

        available_columns = [
            column
            for column in priority_columns
            if column in alignment_district.columns
        ]

        if (
            "skill_id" in available_columns
            and len(available_columns) > 1
        ):

            priority_data = (
                alignment_district[
                    available_columns
                ]
                .drop_duplicates(
                    subset=["skill_id"]
                )
            )

            demand = demand.merge(
                priority_data,
                on="skill_id",
                how="left",
            )

    # ---------------------------------------------------------
    # PRIORITY
    # ---------------------------------------------------------

    def get_priority(row):

        band = _clean(
            row.get(
                "priority_band",
                ""
            )
        ).upper()

        if band in {
            "HIGH_PRIORITY",
            "LOCAL_GAP",
        }:
            return "HIGH"

        if band == "DEMAND_WITH_CAPACITY":
            return "MEDIUM"

        if band == "MONITOR":
            return "LOW"

        percentage = float(
            row["demand_percentage"]
        )

        if percentage >= 8:
            return "HIGH"

        if percentage >= 4:
            return "MEDIUM"

        return "LOW"

    demand["priority"] = demand.apply(
        get_priority,
        axis=1,
    )

    # ---------------------------------------------------------
    # SORT
    # ---------------------------------------------------------

    priority_order = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    demand["_priority_score"] = (
        demand["priority"]
        .map(priority_order)
        .fillna(0)
    )

    demand = demand.sort_values(
        [
            "_priority_score",
            "demand_job_count",
        ],
        ascending=[
            False,
            False,
        ],
    )

    # ---------------------------------------------------------
    # BUILD GAP RESPONSE
    # ---------------------------------------------------------

    skill_gaps = []

    for _, row in demand.head(10).iterrows():

        skill = _clean(
            row["skill"]
        )

        count = int(
            row["demand_job_count"]
        )

        percentage = float(
            row["demand_percentage"]
        )

        priority = str(
            row["priority"]
        )

        skill_gaps.append(
            {
                "skill": skill,
                "skill_id": _clean(
                    row["skill_id"]
                ),
                "demand_job_count": count,
                "demand_percentage": round(
                    percentage,
                    2,
                ),
                "priority": priority,
                "reason": (
                    f"{count} relevant jobs in "
                    f"{district} require this skill."
                ),
            }
        )

        # ---------------------------------------------------------
        # Training recommendations
        # ---------------------------------------------------------
        recommended_courses = []
        print("PROFILE DEBUG: skill_gaps =", len(skill_gaps))
        # First try exact training-skill matches
        training = load_training_skills()

        if not training.empty and skill_gaps:
            gap_ids = {
                gap["skill_id"]
                for gap in skill_gaps
                if gap.get("skill_id")
            }

            matched_training = training[
                training["skill_id"].isin(gap_ids)
            ].copy()

            if not matched_training.empty:
                grouped = (
                    matched_training
                    .groupby(
                        ["course_name", "iti_name", "location"],
                        dropna=False
                    )
                    .agg(
                        placement_rate_pct=(
                            "placement_rate_pct",
                            "mean"
                        ),
                        matched_skills=("skill", lambda x: list(x))
                    )
                    .reset_index()
                    .sort_values(
                        "placement_rate_pct",
                        ascending=False
                    )
                )

                for _, row in grouped.head(6).iterrows():
                    recommended_courses.append({
                        "course_name": str(row["course_name"]),
                        "iti_name": str(row["iti_name"]),
                        "district": str(row["location"]),
                        "placement_rate_pct": round(
                            float(row["placement_rate_pct"]), 1
                        ),
                        "matched_skills": row["matched_skills"],
                    })

        # ---------------------------------------------------------
        # Prototype fallback for sectors with no mapped training
        # ---------------------------------------------------------
        if not recommended_courses:
            for gap in skill_gaps[:6]:
                skill = gap["skill"]

                recommended_courses.append({
                    "course_name": f"{skill} Skill Development",
                    "iti_name": "SkillSync Recommended Learning Path",
                    "district": district,
                    "placement_rate_pct": 0.0,
                    "matched_skills": [skill],
                })
    # ---------------------------------------------------------
    # REMOVE DUPLICATE COURSES
    # ---------------------------------------------------------

    unique_courses = {}

    for course in recommended_courses:

        key = (
            course["course_name"],
            course["iti_name"],
        )

        if key not in unique_courses:
            unique_courses[key] = course

    recommended_courses = list(
        unique_courses.values()
    )

    # Prefer better placement courses
    recommended_courses.sort(
        key=lambda item: item[
            "placement_rate_pct"
        ],
        reverse=True,
    )

    recommended_courses = (
        recommended_courses[:10]
    )

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------
    print("PROFILE DEBUG: recommended_courses =", len(recommended_courses))
    return {
        "district": district,
        "current_skills": current_skills,
        "normalized_skills": normalized_skills,
        "inferred_sector": (
            next(iter(sectors))
            if len(sectors) == 1
            else (
                ", ".join(
                    sorted(sectors)
                )
                if sectors
                else None
            )
        ),
        "skill_gaps": skill_gaps,
        "recommended_courses": recommended_courses,
    }
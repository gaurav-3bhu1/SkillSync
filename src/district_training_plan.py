from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


EXPAND_SCORE = 0.65
REVIEW_SCORE = 0.60


def _first_existing(
    df: pd.DataFrame,
    candidates: List[str],
) -> Optional[str]:

    for column in candidates:
        if column in df.columns:
            return column

    return None


def _safe_numeric(
    series: pd.Series,
) -> pd.Series:

    return pd.to_numeric(
        series,
        errors="coerce",
    ).fillna(0.0)


def _normalize_percentage(
    series: pd.Series,
) -> pd.Series:

    values = _safe_numeric(series)

    # Handle both 0-1 and 0-100 representations.
    if not values.empty and values.max() <= 1.0:
        values = values * 100.0

    return values.clip(
        lower=0,
        upper=100,
    )


def _priority_weight(
    priority_band: str,
) -> float:

    weights = {
        "HIGH_PRIORITY": 1.00,
        "LOCAL_GAP": 0.85,
        "DEMAND_WITH_CAPACITY": 0.45,
        "MONITOR": 0.20,
    }

    return weights.get(
        priority_band,
        0.20,
    )


def _supply_weight(
    supply_status: str,
) -> float:

    weights = {
        "NO_RECORDED_TRAINING_SUPPLY": 1.00,
        "VERY_LOW_CAPACITY": 0.90,
        "LOW_CAPACITY": 0.75,
        "MODERATE_CAPACITY": 0.40,
        "ADEQUATE_OR_HIGH_CAPACITY": 0.10,
        "SUPPLY_WITHOUT_RECORDED_DEMAND": 0.00,
    }

    return weights.get(
        supply_status,
        0.20,
    )


def build_district_training_plan(
    alignment: pd.DataFrame,
    training: pd.DataFrame,
    district: Optional[str] = None,
    top_n: int = 10,
) -> Dict:

    if alignment.empty:
        return {
            "district": district,
            "priority_skills": [],
            "courses_to_expand": [],
            "courses_to_review": [],
            "emerging_opportunities": [],
        }

    alignment = alignment.copy()
    training = training.copy()

    if district is not None:

        alignment = alignment[
            alignment["location"].astype(str).str.strip().str.casefold()
            == district.strip().casefold()
        ].copy()

        training_location_column = _first_existing(
            training,
            [
                "location",
                "district",
            ],
        )

        if training_location_column:

            training = training[
                training[
                    training_location_column
                ].astype(str).str.strip().str.casefold()
                == district.strip().casefold()
            ].copy()

    if alignment.empty:

        return {
            "district": district,
            "priority_skills": [],
            "courses_to_expand": [],
            "courses_to_review": [],
            "emerging_opportunities": [],
        }

    # ---------------------------------------------------------
    # Numeric safety
    # ---------------------------------------------------------

    alignment["demand_job_count"] = _safe_numeric(
        alignment["demand_job_count"]
    )

    alignment["allocated_skill_seats"] = _safe_numeric(
        alignment["allocated_skill_seats"]
    )

    if "district_total_jobs" in alignment.columns:
        alignment["district_total_jobs"] = _safe_numeric(
            alignment["district_total_jobs"]
        )
    else:
        alignment["district_total_jobs"] = (
            alignment.groupby("location")[
                "demand_job_count"
            ].transform("sum")
        )

    # ---------------------------------------------------------
    # Demand intensity
    # ---------------------------------------------------------

    alignment["demand_intensity"] = (
        alignment["demand_job_count"]
        /
        alignment["district_total_jobs"].replace(
            0,
            pd.NA,
        )
    ).fillna(0)

    # ---------------------------------------------------------
    # Relative scarcity
    #
    # This is intentionally a signal, not a claim of absolute
    # labour shortage.
    # ---------------------------------------------------------

    alignment["scarcity_score"] = (
        alignment["demand_intensity"]
        /
        (
            alignment["allocated_skill_seats"]
            + 1
        )
    )

    max_scarcity = alignment[
        "scarcity_score"
    ].max()

    if max_scarcity > 0:

        alignment["normalized_scarcity"] = (
            alignment["scarcity_score"]
            /
            max_scarcity
        )

    else:

        alignment["normalized_scarcity"] = 0.0

    alignment["priority_weight"] = (
        alignment["priority_band"]
        .astype(str)
        .map(_priority_weight)
        .fillna(0.20)
    )

    alignment["supply_weight"] = (
        alignment["supply_status"]
        .astype(str)
        .map(_supply_weight)
        .fillna(0.20)
    )

    # ---------------------------------------------------------
    # Action score
    # ---------------------------------------------------------

    alignment["action_score"] = (
        0.40
        * alignment["priority_weight"]
        +
        0.35
        * alignment["normalized_scarcity"]
        +
        0.25
        * alignment["supply_weight"]
    )

    # ---------------------------------------------------------
    # Priority skills
    # ---------------------------------------------------------

    priority = alignment[
        alignment["priority_band"].isin(
            {
                "HIGH_PRIORITY",
                "LOCAL_GAP",
            }
        )
    ].copy()

    priority = priority.sort_values(
        [
            "action_score",
            "demand_job_count",
        ],
        ascending=False,
    )

    priority_skills = []

    for _, row in priority.head(top_n).iterrows():

        skill = str(row["skill_id"])

        priority_skills.append(
            {
                "skill": skill,
                "action_score": round(
                    float(row["action_score"]),
                    3,
                ),
                "demand_jobs": int(
                    row["demand_job_count"]
                ),
                "allocated_training_seats": int(
                    row["allocated_skill_seats"]
                ),
                "priority_band": row[
                    "priority_band"
                ],
                "recommendation": (
                    "Expand or strengthen training capacity."
                ),
                "reason": (
                    f"{skill} shows meaningful observed demand "
                    "with limited local training capacity."
                ),
            }
        )

    # ---------------------------------------------------------
    # Course-level columns
    # ---------------------------------------------------------

    course_id_column = _first_existing(
        training,
        [
            "course_id",
            "course",
            "course_code",
            "iti_id",
        ],
    )

    course_name_column = _first_existing(
        training,
        [
            "course_name",
            "course",
        ],
    )

    skill_column = _first_existing(
        training,
        [
            "skill",
            "skills",
            "skill_id",
        ],
    )

    intake_column = _first_existing(
        training,
        [
            "annual_intake_seats",
            "annual_intake",
            "intake",
            "seats",
        ],
    )

    placement_column = _first_existing(
        training,
        [
            "placement_rate_pct",
            "placement_rate",
            "placement_rate_percent",
        ],
    )

    if (
        course_id_column is None
        or course_name_column is None
        or skill_column is None
    ):

        return {
            "district": district,
            "priority_skills": priority_skills,
            "courses_to_expand": [],
            "courses_to_review": [],
            "emerging_opportunities": [],
        }

    # ---------------------------------------------------------
    # Build alignment lookup by canonical skill ID
    # ---------------------------------------------------------

    skill_lookup = alignment.set_index(
        "skill_id"
    ).to_dict(
        orient="index"
    )

    # Training data may contain either:
    #   skill_id  -> canonical skill identifier
    #   skill     -> human-readable skill name
    #
    # Prefer skill_id when available because the alignment
    # engine operates on canonical skill IDs.

    training_skill_id_column = _first_existing(
        training,
        [
            "skill_id",
            "skill",
        ],
    )

    if training_skill_id_column is None:
        training_skill_id_column = skill_column


    course_rows = []

    for _, row in training.iterrows():

        skill_id = str(
            row[training_skill_id_column]
        ).strip()

        if not skill_id:
            continue

        signal = skill_lookup.get(
            skill_id
        )

        if signal is None:
            continue

        # Prefer human-readable skill name from alignment
        # when available.
        display_skill = signal.get(
            "skill",
            skill_id,
        )

        course_rows.append(
            {
                "course_id": row[
                    course_id_column
                ],
                "course_name": row[
                    course_name_column
                ],
                "skill_id": skill_id,
                "skill": display_skill,
                "action_score": signal[
                    "action_score"
                ],
                "priority_band": signal[
                    "priority_band"
                ],
                "supply_status": signal[
                    "supply_status"
                ],
                "demand_job_count": signal[
                    "demand_job_count"
                ],
            }
        )

    # ---------------------------------------------------------
    # Merge course skills with district signals
    # ---------------------------------------------------------

    course_rows = []

    for _, row in training.iterrows():

        skill = str(
            row[skill_column]
        ).strip()

        if not skill:
            continue

        signal = skill_lookup.get(skill)

        if signal is None:
            continue

        course_rows.append(
            {
                "course_id": row[
                    course_id_column
                ],
                "course_name": row[
                    course_name_column
                ],
                "skill": skill,
                "action_score": signal[
                    "action_score"
                ],
                "priority_band": signal[
                    "priority_band"
                ],
                "supply_status": signal[
                    "supply_status"
                ],
                "demand_job_count": signal[
                    "demand_job_count"
                ],
            }
        )

    course_signals = pd.DataFrame(
        course_rows
    )

    if course_signals.empty:

        return {
            "district": district,
            "priority_skills": priority_skills,
            "courses_to_expand": [],
            "courses_to_review": [],
            "emerging_opportunities": [],
        }

    # ---------------------------------------------------------
    # Aggregate skills -> course
    # ---------------------------------------------------------

    course_grouped = (
        course_signals
        .groupby(
            [
                "course_id",
                "course_name",
            ],
            dropna=False,
        )
        .agg(
            action_score=(
                "action_score",
                "mean",
            ),
            max_action_score=(
                "action_score",
                "max",
            ),
            demand_jobs=(
                "demand_job_count",
                "sum",
            ),
            priority_skills=(
                "skill",
                lambda x: list(
                    dict.fromkeys(x)
                ),
            ),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # Attach placement / intake
    # ---------------------------------------------------------

    course_meta_columns = [
        course_id_column,
        course_name_column,
    ]

    course_meta = training[
        course_meta_columns
        + (
            [intake_column]
            if intake_column
            else []
        )
        + (
            [placement_column]
            if placement_column
            else []
        )
    ].drop_duplicates(
        subset=[
            course_id_column,
            course_name_column,
        ]
    )

    course_grouped = course_grouped.merge(
        course_meta,
        how="left",
        left_on=[
            "course_id",
            "course_name",
        ],
        right_on=[
            course_id_column,
            course_name_column,
        ],
    )

    if placement_column:

        course_grouped[
            "placement_rate"
        ] = _normalize_percentage(
            course_grouped[
                placement_column
            ]
        )

    else:

        course_grouped[
            "placement_rate"
        ] = 0.0

    if intake_column:

        course_grouped[
            "annual_intake"
        ] = _safe_numeric(
            course_grouped[
                intake_column
            ]
        )

    else:

        course_grouped[
            "annual_intake"
        ] = 0.0

    # ---------------------------------------------------------
    # Courses to EXPAND
    #
    # Existing courses serving skills with strong demand and
    # weak/limited capacity.
    # ---------------------------------------------------------

    expand = course_grouped[
        (
            course_grouped[
                "max_action_score"
            ]
            >= EXPAND_SCORE
        )
        &
        (
            course_grouped[
                "demand_jobs"
            ]
            > 0
        )
    ].copy()

    expand["recommendation"] = (
        "Consider expanding or strengthening this course."
    )

    expand["reason"] = (
        "The course covers skills with strong local "
        "demand-alignment signals."
    )

    expand = expand.sort_values(
        [
            "max_action_score",
            "demand_jobs",
        ],
        ascending=False,
    )

    courses_to_expand = []

    for _, row in expand.head(top_n).iterrows():

        courses_to_expand.append(
            {
                "course_id": row[
                    "course_id"
                ],
                "course_name": row[
                    "course_name"
                ],
                "action_score": round(
                    float(
                        row[
                            "max_action_score"
                        ]
                    ),
                    3,
                ),
                "demand_jobs": int(
                    row[
                        "demand_jobs"
                    ]
                ),
                "annual_intake": int(
                    row[
                        "annual_intake"
                    ]
                ),
                "placement_rate": round(
                    float(
                        row[
                            "placement_rate"
                        ]
                    ),
                    2,
                ),
                "recommendation": row[
                    "recommendation"
                ],
                "reason": row[
                    "reason"
                ],
            }
        )

    # ---------------------------------------------------------
    # Courses to REVIEW
    #
    # Important: review != obsolete.
    # ---------------------------------------------------------

    review = course_grouped[
        (
            course_grouped[
                "placement_rate"
            ] < 40
        )
        |
        (
            course_grouped[
                "max_action_score"
            ] < REVIEW_SCORE
        )
    ].copy()

    review = review.sort_values(
        [
            "placement_rate",
            "action_score",
        ],
        ascending=[
            True,
            True,
        ],
    )

    courses_to_review = []

    for _, row in review.head(top_n).iterrows():

        reason_parts = []

        if row[
            "placement_rate"
        ] < 40:

            reason_parts.append(
                "low recorded placement rate"
            )

        if row[
            "max_action_score"
        ] < REVIEW_SCORE:

            reason_parts.append(
                "weak local demand-alignment signal"
            )

        courses_to_review.append(
            {
                "course_id": row[
                    "course_id"
                ],
                "course_name": row[
                    "course_name"
                ],
                "placement_rate": round(
                    float(
                        row[
                            "placement_rate"
                        ]
                    ),
                    2,
                ),
                "recommendation": (
                    "Review course relevance, curriculum "
                    "and capacity before making changes."
                ),
                "reason": "; ".join(
                    reason_parts
                ),
            }
        )

    # ---------------------------------------------------------
    # Emerging opportunities
    #
    # High-demand skills with no/very limited local supply.
    # ---------------------------------------------------------

    emerging = alignment[
        alignment[
            "supply_status"
        ].isin(
            {
                "NO_RECORDED_TRAINING_SUPPLY",
                "VERY_LOW_CAPACITY",
                "LOW_CAPACITY",
            }
        )
        &
        (
            alignment[
                "demand_job_count"
            ] > 0
        )
    ].copy()

    emerging = emerging.sort_values(
        [
            "action_score",
            "demand_job_count",
        ],
        ascending=False,
    )

    emerging_opportunities = []

    for _, row in emerging.head(top_n).iterrows():

        emerging_opportunities.append(
            {
                "skill": str(
                    row["skill_id"]
                ),
                "demand_jobs": int(
                    row[
                        "demand_job_count"
                    ]
                ),
                "allocated_training_seats": int(
                    row[
                        "allocated_skill_seats"
                    ]
                ),
                "recommendation": (
                    "Consider developing a new module, "
                    "course or upskilling pathway."
                ),
                "reason": (
                    "Observed local demand exists while "
                    "recorded training capacity is limited."
                ),
            }
        )

    return {
        "district": district,
        "priority_skills": priority_skills,
        "courses_to_expand": courses_to_expand,
        "courses_to_review": courses_to_review,
        "emerging_opportunities": emerging_opportunities,
    }


def save_training_plan(
    plan: Dict,
    path: str,
) -> None:

    rows = []

    for item in plan[
        "priority_skills"
    ]:

        rows.append(
            {
                "district": plan["district"],
                "action_type": "PRIORITY_SKILL",
                **item,
            }
        )

    for item in plan[
        "courses_to_expand"
    ]:

        rows.append(
            {
                "district": plan["district"],
                "action_type": "EXPAND_COURSE",
                **item,
            }
        )

    for item in plan[
        "courses_to_review"
    ]:

        rows.append(
            {
                "district": plan["district"],
                "action_type": "REVIEW_COURSE",
                **item,
            }
        )

    for item in plan[
        "emerging_opportunities"
    ]:

        rows.append(
            {
                "district": plan["district"],
                "action_type": "EMERGING_OPPORTUNITY",
                **item,
            }
        )

    pd.DataFrame(rows).to_csv(
        path,
        index=False,
    )
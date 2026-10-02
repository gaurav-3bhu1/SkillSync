from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import csv

from src.external_data_adapter import (
    load_external_jobs,
    standardize_jobs,
    load_external_training_supply,
    standardize_training_supply,
)

from src.skill_normalizer import normalize_skill


CROSSWALK_PATH = Path(
    "data/processed/skill_crosswalk.csv"
)

JOB_OUTPUT_PATH = Path(
    "data/processed/job_skill_normalized.csv"
)

TRAINING_OUTPUT_PATH = Path(
    "data/processed/training_skill_normalized.csv"
)


def load_job_crosswalk():
    """
    Existing job crosswalk is the authoritative resolution for
    job-market raw skills.
    """

    lookup = {}

    with CROSSWALK_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            lookup[row["raw_skill"]] = row

    return lookup


def normalize_training_skill(
    raw_skill: str,
    source: str,
):
    """
    Normalize a training skill.

    Exact and semantic matches use the shared taxonomy.
    Unmatched skills become provisional training concepts.
    """

    result = normalize_skill(raw_skill)

    if result.method == "exact_alias":
        return {
            "raw_skill": raw_skill,
            "canonical_skill": result.canonical_skill,
            "skill_id": result.skill_id,
            "skill_family": result.skill_family,
            "sector": result.sector,
            "method": result.method,
            "confidence": result.confidence,
            "resolution_status": "EXACT_RESOLVED",
            "source": source,
        }

    if result.method == "semantic_candidate":
        return {
            "raw_skill": raw_skill,
            "canonical_skill": result.canonical_skill,
            "skill_id": result.skill_id,
            "skill_family": result.skill_family,
            "sector": result.sector,
            "method": result.method,
            "confidence": result.confidence,
            "resolution_status": "SEMANTIC_REVIEW",
            "source": source,
        }

    # Keep unmatched training skills visible rather than silently dropping.
    return {
        "raw_skill": raw_skill,
        "canonical_skill": raw_skill,
        "skill_id": f"TRAINING_RAW::{raw_skill}",
        "skill_family": "",
        "sector": "",
        "method": "unmatched",
        "confidence": result.confidence,
        "resolution_status": "PROVISIONAL_RAW",
        "source": source,
    }


def main():

    print("=" * 80)
    print("SkillSync - Build Normalized Skill Tables")
    print("=" * 80)

    # ==========================================================
    # LOAD EXISTING JOB CROSSWALK
    # ==========================================================

    job_crosswalk = load_job_crosswalk()

    print(
        f"\nLoaded job crosswalk entries: "
        f"{len(job_crosswalk)}"
    )

    # ==========================================================
    # JOB SKILLS
    # ==========================================================

    jobs_raw = load_external_jobs()
    jobs = standardize_jobs(jobs_raw)

    job_rows = []

    for _, job in jobs.iterrows():

        job_id = str(job["job_id"])
        location = str(job["location"])
        industry = str(job["industry"])
        role = str(job["role"])

        for raw_skill in job["required_skills"]:

            raw_skill = str(raw_skill).strip()

            if not raw_skill:
                continue

            mapping = job_crosswalk.get(raw_skill)

            if mapping is None:
                # Defensive fallback.
                result = normalize_skill(raw_skill)

                if result.canonical_skill:
                    operational_skill = result.canonical_skill
                    operational_id = result.skill_id
                    status = "SEMANTIC_REVIEW"
                    method = result.method
                    confidence = result.confidence
                    family = result.skill_family
                    sector = result.sector

                else:
                    operational_skill = raw_skill
                    operational_id = f"JOB_RAW::{raw_skill}"
                    status = "PROVISIONAL_RAW"
                    method = "unmatched"
                    confidence = result.confidence
                    family = ""
                    sector = ""

            else:
                operational_skill = mapping[
                    "operational_skill"
                ]

                operational_id = mapping[
                    "operational_skill_id"
                ]

                status = mapping[
                    "resolution_status"
                ]

                method = mapping[
                    "normalization_method"
                ]

                confidence = float(
                    mapping["confidence"]
                )

                family = mapping[
                    "candidate_skill_family"
                ]

                sector = mapping[
                    "candidate_sector"
                ]

            job_rows.append(
                {
                    "job_id": job_id,
                    "role": role,
                    "location": location,
                    "industry": industry,
                    "raw_skill": raw_skill,
                    "skill_id": operational_id,
                    "skill": operational_skill,
                    "skill_family": family,
                    "skill_sector": sector,
                    "normalization_method": method,
                    "confidence": f"{confidence:.4f}",
                    "resolution_status": status,
                    "demand_trend": str(
                        job["demand_trend"]
                    ),
                    "automation_risk_index": str(
                        job["automation_risk_index"]
                    ),
                    "salary_monthly_inr": job[
                        "salary_monthly_inr"
                    ],
                    "nsqf_level": job[
                        "nsqf_level"
                    ],
                    "proficiency": job[
                        "proficiency"
                    ],
                }
            )

    # ==========================================================
    # TRAINING SKILLS
    # ==========================================================

    training_raw = load_external_training_supply()
    training = standardize_training_supply(
        training_raw
    )

    training_rows = []

    for _, course in training.iterrows():

        iti_id = str(course["iti_id"])

        base = {
            "iti_id": iti_id,
            "iti_name": str(course["iti_name"]),
            "location": str(course["location"]),
            "industrial_cluster": str(
                course["industrial_cluster"]
            ),
            "course_name": str(course["course_name"]),
            "industry": str(course["industry"]),
            "annual_intake_seats": course[
                "annual_intake_seats"
            ],
            "placement_rate_pct": course[
                "placement_rate_pct"
            ],
            "mismatch_flag": str(
                course["mismatch_flag"]
            ),
        }

        # ------------------------------------------------------
        # SKILLS TAUGHT
        # ------------------------------------------------------

        for raw_skill in course["skills_taught"]:

            raw_skill = str(raw_skill).strip()

            if not raw_skill:
                continue

            match = normalize_training_skill(
                raw_skill,
                source="skills_taught",
            )

            training_rows.append(
                {
                    **base,
                    "raw_skill": match["raw_skill"],
                    "skill_id": match["skill_id"],
                    "skill": match["canonical_skill"],
                    "skill_family": match[
                        "skill_family"
                    ],
                    "skill_sector": match["sector"],
                    "source": match["source"],
                    "normalization_method": match[
                        "method"
                    ],
                    "confidence": f"{match['confidence']:.4f}",
                    "resolution_status": match[
                        "resolution_status"
                    ],
                    "counts_as_supply": True,
                }
            )

        # ------------------------------------------------------
        # SKILLS GAP
        # ------------------------------------------------------

        for raw_skill in course["skills_gap"]:

            raw_skill = str(raw_skill).strip()

            if not raw_skill:
                continue

            match = normalize_training_skill(
                raw_skill,
                source="skills_gap",
            )

            training_rows.append(
                {
                    **base,
                    "raw_skill": match["raw_skill"],
                    "skill_id": match["skill_id"],
                    "skill": match["canonical_skill"],
                    "skill_family": match[
                        "skill_family"
                    ],
                    "skill_sector": match["sector"],
                    "source": match["source"],
                    "normalization_method": match[
                        "method"
                    ],
                    "confidence": f"{match['confidence']:.4f}",
                    "resolution_status": match[
                        "resolution_status"
                    ],
                    "counts_as_supply": False,
                }
            )

    # ==========================================================
    # WRITE JOB TABLE
    # ==========================================================

    JOB_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with JOB_OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "job_id",
                "role",
                "location",
                "industry",
                "raw_skill",
                "skill_id",
                "skill",
                "skill_family",
                "skill_sector",
                "normalization_method",
                "confidence",
                "resolution_status",
                "demand_trend",
                "automation_risk_index",
                "salary_monthly_inr",
                "nsqf_level",
                "proficiency",
            ],
        )

        writer.writeheader()
        writer.writerows(job_rows)

    # ==========================================================
    # WRITE TRAINING TABLE
    # ==========================================================

    with TRAINING_OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "iti_id",
                "iti_name",
                "location",
                "industrial_cluster",
                "course_name",
                "industry",
                "annual_intake_seats",
                "placement_rate_pct",
                "mismatch_flag",
                "raw_skill",
                "skill_id",
                "skill",
                "skill_family",
                "skill_sector",
                "source",
                "normalization_method",
                "confidence",
                "resolution_status",
                "counts_as_supply",
            ],
        )

        writer.writeheader()
        writer.writerows(training_rows)

    # ==========================================================
    # SUMMARY
    # ==========================================================

    job_status = defaultdict(int)

    for row in job_rows:
        job_status[row["resolution_status"]] += 1

    training_status = defaultdict(int)

    for row in training_rows:
        training_status[row["resolution_status"]] += 1

    taught_count = sum(
        1
        for row in training_rows
        if row["source"] == "skills_taught"
    )

    gap_count = sum(
        1
        for row in training_rows
        if row["source"] == "skills_gap"
    )

    print("\nJOB SKILLS")
    print("-" * 80)
    print(f"Job-skill rows: {len(job_rows)}")

    for status, count in sorted(job_status.items()):
        print(f"  {status}: {count}")

    print("\nTRAINING SKILLS")
    print("-" * 80)
    print(f"Training-skill rows: {len(training_rows)}")
    print(f"  Skills taught: {taught_count}")
    print(f"  Skills gaps: {gap_count}")

    for status, count in sorted(training_status.items()):
        print(f"  {status}: {count}")

    print(
        f"\nWritten:\n"
        f"  {JOB_OUTPUT_PATH}\n"
        f"  {TRAINING_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
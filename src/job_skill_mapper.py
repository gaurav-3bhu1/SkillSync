from __future__ import annotations

from typing import List

import pandas as pd

from src.role_normalizer import normalize_role
from src.skill_extractor import SkillExtractor


def build_job_skill_mapping(
    jobs: pd.DataFrame,
    extractor: SkillExtractor,
) -> pd.DataFrame:
    """
    Convert jobs into a long-format job-skill table.

    One row represents one job-skill relationship.
    """

    rows: List[dict] = []

    for _, job in jobs.iterrows():

        canonical_role = normalize_role(
            job["title"]
        )

        extracted_skills = extractor.extract(
            job["description"]
        )

        for skill in extracted_skills:

            rows.append(
                {
                    "job_id": job["job_id"],
                    "title": job["title"],
                    "role": canonical_role,
                    "location": job["location"],
                    "industry": job["industry"],
                    "posted_date": job["posted_date"],
                    "skill": skill,
                }
            )

    return pd.DataFrame(rows)
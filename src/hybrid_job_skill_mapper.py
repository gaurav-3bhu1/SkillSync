from __future__ import annotations

from typing import List

import pandas as pd


def build_hybrid_job_skill_mapping(
    jobs: pd.DataFrame,
    extractor,
) -> pd.DataFrame:
    """
    Build a long-format job-skill mapping using a
    hybrid extractor.

    The mapping preserves extraction source and confidence.

    Output columns:

        job_id
        title
        role
        location
        industry
        posted_date
        skill
        source
        confidence
    """

    rows: List[dict] = []

    for _, job in jobs.iterrows():

        text = (
            str(job["title"])
            + ". "
            + str(job["description"])
        )

        results = extractor.extract_with_metadata(
            text
        )

        for result in results:

            rows.append(
                {
                    "job_id": job["job_id"],
                    "title": job["title"],
                    "role": extractor_role(job["title"]),
                    "location": job["location"],
                    "industry": job["industry"],
                    "posted_date": job["posted_date"],
                    "skill": result["skill"],
                    "source": result["source"],
                    "confidence": result["confidence"],
                }
            )

    columns = [
        "job_id",
        "title",
        "role",
        "location",
        "industry",
        "posted_date",
        "skill",
        "source",
        "confidence",
    ]

    return pd.DataFrame(rows, columns=columns)


def extractor_role(title: str) -> str:
    """
    Keep role normalization in one place by using the
    existing role normalizer.
    """

    from src.role_normalizer import normalize_role

    return normalize_role(title)
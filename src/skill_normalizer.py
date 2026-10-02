from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer, util


TAXONOMY_PATH = Path("data/processed/skill_taxonomy.csv")

MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_SEMANTIC_THRESHOLD = 0.72


@dataclass(frozen=True)
class SkillMatch:
    raw_skill: str
    canonical_skill: str | None
    skill_id: str | None
    skill_family: str | None
    sector: str | None
    method: str
    confidence: float


def normalize_text(text: str) -> str:
    text = str(text).strip().lower()

    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")

    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


@lru_cache(maxsize=1)
def load_taxonomy():
    rows = []

    with TAXONOMY_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            aliases = [
                alias.strip()
                for alias in row["aliases"].split("|")
                if alias.strip()
            ]

            rows.append(
                {
                    "skill_id": row["skill_id"].strip(),
                    "canonical_skill": row["canonical_skill"].strip(),
                    "skill_family": row["skill_family"].strip(),
                    "sector": row["sector"].strip(),
                    "skill_type": row["skill_type"].strip(),
                    "aliases": aliases,
                }
            )

    return rows


@lru_cache(maxsize=1)
def build_alias_lookup():
    lookup = {}

    for row in load_taxonomy():
        terms = [
            row["canonical_skill"],
            *row["aliases"],
        ]

        for term in terms:
            normalized = normalize_text(term)

            if normalized:
                # Same-skill duplicates are harmless.
                lookup[normalized] = row

    return lookup


@lru_cache(maxsize=1)
def build_semantic_candidates():
    """
    Returns:
        candidates: list[str]
        metadata: list[dict]
    """

    candidates = []
    metadata = []

    for row in load_taxonomy():
        terms = [
            row["canonical_skill"],
            *row["aliases"],
        ]

        seen = set()

        for term in terms:
            normalized = normalize_text(term)

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)

            candidates.append(term)
            metadata.append(row)

    return candidates, metadata


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def get_candidate_embeddings():
    candidates, _ = build_semantic_candidates()

    model = get_model()

    return model.encode(
        candidates,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )


def normalize_skill(
    raw_skill: str,
    semantic_threshold: float = DEFAULT_SEMANTIC_THRESHOLD,
) -> SkillMatch:

    raw_skill = str(raw_skill).strip()

    if not raw_skill:
        return SkillMatch(
            raw_skill="",
            canonical_skill=None,
            skill_id=None,
            skill_family=None,
            sector=None,
            method="empty",
            confidence=0.0,
        )

    alias_lookup = build_alias_lookup()

    normalized = normalize_text(raw_skill)

    # ---------------------------------------------------------
    # 1. Exact alias match
    # ---------------------------------------------------------
    exact = alias_lookup.get(normalized)

    if exact:
        return SkillMatch(
            raw_skill=raw_skill,
            canonical_skill=exact["canonical_skill"],
            skill_id=exact["skill_id"],
            skill_family=exact["skill_family"],
            sector=exact["sector"],
            method="exact_alias",
            confidence=1.0,
        )

    # ---------------------------------------------------------
    # 2. Semantic matching
    # ---------------------------------------------------------
    model = get_model()

    candidates, metadata = build_semantic_candidates()
    candidate_embeddings = get_candidate_embeddings()

    query_embedding = model.encode(
        [raw_skill],
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    scores = util.cos_sim(
        query_embedding,
        candidate_embeddings,
    )[0]

    best_index = int(scores.argmax())
    best_score = float(scores[best_index])

    if best_score < semantic_threshold:
        return SkillMatch(
            raw_skill=raw_skill,
            canonical_skill=None,
            skill_id=None,
            skill_family=None,
            sector=None,
            method="unmatched",
            confidence=best_score,
        )

    matched = metadata[best_index]

    return SkillMatch(
        raw_skill=raw_skill,
        canonical_skill=matched["canonical_skill"],
        skill_id=matched["skill_id"],
        skill_family=matched["skill_family"],
        sector=matched["sector"],
        method="semantic_candidate",
        confidence=best_score,
    )
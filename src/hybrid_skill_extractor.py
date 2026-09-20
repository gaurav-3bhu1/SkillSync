from __future__ import annotations

from typing import Dict, List

import pandas as pd

from src.skill_extractor import SkillExtractor
from src.semantic_matcher import SemanticSkillMatcher
from src.config import (
    SEMANTIC_THRESHOLD,
    SEMANTIC_TOP_K,
)

class HybridSkillExtractor:
    """
    Combines deterministic skill extraction with
    semantic embedding-based matching.

    Exact matches are always retained.

    Semantic matches are added only when their
    similarity score reaches the configured threshold.
    """

    def __init__(
        self,
        skills: pd.DataFrame,
        semantic_threshold: float = SEMANTIC_THRESHOLD,
        semantic_top_k: int = SEMANTIC_TOP_K,
    ):
        self.exact_extractor = SkillExtractor(skills)

        self.semantic_matcher = SemanticSkillMatcher(
            skills,
            threshold=semantic_threshold,
        )

        self.semantic_top_k = semantic_top_k

    def extract(
        self,
        text: str,
        semantic_threshold: float | None = None,
    ) -> List[str]:
        """
        Return canonical skill names.

        This method intentionally has the same interface
        as SkillExtractor.extract(), so this class can be
        used anywhere the existing extractor is expected.
        """

        metadata = self.extract_with_metadata(
            text,
            semantic_threshold=semantic_threshold,
        )

        return [
            item["skill"]
            for item in metadata
        ]

    def extract_with_metadata(
        self,
        text: str,
        semantic_threshold: float | None = None,
    ) -> List[Dict]:
        """
        Return extracted skills together with their source
        and confidence.

        Example:

        [
            {
                "skill": "Java",
                "source": "exact",
                "confidence": 1.0,
            },
            {
                "skill": "Docker",
                "source": "semantic",
                "confidence": 0.5629,
            },
        ]
        """

        if not text or not str(text).strip():
            return []

        exact_skills = self.exact_extractor.extract(
            text
        )

        results: List[Dict] = []

        seen = set()

        # --------------------------------------------------
        # EXACT MATCHES
        # --------------------------------------------------

        for skill in exact_skills:

            normalized = skill.strip().casefold()

            if normalized in seen:
                continue

            seen.add(normalized)

            results.append(
                {
                    "skill": skill,
                    "source": "exact",
                    "confidence": 1.0,
                }
            )

        # --------------------------------------------------
        # SEMANTIC MATCHES
        # --------------------------------------------------

        semantic_matches = (
            self.semantic_matcher.match(
                text,
                top_k=self.semantic_top_k,
                threshold=semantic_threshold,
            )
        )

        for match in semantic_matches:

            skill = match["skill"]
            score = float(match["score"])

            normalized = skill.strip().casefold()

            if normalized in seen:
                continue

            seen.add(normalized)

            results.append(
                {
                    "skill": skill,
                    "source": "semantic",
                    "confidence": score,
                }
            )

        return results
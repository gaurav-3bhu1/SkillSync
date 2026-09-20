from __future__ import annotations

from typing import List, Dict

import pandas as pd
from sentence_transformers import SentenceTransformer
from src.config import SEMANTIC_THRESHOLD


class SemanticSkillMatcher:
    """
    Semantic skill matcher using sentence embeddings.

    It compares a text fragment against the canonical skills
    defined in skills.csv and returns the most semantically
    similar skills above a configurable threshold.
    """

    def __init__(
        self,
        skills: pd.DataFrame,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        threshold: float = SEMANTIC_THRESHOLD,
    ):
        if "skill_name" not in skills.columns:
            raise ValueError(
                "skills DataFrame must contain skill_name"
            )

        self.skills = skills.copy()

        self.skill_names = (
            self.skills["skill_name"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

        if not self.skill_names:
            raise ValueError(
                "No canonical skills were found."
            )

        self.threshold = threshold

        self.model = SentenceTransformer(
            model_name
        )

        self.skill_embeddings = self.model.encode(
            self.skill_names,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def match(
    self,
    text: str,
    top_k: int = 5,
    threshold: float | None = None,
    ) -> List[Dict]:
        """
        Return semantically similar canonical skills.

        Each result contains:

            skill
            score
        """

        if not text or not str(text).strip():
            return []

        embedding = self.model.encode(
            [str(text)],
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        similarities = self.model.similarity(
            embedding,
            self.skill_embeddings,
        )[0]

        scores = similarities.tolist()

        ranked = sorted(
            zip(self.skill_names, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        results = []

        active_threshold = (
            self.threshold
            if threshold is None
            else threshold
        )

        for skill, score in ranked[:top_k]:
            score = float(score)

            if score >= active_threshold:
                results.append(
                    {
                        "skill": skill,
                        "score": round(score, 4),
                    }
                )

        return results
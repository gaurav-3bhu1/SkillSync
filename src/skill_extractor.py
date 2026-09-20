from __future__ import annotations

import re
from typing import Dict, List, Tuple

import pandas as pd


class SkillExtractor:
    """
    Extracts canonical skills from text using the skill vocabulary
    stored in skills.csv.

    This is our baseline extractor. It uses aliases rather than
    machine learning, giving us a deterministic and testable baseline.
    """

    def __init__(self, skills_df: pd.DataFrame) -> None:
        self.skills_df = skills_df
        self.alias_map = self._build_alias_map()

    def _build_alias_map(self) -> Dict[str, str]:
        """
        Create:

            alias -> canonical skill

        Example:

            "reactjs"     -> "React"
            "react.js"    -> "React"
            "postgres"    -> "PostgreSQL"
            "springboot"  -> "Spring Boot"
        """

        alias_map: Dict[str, str] = {}

        for _, row in self.skills_df.iterrows():
            canonical_skill = str(row["skill_name"]).strip()

            # Include canonical name itself.
            alias_map[canonical_skill.lower()] = canonical_skill

            aliases = str(row["aliases"])

            for alias in aliases.split(";"):
                alias = alias.strip()

                if alias:
                    alias_map[alias.lower()] = canonical_skill

        return alias_map

    def extract(self, text: str) -> List[str]:
        """
        Extract canonical skills from a piece of text.

        Returns:
            List[str]: unique canonical skill names.
        """

        if not isinstance(text, str) or not text.strip():
            return []

        text = text.lower()

        # Longest aliases first so that:
        #
        # "REST API"
        #
        # is matched before:
        #
        # "REST"
        #
        sorted_aliases = sorted(
            self.alias_map.keys(),
            key=len,
            reverse=True,
        )

        matches: List[Tuple[int, int, str]] = []

        for alias in sorted_aliases:
            escaped_alias = re.escape(alias)

            # Prevent partial-word matches.
            pattern = rf"(?<![a-zA-Z0-9_]){escaped_alias}(?![a-zA-Z0-9_])"

            for match in re.finditer(pattern, text):
                canonical_skill = self.alias_map[alias]

                matches.append(
                    (
                        match.start(),
                        match.end(),
                        canonical_skill,
                    )
                )

        # Sort by position in the original text.
        matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))

        selected: List[Tuple[int, int, str]] = []
        seen_skills = set()

        for start, end, canonical_skill in matches:

            # Skip duplicate canonical skills.
            if canonical_skill in seen_skills:
                continue

            # Check overlap with an already selected match.
            overlaps = any(
                not (end <= selected_start or start >= selected_end)
                for selected_start, selected_end, _ in selected
            )

            if overlaps:
                continue

            selected.append((start, end, canonical_skill))
            seen_skills.add(canonical_skill)

        # Preserve order in which the skills appeared.
        selected.sort(key=lambda item: item[0])

        return [skill for _, _, skill in selected]
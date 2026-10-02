from collections import defaultdict
from pathlib import Path
import csv

from src.skill_normalizer import normalize_text


TAXONOMY_PATH = Path("data/processed/skill_taxonomy.csv")


def main():
    print("=" * 80)
    print("SkillSync - Skill Taxonomy Validator")
    print("=" * 80)

    with TAXONOMY_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        rows = list(csv.DictReader(f))

    errors = []
    warnings = []

    skill_ids = set()

    # Maps normalized alias -> set of (skill_id, canonical_skill)
    alias_to_skills = defaultdict(set)

    for row in rows:
        skill_id = row["skill_id"].strip()
        canonical = row["canonical_skill"].strip()

        if not skill_id:
            errors.append("Missing skill_id")

        if skill_id in skill_ids:
            errors.append(f"Duplicate skill_id: {skill_id}")

        skill_ids.add(skill_id)

        aliases = [
            alias.strip()
            for alias in row["aliases"].split("|")
            if alias.strip()
        ]

        # Include canonical skill as a valid lookup term.
        all_terms = [canonical, *aliases]

        # Remove duplicate terms belonging to the SAME skill.
        unique_terms = {
            normalize_text(term)
            for term in all_terms
            if normalize_text(term)
        }

        for normalized in unique_terms:
            alias_to_skills[normalized].add(
                (skill_id, canonical)
            )

        # Warn if canonical is explicitly repeated in aliases.
        canonical_norm = normalize_text(canonical)

        alias_norms = {
            normalize_text(alias)
            for alias in aliases
            if normalize_text(alias)
        }

        if canonical_norm in alias_norms:
            warnings.append(
                f"Canonical skill repeated in aliases: "
                f"{skill_id} -> {canonical}"
            )

    # Only report aliases that point to MORE THAN ONE skill.
    true_collisions = {
        alias: matches
        for alias, matches in alias_to_skills.items()
        if len(matches) > 1
    }

    print(f"\nTaxonomy rows: {len(rows)}")
    print(f"Unique skill IDs: {len(skill_ids)}")
    print(f"Unique normalized aliases: {len(alias_to_skills)}")

    if warnings:
        print(
            f"\nWarnings: {len(warnings)} canonical/alias repetitions"
        )

    if true_collisions:
        print("\nTRUE CROSS-SKILL ALIAS COLLISIONS FOUND:")
        print("-" * 80)

        for alias, matches in sorted(true_collisions.items()):
            print(f"\nAlias: {alias}")

            for skill_id, canonical in sorted(matches):
                print(f"  {skill_id} -> {canonical}")

        errors.append(
            f"{len(true_collisions)} aliases map to multiple skills"
        )

    if errors:
        print("\nTAXONOMY VALIDATION FAILED")

        for error in errors:
            print(f"ERROR: {error}")

        raise SystemExit(1)

    print("\nTaxonomy validation passed.")

    if warnings:
        print(
            "\nNote: warnings are non-fatal and can be cleaned later."
        )


if __name__ == "__main__":
    main()
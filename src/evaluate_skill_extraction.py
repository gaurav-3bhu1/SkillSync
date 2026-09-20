from __future__ import annotations

import pandas as pd

from src.data_loader import load_skills
from src.skill_extractor import SkillExtractor
from src.hybrid_skill_extractor import HybridSkillExtractor
from src.evaluation import (
    calculate_example_metrics,
    calculate_micro_metrics,
    calculate_hard_negative_metrics,
)


EVAL_PATH = (
    "data/raw/skill_eval.csv"
)


def parse_expected_skills(
    value,
) -> list[str]:
    """
    Parse expected skills from the evaluation CSV.

    Empty cells / NaN represent examples where no
    canonical skill should be extracted.
    """

    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    return [
        skill.strip()
        for skill in value.split(";")
        if skill.strip()
    ]


def evaluate_extractor(
    eval_df: pd.DataFrame,
    extractor,
    semantic_threshold: float | None = None,
) -> tuple[list[dict], dict]:

    example_results = []

    for _, row in eval_df.iterrows():

        text = row["text"]

        expected = parse_expected_skills(
            row["expected_skills"]
        )

        if semantic_threshold is None:
            predicted = extractor.extract(
                text
            )
        else:
            predicted = extractor.extract(
                text,
                semantic_threshold=semantic_threshold,
            )

        metrics = calculate_example_metrics(
            predicted=predicted,
            expected=expected,
        )

        example_results.append(
            {
                "eval_id": row["eval_id"],
                "expected": expected,
                "predicted": predicted,
                **metrics,
            }
        )

    micro_metrics = calculate_micro_metrics(
        example_results
    )

    return example_results, micro_metrics


def print_detailed_results(
    results: list[dict],
):

    print("\n" + "=" * 80)
    print("PER-EXAMPLE RESULTS")
    print("=" * 80)

    for result in results:

        print(
            f"\n{result['eval_id']}"
        )

        print(
            f"Expected: "
            f"{result['expected']}"
        )

        print(
            f"Predicted: "
            f"{result['predicted']}"
        )

        print(
            f"Precision: "
            f"{result['precision']:.4f}"
        )

        print(
            f"Recall: "
            f"{result['recall']:.4f}"
        )

        print(
            f"F1: "
            f"{result['f1']:.4f}"
        )


def main():

    eval_df = pd.read_csv(
        EVAL_PATH
    )

    skills = load_skills()

    exact_extractor = SkillExtractor(
        skills
    )

    hybrid_extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
        semantic_top_k=3,
    )

    print("=" * 80)
    print("SkillSync - Skill Extraction Evaluation")
    print("=" * 80)

    print(
        f"\nEvaluation examples: "
        f"{len(eval_df)}"
    )

    # -------------------------------------------------------
    # EXACT BASELINE
    # -------------------------------------------------------

    exact_results, exact_metrics = (
        evaluate_extractor(
            eval_df,
            exact_extractor,
        )
    )

    print("\n" + "=" * 80)
    print("EXACT MATCHING BASELINE")
    print("=" * 80)

    print(
        f"Precision: "
        f"{exact_metrics['precision']:.4f}"
    )

    print(
        f"Recall: "
        f"{exact_metrics['recall']:.4f}"
    )

    print(
        f"F1: "
        f"{exact_metrics['f1']:.4f}"
    )

    # -------------------------------------------------------
    # HYBRID MODEL
    # -------------------------------------------------------

    hybrid_results, hybrid_metrics = (
        evaluate_extractor(
            eval_df,
            hybrid_extractor,
        )
    )
    hybrid_negative_metrics = (
    calculate_hard_negative_metrics(
        hybrid_results
    )
    )

    print("\n" + "=" * 80)
    print("HYBRID MATCHING")
    print("=" * 80)

    print(
        f"Precision: "
        f"{hybrid_metrics['precision']:.4f}"
    )

    print(
        f"Recall: "
        f"{hybrid_metrics['recall']:.4f}"
    )

    print(
        f"F1: "
        f"{hybrid_metrics['f1']:.4f}"
    )

    # -------------------------------------------------------
    # COMPARISON
    # -------------------------------------------------------

    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)

    print(
        f"Exact F1:  "
        f"{exact_metrics['f1']:.4f}"
    )

    print(
        f"Hybrid F1: "
        f"{hybrid_metrics['f1']:.4f}"
    )

    print("\n" + "=" * 80)
    print("HYBRID HARD-NEGATIVE EVALUATION")
    print("=" * 80)

    print(
        f"Negative examples: "
        f"{hybrid_negative_metrics['negative_examples']}"
    )

    print(
        f"False-positive examples: "
        f"{hybrid_negative_metrics['false_positive_examples']}"
    )

    print(
        f"Specificity: "
        f"{hybrid_negative_metrics['specificity']:.4f}"
    )

    improvement = (
        hybrid_metrics["f1"]
        - exact_metrics["f1"]
    )

    print(
        f"F1 change: "
        f"{improvement:+.4f}"
    )

    # -------------------------------------------------------
    # DETAILED HYBRID RESULTS
    # -------------------------------------------------------

    print_detailed_results(
        hybrid_results
    )


if __name__ == "__main__":
    main()
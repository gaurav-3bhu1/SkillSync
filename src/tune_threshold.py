from __future__ import annotations

import pandas as pd

from src.data_loader import load_skills
from src.hybrid_skill_extractor import HybridSkillExtractor
from src.evaluate_skill_extraction import (
    evaluate_extractor,
)
from src.evaluation import (
    calculate_hard_negative_metrics,
)


EVAL_PATH = "data/raw/skill_eval.csv"

THRESHOLDS = [
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
]


def main():

    eval_df = pd.read_csv(
        EVAL_PATH
    )

    skills = load_skills()

    hybrid_extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
        semantic_top_k=3,
    )

    rows = []

    print("=" * 80)
    print("SkillSync - Semantic Threshold Sweep")
    print("=" * 80)

    for threshold in THRESHOLDS:

        results, metrics = evaluate_extractor(
            eval_df,
            hybrid_extractor,
            semantic_threshold=threshold,
        )

        negative_metrics = (
            calculate_hard_negative_metrics(
                results
            )
        )

        rows.append(
            {
                "threshold": threshold,
                "precision": round(
                    metrics["precision"],
                    4,
                ),
                "recall": round(
                    metrics["recall"],
                    4,
                ),
                "f1": round(
                    metrics["f1"],
                    4,
                ),
                "hard_negative_specificity": round(
                    negative_metrics[
                        "specificity"
                    ],
                    4,
                ),
                "false_positive_examples": (
                    negative_metrics[
                        "false_positive_examples"
                    ]
                ),
            }
        )

    results_df = pd.DataFrame(rows)

    print("\n" + "=" * 80)
    print("THRESHOLD RESULTS")
    print("=" * 80)

    print(
        results_df.to_string(
            index=False
        )
    )

    # ------------------------------------------------------
    # SELECT BEST THRESHOLD
    # ------------------------------------------------------
    #
    # Primary criterion:
    #   highest F1
    #
    # Tie-breaker 1:
    #   highest hard-negative specificity
    #
    # Tie-breaker 2:
    #   highest precision
    #
    # This is a prototype selection rule and should later
    # be validated on a larger held-out evaluation set.

    best = results_df.sort_values(
        [
            "f1",
            "hard_negative_specificity",
            "precision",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    ).iloc[0]

    print("\n" + "=" * 80)
    print("SELECTED THRESHOLD")
    print("=" * 80)

    print(
        f"Threshold: "
        f"{best['threshold']:.2f}"
    )

    print(
        f"F1: "
        f"{best['f1']:.4f}"
    )

    print(
        f"Precision: "
        f"{best['precision']:.4f}"
    )

    print(
        f"Recall: "
        f"{best['recall']:.4f}"
    )

    print(
        f"Hard-negative specificity: "
        f"{best['hard_negative_specificity']:.4f}"
    )

    output_path = (
        "data/processed/"
        "semantic_threshold_results.csv"
    )

    results_df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved threshold results to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()
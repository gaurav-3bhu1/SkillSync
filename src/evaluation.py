from __future__ import annotations

from typing import Iterable, Set

import pandas as pd


def normalize_skill_set(
    skills: Iterable[str],
) -> Set[str]:
    """
    Normalize skill names for set comparison.
    """

    return {
        str(skill).strip().casefold()
        for skill in skills
        if str(skill).strip()
    }


def calculate_example_metrics(
    predicted: Iterable[str],
    expected: Iterable[str],
) -> dict:
    """
    Calculate precision, recall and F1 for one
    multi-label skill extraction example.
    """

    predicted_set = normalize_skill_set(
        predicted
    )

    expected_set = normalize_skill_set(
        expected
    )

    true_positive = len(
        predicted_set & expected_set
    )

    false_positive = len(
        predicted_set - expected_set
    )

    false_negative = len(
        expected_set - predicted_set
    )

    if true_positive + false_positive > 0:
        precision = (
            true_positive
            / (true_positive + false_positive)
        )
    else:
        precision = 0.0

    if true_positive + false_negative > 0:
        recall = (
            true_positive
            / (true_positive + false_negative)
        )
    else:
        recall = 0.0

    if precision + recall > 0:
        f1 = (
            2
            * precision
            * recall
            / (precision + recall)
        )
    else:
        f1 = 0.0

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def calculate_micro_metrics(
    results: list[dict],
) -> dict:
    """
    Calculate micro-averaged precision, recall and F1.
    """

    true_positive = sum(
        item["true_positive"]
        for item in results
    )

    false_positive = sum(
        item["false_positive"]
        for item in results
    )

    false_negative = sum(
        item["false_negative"]
        for item in results
    )

    if true_positive + false_positive > 0:
        precision = (
            true_positive
            / (true_positive + false_positive)
        )
    else:
        precision = 0.0

    if true_positive + false_negative > 0:
        recall = (
            true_positive
            / (true_positive + false_negative)
        )
    else:
        recall = 0.0

    if precision + recall > 0:
        f1 = (
            2
            * precision
            * recall
            / (precision + recall)
        )
    else:
        f1 = 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

def calculate_hard_negative_metrics(
    results: list[dict],
) -> dict:
    """
    Evaluate examples whose expected skill set is empty.

    These examples measure whether the extractor
    invents skills for broad or ambiguous text.
    """

    negative_examples = [
        result
        for result in results
        if len(result["expected"]) == 0
    ]

    if not negative_examples:
        return {
            "negative_examples": 0,
            "false_positive_examples": 0,
            "specificity": 0.0,
        }

    false_positive_examples = sum(
        1
        for result in negative_examples
        if len(result["predicted"]) > 0
    )

    true_negative_examples = (
        len(negative_examples)
        - false_positive_examples
    )

    specificity = (
        true_negative_examples
        / len(negative_examples)
    )

    return {
        "negative_examples": len(
            negative_examples
        ),
        "false_positive_examples": (
            false_positive_examples
        ),
        "specificity": specificity,
    }
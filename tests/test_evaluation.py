from src.evaluation import (
    calculate_example_metrics,
    calculate_micro_metrics,
)


def test_example_metrics():

    result = calculate_example_metrics(
        predicted=["Java", "Docker"],
        expected=["Java", "Spring Boot"],
    )

    print("\nExample metrics:")
    print(result)

    assert result["true_positive"] == 1
    assert result["false_positive"] == 1
    assert result["false_negative"] == 1

    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5


def test_micro_metrics():

    results = [
        {
            "true_positive": 2,
            "false_positive": 1,
            "false_negative": 1,
        },
        {
            "true_positive": 1,
            "false_positive": 0,
            "false_negative": 1,
        },
    ]

    # calculate_micro_metrics expects precision
    # fields only if using the current implementation,
    # so add them through the same metric structure.

    for result in results:

        tp = result["true_positive"]
        fp = result["false_positive"]
        fn = result["false_negative"]

        result["precision"] = (
            tp / (tp + fp)
            if tp + fp > 0
            else 0.0
        )

        result["recall"] = (
            tp / (tp + fn)
            if tp + fn > 0
            else 0.0
        )

        result["f1"] = 0.0

    metrics = calculate_micro_metrics(
        results
    )

    print("\nMicro metrics:")
    print(metrics)

    assert round(
        metrics["precision"], 4
    ) == 0.75

    assert round(
        metrics["recall"], 4
    ) == 0.6

    assert round(
        metrics["f1"], 4
    ) == 0.6667


if __name__ == "__main__":

    test_example_metrics()
    test_micro_metrics()

    print(
        "\nEvaluation tests passed."
    )
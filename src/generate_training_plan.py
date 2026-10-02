from pathlib import Path

import pandas as pd

from src.district_training_plan import (
    build_district_training_plan,
    save_training_plan,
)


ALIGNMENT_PATH = Path(
    "data/processed/district_skill_alignment.csv"
)

TRAINING_PATH = Path(
    "data/processed/training_skill_normalized.csv"
)

OUTPUT_PATH = Path(
    "data/processed/district_training_plan.csv"
)


def main():

    alignment = pd.read_csv(
        ALIGNMENT_PATH
    )

    training = pd.read_csv(
        TRAINING_PATH
    )

    districts = sorted(
        alignment[
            "location"
        ]
        .dropna()
        .astype(str)
        .unique()
    )

    print(
        f"Districts available: {len(districts)}"
    )

    for district in districts:

        plan = build_district_training_plan(
            alignment=alignment,
            training=training,
            district=district,
            top_n=10,
        )

        print()
        print(
            "=" * 70
        )
        print(
            f"TRAINING PLAN: {district}"
        )
        print(
            "=" * 70
        )

        print(
            "\nPriority skills:"
        )

        for item in plan[
            "priority_skills"
        ][:5]:

            print(
                f"  - {item['skill']} "
                f"(score={item['action_score']})"
            )

        print(
            "\nCourses to expand:"
        )

        for item in plan[
            "courses_to_expand"
        ][:5]:

            print(
                f"  - {item['course_name']}"
            )

        print(
            "\nCourses to review:"
        )

        for item in plan[
            "courses_to_review"
        ][:5]:

            print(
                f"  - {item['course_name']}"
            )

        print(
            "\nEmerging opportunities:"
        )

        for item in plan[
            "emerging_opportunities"
        ][:5]:

            print(
                f"  - {item['skill']}"
            )

    # ---------------------------------------------------------
    # Save all district plans into one flat analytical file.
    # ---------------------------------------------------------

    plans = []

    for district in districts:

        plan = build_district_training_plan(
            alignment=alignment,
            training=training,
            district=district,
            top_n=10,
        )

        for action_type, key in [
            (
                "PRIORITY_SKILL",
                "priority_skills",
            ),
            (
                "EXPAND_COURSE",
                "courses_to_expand",
            ),
            (
                "REVIEW_COURSE",
                "courses_to_review",
            ),
            (
                "EMERGING_OPPORTUNITY",
                "emerging_opportunities",
            ),
        ]:

            for item in plan[key]:

                plans.append(
                    {
                        "district": district,
                        "action_type": action_type,
                        **item,
                    }
                )

    pd.DataFrame(
        plans
    ).to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print(
        f"Saved: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
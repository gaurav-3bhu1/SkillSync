from src.data_loader import load_jobs, load_skills
from src.skill_extractor import SkillExtractor
from src.job_skill_mapper import build_job_skill_mapping
from src.trend_engine import (
    calculate_monthly_skill_trends,
    compare_recent_vs_previous,
    get_emerging_skills,
)


def main():
    jobs = load_jobs()
    skills = load_skills()

    extractor = SkillExtractor(skills)

    job_skill_mapping = build_job_skill_mapping(
        jobs,
        extractor,
    )

    print("=" * 60)
    print("SkillSync - Skill Trend Analysis")
    print("=" * 60)

    role = input(
        "Enter role (blank for all roles): "
    ).strip()

    location = input(
        "Enter location (blank for all locations): "
    ).strip()

    role_filter = role if role else None

    location_filter = (
        location if location else None
    )

    monthly_trends = calculate_monthly_skill_trends(
        job_skill_mapping,
        role=role_filter,
        location=location_filter,
    )

    comparison = compare_recent_vs_previous(
        job_skill_mapping,
        role=role_filter,
        location=location_filter,
        window_days=30,
    )

    emerging = get_emerging_skills(
        comparison
    )

    if monthly_trends.empty:
        print("\nNo matching data found.")
        return

    print("\n" + "=" * 60)
    print("MONTHLY SKILL DEMAND")
    print("=" * 60)

    print(
        monthly_trends.to_string(
            index=False
        )
    )

    print("\n" + "=" * 60)
    print("RECENT VS PREVIOUS PERIOD")
    print("=" * 60)

    print(
        comparison.to_string(
            index=False
        )
    )

    print("\n" + "=" * 60)
    print("EMERGING SKILLS")
    print("=" * 60)

    if emerging.empty:
        print(
            "No emerging skills detected "
            "using the current prototype threshold."
        )
    else:
        print(
            emerging[
                [
                    "skill",
                    "recent_job_count",
                    "recent_demand_percentage",
                    "change_percentage_points",
                    "trend",
                ]
            ].to_string(index=False)
        )

    monthly_trends.to_csv(
        "data/processed/monthly_skill_trends.csv",
        index=False,
    )

    comparison.to_csv(
        "data/processed/skill_trend_comparison.csv",
        index=False,
    )

    print(
        "\nSaved trend analysis to "
        "data/processed/"
    )


if __name__ == "__main__":
    main()
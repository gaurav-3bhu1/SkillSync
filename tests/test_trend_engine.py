import pandas as pd

from src.trend_engine import (
    calculate_monthly_skill_trends,
    compare_recent_vs_previous,
    get_emerging_skills,
)


def build_test_data():
    return pd.DataFrame(
        [
            # Previous period
            {
                "job_id": "J001",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Java",
                "posted_date": "2026-07-10",
            },
            {
                "job_id": "J002",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Java",
                "posted_date": "2026-07-20",
            },
            {
                "job_id": "J003",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Docker",
                "posted_date": "2026-07-25",
            },

            # Recent period
            {
                "job_id": "J004",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Java",
                "posted_date": "2026-08-10",
            },
            {
                "job_id": "J005",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Docker",
                "posted_date": "2026-08-15",
            },
            {
                "job_id": "J006",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "Docker",
                "posted_date": "2026-08-20",
            },
            {
                "job_id": "J007",
                "role": "Backend Developer",
                "location": "Pune",
                "skill": "AWS",
                "posted_date": "2026-08-25",
            },
        ]
    )


def test_monthly_skill_trends():

    df = build_test_data()

    result = calculate_monthly_skill_trends(df)

    print("\nMonthly trends:")
    print(result)

    assert not result.empty

    assert set(result["month"]) == {
        "2026-07",
        "2026-08",
    }

    august_docker = result[
        (result["month"] == "2026-08")
        & (result["skill"] == "Docker")
    ].iloc[0]

    assert august_docker["job_count"] == 2
    assert august_docker["total_jobs"] == 4
    assert august_docker["demand_percentage"] == 50.0


def test_recent_vs_previous():

    df = build_test_data()

    result = compare_recent_vs_previous(
        df,
        role="Backend Developer",
        location="Pune",
        window_days=30,
    )

    print("\nRecent vs previous:")
    print(result)

    docker = result[
        result["skill"] == "Docker"
    ].iloc[0]

    assert docker["previous_job_count"] == 1
    assert docker["recent_job_count"] == 2

    assert docker["previous_demand_percentage"] == 33.33
    assert docker["recent_demand_percentage"] == 50.0

    assert docker["change_percentage_points"] == 16.67
    assert docker["trend"] == "Emerging"


def test_emerging_skills():

    df = build_test_data()

    comparison = compare_recent_vs_previous(
        df,
        window_days=30,
    )

    emerging = get_emerging_skills(
        comparison
    )

    print("\nEmerging skills:")
    print(emerging)

    assert "Docker" in set(
        emerging["skill"]
    )


if __name__ == "__main__":

    test_monthly_skill_trends()
    test_recent_vs_previous()
    test_emerging_skills()

    print(
        "\nAll trend engine tests passed."
    )
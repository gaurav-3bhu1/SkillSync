import pandas as pd

from src.district_training_plan import (
    build_district_training_plan,
)


def test_district_training_plan():

    alignment = pd.DataFrame(
        [
            {
                "location": "Pune",
                "skill_id": "Industrial IoT",
                "demand_job_count": 40,
                "allocated_skill_seats": 5,
                "district_total_jobs": 100,
                "supply_status": "LOW_CAPACITY",
                "priority_band": "HIGH_PRIORITY",
            },
            {
                "location": "Pune",
                "skill_id": "Tally",
                "demand_job_count": 3,
                "allocated_skill_seats": 100,
                "district_total_jobs": 100,
                "supply_status": "ADEQUATE_OR_HIGH_CAPACITY",
                "priority_band": "MONITOR",
            },
        ]
    )

    training = pd.DataFrame(
        [
            {
                "course_id": "C001",
                "course_name": "Industrial IoT Technician",
                "location": "Pune",
                "skill": "Industrial IoT",
                "annual_intake_seats": 5,
                "placement_rate_pct": 72,
            },
            {
                "course_id": "C002",
                "course_name": "Office Accounting",
                "location": "Pune",
                "skill": "Tally",
                "annual_intake_seats": 100,
                "placement_rate_pct": 25,
            },
        ]
    )

    plan = build_district_training_plan(
        alignment,
        training,
        district="Pune",
    )

    assert plan["district"] == "Pune"

    assert len(
        plan["priority_skills"]
    ) > 0

    assert (
        plan["priority_skills"][0]["skill"]
        == "Industrial IoT"
    )

    assert len(
        plan["courses_to_expand"]
    ) > 0

    assert (
        plan["courses_to_expand"][0][
            "course_name"
        ]
        == "Industrial IoT Technician"
    )

    assert len(
        plan["courses_to_review"]
    ) > 0

    assert (
        plan["courses_to_review"][0][
            "course_name"
        ]
        == "Office Accounting"
    )

    print(
        "District training plan tests passed."
    )


if __name__ == "__main__":
    test_district_training_plan()
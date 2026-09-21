from src.external_data_adapter import (
    load_external_jobs,
    load_external_training_supply,
    standardize_jobs,
    standardize_training_supply,
)


def test_external_jobs():

    raw = load_external_jobs()
    canonical = standardize_jobs(raw)

    print("\nExternal jobs:")
    print(
        f"Raw rows: {len(raw)}"
    )

    print(
        f"Canonical rows: {len(canonical)}"
    )

    assert len(raw) == 10250
    assert len(canonical) == 10250

    assert (
        canonical["job_id"]
        .nunique()
        == 10250
    )

    assert list(
        canonical.columns
    ) == [
        "job_id",
        "title",
        "role",
        "location",
        "industry",
        "industrial_cluster",
        "description",
        "required_skills",
        "nsqf_level",
        "proficiency",
        "experience_years",
        "education",
        "salary_monthly_inr",
        "company_name",
        "employment_type",
        "posting_source",
        "demand_trend",
        "automation_risk_index",
    ]


def test_external_training_supply():

    raw = load_external_training_supply()
    canonical = standardize_training_supply(
        raw
    )

    print("\nExternal training supply:")
    print(
        f"Raw rows: {len(raw)}"
    )

    print(
        f"Canonical rows: {len(canonical)}"
    )

    assert len(raw) == 436
    assert len(canonical) == 436

    assert (
        canonical["iti_id"]
        .nunique()
        == 158
    )

    assert list(
        canonical.columns
    ) == [
        "iti_id",
        "iti_name",
        "location",
        "industrial_cluster",
        "tier",
        "iti_type",
        "course_name",
        "industry",
        "nsqf_level",
        "duration_months",
        "annual_intake_seats",
        "placement_rate_pct",
        "skills_taught",
        "skills_gap",
        "demand_alignment",
        "mismatch_flag",
    ]


def test_district_normalization():

    jobs = standardize_jobs(
        load_external_jobs()
    )

    courses = standardize_training_supply(
        load_external_training_supply()
    )

    job_locations = set(
        jobs["location"]
    )

    course_locations = set(
        courses["location"]
    )

    assert (
        "Chhatrapati Sambhaji Nagar"
        in job_locations
    )

    assert (
        "Chhatrapati Sambhaji Nagar"
        in course_locations
    )

    assert (
        "Dharashiv"
        in job_locations
    )


if __name__ == "__main__":

    test_external_jobs()
    test_external_training_supply()
    test_district_normalization()

    print(
        "\nExternal data adapter tests passed."
    )
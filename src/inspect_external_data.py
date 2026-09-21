from src.external_data_adapter import (
    load_external_jobs,
    load_external_training_supply,
    standardize_jobs,
    standardize_training_supply,
)


def main():

    jobs_raw = load_external_jobs()
    jobs = standardize_jobs(jobs_raw)

    courses_raw = load_external_training_supply()
    courses = standardize_training_supply(
        courses_raw
    )

    print("=" * 70)
    print("SkillSync - External Data Adapter")
    print("=" * 70)

    print("\nJOB DATA")
    print(
        f"Records: {len(jobs)}"
    )

    print(
        f"Districts: "
        f"{jobs['location'].nunique()}"
    )

    print(
        f"Sectors: "
        f"{jobs['industry'].nunique()}"
    )

    print("\nSample canonical job:")

    print(
        jobs.iloc[0].to_dict()
    )

    print("\nTRAINING DATA")
    print(
        f"Records: {len(courses)}"
    )

    print(
        f"ITIs: "
        f"{courses['iti_id'].nunique()}"
    )

    print(
        f"Courses: "
        f"{courses['course_name'].nunique()}"
    )

    print(
        f"Districts: "
        f"{courses['location'].nunique()}"
    )

    print("\nSample canonical training record:")

    print(
        courses.iloc[0].to_dict()
    )


if __name__ == "__main__":
    main()
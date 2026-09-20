from src.data_loader import load_jobs, load_skills
from src.demand_engine import calculate_filtered_demand
from src.job_skill_mapper import build_job_skill_mapping
from src.skill_extractor import SkillExtractor


def main() -> None:

    jobs = load_jobs()
    skills = load_skills()

    extractor = SkillExtractor(skills)

    mapping = build_job_skill_mapping(
        jobs,
        extractor,
    )

    role = input(
        "Enter role: "
    ).strip()

    location = input(
        "Enter location: "
    ).strip()

    result = calculate_filtered_demand(
        mapping,
        role=role,
        location=location,
    )

    print("\nSkill Demand")
    print("=" * 50)

    if result.empty:
        print(
            "No matching jobs found."
        )
        return

    print(
        result.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
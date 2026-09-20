from pathlib import Path
from src.data_loader import load_jobs, load_skills
from src.demand_engine import calculate_filtered_demand
from src.job_skill_mapper import build_job_skill_mapping
from src.skill_extractor import SkillExtractor

def main() -> None:

    jobs = load_jobs()
    skills = load_skills()

    extractor = SkillExtractor(skills)

    job_skill_df = build_job_skill_mapping(
        jobs,
        extractor,
    )

    output_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "job_skill_mapping.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    job_skill_df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved job-skill mapping to: {output_path}"
    )

    print("=" * 60)
    print("SkillSync - Industry Skill Demand")
    print("=" * 60)

    print("\nTOP SKILLS - ALL JOBS")

    overall = calculate_filtered_demand(
        job_skill_df
    )

    print(
        overall.head(10).to_string(
            index=False
        )
    )

    print("\n" + "=" * 60)

    print("\nBACKEND DEVELOPER - PUNE")

    backend_pune = calculate_filtered_demand(
        job_skill_df,
        role="Backend Developer",
        location="Pune",
    )

    print(
        backend_pune.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
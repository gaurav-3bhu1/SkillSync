from src.alignment_engine import (
    calculate_course_alignment,
    prioritize_skill_gaps,
)
from src.course_skill_mapper import build_course_skill_mapping
from src.data_loader import (
    load_courses,
    load_jobs,
    load_skills,
)
from src.demand_engine import calculate_filtered_demand
from src.job_skill_mapper import build_job_skill_mapping
from src.skill_extractor import SkillExtractor


def main() -> None:

    jobs = load_jobs()
    courses = load_courses()
    skills = load_skills()

    # -------------------------
    # BUILD JOB-SKILL MAPPING
    # -------------------------

    extractor = SkillExtractor(skills)

    job_skill_df = build_job_skill_mapping(
        jobs,
        extractor,
    )

    # -------------------------
    # USER INPUT
    # -------------------------

    role = input(
        "Enter role: "
    ).strip()

    location = input(
        "Enter location: "
    ).strip()

    course_id = input(
        "Enter course ID: "
    ).strip()

    # -------------------------
    # DEMAND
    # -------------------------

    demand_df = calculate_filtered_demand(
        job_skill_df,
        role=role,
        location=location,
    )

    if demand_df.empty:
        print(
            "\nNo matching jobs found."
        )
        return

    # -------------------------
    # COURSE
    # -------------------------

    matching_courses = courses[
        courses["course_id"] == course_id
    ]

    if matching_courses.empty:
        print(
            f"\nCourse '{course_id}' not found."
        )
        return

    course = matching_courses.iloc[0]

    course_skills = [
        skill.strip()
        for skill in str(
            course["skills"]
        ).split(";")
        if skill.strip()
    ]

    # -------------------------
    # ALIGNMENT
    # -------------------------

    alignment = calculate_course_alignment(
        course_skills,
        demand_df,
    )

    gaps = prioritize_skill_gaps(
        alignment["missing_skills"],
        demand_df,
    )

    # -------------------------
    # OUTPUT
    # -------------------------

    print("\n" + "=" * 60)
    print("SKILLSYNC - COURSE ALIGNMENT")
    print("=" * 60)

    print(f"\nRole:     {role}")
    print(f"Location: {location}")
    print(f"Course:   {course['course_name']}")
    print(f"Course ID: {course_id}")

    print("\n" + "-" * 60)
    print("INDUSTRY DEMAND")
    print("-" * 60)

    print(
        demand_df.head(10).to_string(
            index=False
        )
    )

    print("\n" + "-" * 60)
    print("COURSE SKILLS")
    print("-" * 60)

    print(", ".join(course_skills))

    print("\n" + "-" * 60)
    print("ALIGNMENT")
    print("-" * 60)

    print(
        f"Alignment Score: "
        f"{alignment['alignment_score']}%"
    )

    print("\nCovered skills:")
    for skill in alignment["covered_skills"]:
        print(f"  ✓ {skill}")

    print("\nMissing skills:")
    for skill in alignment["missing_skills"]:
        print(f"  ✗ {skill}")

    print("\n" + "-" * 60)
    print("PRIORITIZED SKILL GAPS")
    print("-" * 60)

    if gaps.empty:
        print("No skill gaps detected.")
    else:
        print(
            gaps[
                [
                    "skill",
                    "demand_percentage",
                    "priority",
                ]
            ].to_string(index=False)
        )

    print("\n" + "-" * 60)
    print("CURRICULUM RECOMMENDATION")
    print("-" * 60)

    if gaps.empty:
        print(
            "Course is well aligned with "
            "the selected industry demand."
        )
    else:
        print(
            "Consider adding the following skills:"
        )

        for _, row in gaps.iterrows():

            print(
                f"  → {row['skill']} "
                f"({row['priority']} priority)"
            )


if __name__ == "__main__":
    main()
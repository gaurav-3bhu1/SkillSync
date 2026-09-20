import pandas as pd

from src.hybrid_skill_extractor import HybridSkillExtractor


def build_test_skills():

    return pd.DataFrame(
        [
            {
                "skill_id": "S001",
                "skill_name": "Java",
                "category": "Programming",
                "aliases": "java;java se;java programming",
            },
            {
                "skill_id": "S011",
                "skill_name": "Spring Boot",
                "category": "Backend",
                "aliases": "spring boot;springboot",
            },
            {
                "skill_id": "S019",
                "skill_name": "Docker",
                "category": "DevOps",
                "aliases": "docker;containerization",
            },
            {
                "skill_id": "S021",
                "skill_name": "AWS",
                "category": "Cloud",
                "aliases": "aws;amazon web services",
            },
        ]
    )


def test_exact_match_is_preserved():

    skills = build_test_skills()

    extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
    )

    results = extractor.extract_with_metadata(
        "Java developer using Spring Boot."
    )

    print("\nExact + semantic results:")
    print(results)

    skills_found = {
        item["skill"]
        for item in results
    }

    assert "Java" in skills_found
    assert "Spring Boot" in skills_found

    exact_results = [
        item
        for item in results
        if item["source"] == "exact"
    ]

    assert len(exact_results) >= 2


def test_semantic_match():

    skills = build_test_skills()

    extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
    )

    results = extractor.extract_with_metadata(
        "container based application deployment"
    )

    print("\nSemantic result:")
    print(results)

    skills_found = {
        item["skill"]
        for item in results
    }

    assert "Docker" in skills_found

    docker_result = next(
        item
        for item in results
        if item["skill"] == "Docker"
    )

    assert docker_result["source"] == "semantic"
    assert docker_result["confidence"] >= 0.55


def test_extract_returns_strings():

    skills = build_test_skills()

    extractor = HybridSkillExtractor(
        skills,
        semantic_threshold=0.55,
    )

    results = extractor.extract(
        "Java backend development"
    )

    print("\nSimple extract result:")
    print(results)

    assert all(
        isinstance(skill, str)
        for skill in results
    )


if __name__ == "__main__":

    test_exact_match_is_preserved()
    test_semantic_match()
    test_extract_returns_strings()

    print(
        "\nAll hybrid skill extractor tests passed."
    )
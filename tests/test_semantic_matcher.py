import pandas as pd

from src.semantic_matcher import SemanticSkillMatcher


def main():

    skills = pd.DataFrame(
        [
            {
                "skill_id": "S001",
                "skill_name": "Java",
                "category": "Programming",
                "aliases": "java",
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

    matcher = SemanticSkillMatcher(
        skills,
        threshold=0.40,
    )

    test_texts = [
        "Java backend programming",
        "container based application deployment",
        "Amazon cloud infrastructure",
    ]

    for text in test_texts:

        results = matcher.match(
            text,
            top_k=3,
        )

        print("\nTEXT:")
        print(text)

        print("\nMATCHES:")

        for result in results:
            print(
                f"  {result['skill']:<20}"
                f"{result['score']:.4f}"
            )


if __name__ == "__main__":
    main()
from src.role_normalizer import normalize_role


def main() -> None:

    test_cases = {
        "Backend Developer": "Backend Developer",
        "Senior Backend Developer": "Backend Developer",
        "Java Developer": "Backend Developer",
        "Node.js Developer": "Backend Developer",
        "API Developer": "Backend Developer",
        "Software Engineer": "Backend Developer",

        "Frontend Developer": "Frontend Developer",
        "React Developer": "Frontend Developer",
        "UI Developer": "Frontend Developer",

        "Data Analyst": "Data Analyst",
        "BI Analyst": "Data Analyst",

        "Data Scientist": "Data Scientist",
        "Data Engineer": "Data Engineer",

        "DevOps Engineer": "Cloud / DevOps",
        "Cloud Engineer": "Cloud / DevOps",
        "Site Reliability Engineer": "Cloud / DevOps",

        "QA Automation Engineer": "QA / Test Automation",

        "Product Manager": "Product Management",

        "Technical Support Engineer": "Technical Support",
    }

    for title, expected in test_cases.items():

        actual = normalize_role(title)

        print(f"{title:35} -> {actual}")

        assert actual == expected, (
            f"Expected '{expected}', got '{actual}'"
        )

    print("\nAll role normalization tests passed.")


if __name__ == "__main__":
    main()
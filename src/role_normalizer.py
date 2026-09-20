from __future__ import annotations

import re


ROLE_RULES = [
    (
        "Full Stack Developer",
        [
            "full stack",
            "fullstack",
        ],
    ),
    (
        "Backend Developer",
        [
            "backend",
            "java developer",
            "node.js developer",
            "node developer",
            "api developer",
            "software engineer",
        ],
    ),
    (
        "Frontend Developer",
        [
            "frontend",
            "front end",
            "react developer",
            "ui developer",
        ],
    ),
    (
        "Data Analyst",
        [
            "data analyst",
            "bi analyst",
        ],
    ),
    (
        "Data Scientist",
        [
            "data scientist",
        ],
    ),
    (
        "Data Engineer",
        [
            "data engineer",
        ],
    ),
    (
        "Cloud / DevOps",
        [
            "devops",
            "cloud engineer",
            "cloud architect",
            "site reliability",
            "sre",
        ],
    ),
    (
        "QA / Test Automation",
        [
            "qa",
            "quality assurance",
            "test automation",
        ],
    ),
    (
        "Product Management",
        [
            "product manager",
            "product management",
        ],
    ),
    (
        "Technical Support",
        [
            "technical support",
            "support engineer",
        ],
    ),
]


def normalize_role(title: str) -> str:
    """
    Convert a raw job title into a canonical role family.
    """

    if not isinstance(title, str):
        return "Other"

    normalized = re.sub(
        r"\s+",
        " ",
        title.lower().strip(),
    )

    for canonical_role, patterns in ROLE_RULES:

        for pattern in patterns:

            if pattern in normalized:
                return canonical_role

    return "Other"
from __future__ import annotations

import calendar
import random
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

SOURCE_PATH = RAW_DIR / "jobs.csv"
OUTPUT_PATH = RAW_DIR / "jobs_expanded.csv"

RANDOM_SEED = 20260920

LOCATIONS = [
    "Pune",
    "Mumbai",
    "Nagpur",
    "Nashik",
]

INDUSTRIES = [
    "IT Services",
    "SaaS",
    "FinTech",
    "HealthTech",
    "E-commerce",
    "EdTech",
    "Manufacturing Technology",
    "Logistics & Mobility",
]

# 22 title variants x 10 records each = 220 new jobs.
TITLE_TEMPLATES = {
    "Backend Developer": {
        "required": [
            "Java",
            "Spring Boot",
            "SQL",
            "REST API",
        ],
        "optional": [
            "PostgreSQL",
            "Docker",
            "AWS",
            "Git",
            "Jenkins",
            "GraphQL",
            "Node.js",
            "FastAPI",
        ],
    },
    "Backend Engineer": {
        "required": [
            "Java",
            "Spring Boot",
            "SQL",
            "REST API",
        ],
        "optional": [
            "PostgreSQL",
            "Docker",
            "AWS",
            "Git",
            "Jenkins",
            "GraphQL",
            "Node.js",
        ],
    },
    "Senior Backend Developer": {
        "required": [
            "Java",
            "Spring Boot",
            "SQL",
            "REST API",
            "PostgreSQL",
        ],
        "optional": [
            "Docker",
            "AWS",
            "Git",
            "Jenkins",
            "GraphQL",
            "Kubernetes",
        ],
    },
    "Java Developer": {
        "required": [
            "Java",
            "Spring Boot",
            "SQL",
            "PostgreSQL",
            "REST API",
        ],
        "optional": [
            "Docker",
            "AWS",
            "Git",
            "Jenkins",
            "Kubernetes",
        ],
    },
    "Node.js Developer": {
        "required": [
            "Node.js",
            "JavaScript",
            "REST API",
            "MongoDB",
            "Express.js",
        ],
        "optional": [
            "TypeScript",
            "Docker",
            "AWS",
            "Git",
            "GraphQL",
        ],
    },
    "API Developer": {
        "required": [
            "REST API",
            "Java",
            "Spring Boot",
            "SQL",
        ],
        "optional": [
            "FastAPI",
            "Node.js",
            "Docker",
            "AWS",
            "GraphQL",
            "PostgreSQL",
            "Git",
        ],
    },
    "Frontend Developer": {
        "required": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Git",
        ],
        "optional": [
            "TypeScript",
            "Tailwind CSS",
            "Node.js",
            "Angular",
        ],
    },
    "React Developer": {
        "required": [
            "React",
            "JavaScript",
            "HTML",
            "CSS",
        ],
        "optional": [
            "TypeScript",
            "Tailwind CSS",
            "Git",
            "Node.js",
        ],
    },
    "UI Developer": {
        "required": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Tailwind CSS",
        ],
        "optional": [
            "TypeScript",
            "Git",
            "Angular",
        ],
    },
    "Frontend Engineer": {
        "required": [
            "React",
            "TypeScript",
            "JavaScript",
            "HTML",
            "CSS",
        ],
        "optional": [
            "Tailwind CSS",
            "Git",
            "Node.js",
            "Angular",
        ],
    },
    "Full Stack Developer": {
        "required": [
            "React",
            "JavaScript",
            "Node.js",
            "REST API",
            "SQL",
        ],
        "optional": [
            "PostgreSQL",
            "Docker",
            "AWS",
            "Git",
            "TypeScript",
            "Express.js",
        ],
    },
    "Full Stack Engineer": {
        "required": [
            "React",
            "Node.js",
            "JavaScript",
            "REST API",
            "SQL",
        ],
        "optional": [
            "PostgreSQL",
            "Docker",
            "AWS",
            "Git",
            "TypeScript",
            "Express.js",
        ],
    },
    "Data Analyst": {
        "required": [
            "Python",
            "SQL",
            "Excel",
            "Pandas",
            "Data Visualization",
        ],
        "optional": [
            "Power BI",
            "NumPy",
            "Data Analysis",
            "Git",
        ],
    },
    "BI Analyst": {
        "required": [
            "Excel",
            "Power BI",
            "SQL",
            "Data Visualization",
        ],
        "optional": [
            "Python",
            "Pandas",
            "Data Analysis",
            "Git",
        ],
    },
    "Data Scientist": {
        "required": [
            "Python",
            "Pandas",
            "NumPy",
            "Machine Learning",
        ],
        "optional": [
            "Deep Learning",
            "Natural Language Processing",
            "SQL",
            "Data Analysis",
            "Docker",
        ],
    },
    "Data Engineer": {
        "required": [
            "Python",
            "SQL",
            "PostgreSQL",
            "Pandas",
            "Docker",
        ],
        "optional": [
            "AWS",
            "Linux",
            "Git",
            "Terraform",
            "Kubernetes",
        ],
    },
    "DevOps Engineer": {
        "required": [
            "Docker",
            "Kubernetes",
            "AWS",
            "Linux",
            "Git",
        ],
        "optional": [
            "Terraform",
            "CI/CD",
            "Jenkins",
            "Azure",
            "GCP",
            "PowerShell",
        ],
    },
    "Cloud Engineer": {
        "required": [
            "AWS",
            "Linux",
            "Docker",
            "Terraform",
        ],
        "optional": [
            "Kubernetes",
            "Azure",
            "GCP",
            "Git",
            "CI/CD",
        ],
    },
    "Site Reliability Engineer": {
        "required": [
            "Docker",
            "Kubernetes",
            "AWS",
            "Linux",
            "Git",
        ],
        "optional": [
            "Terraform",
            "CI/CD",
            "Jenkins",
            "PowerShell",
            "Azure",
        ],
    },
    "QA Automation Engineer": {
        "required": [
            "Java",
            "Python",
            "SQL",
            "Git",
            "CI/CD",
        ],
        "optional": [
            "Jenkins",
            "Docker",
            "PostgreSQL",
            "AWS",
        ],
    },
    "Product Manager": {
        "required": [
            "Excel",
            "SQL",
            "Data Analysis",
            "Data Visualization",
        ],
        "optional": [
            "Power BI",
            "Python",
            "Git",
            "PostgreSQL",
        ],
    },
    "Technical Support Engineer": {
        "required": [
            "Linux",
            "PowerShell",
            "SQL",
            "Git",
        ],
        "optional": [
            "AWS",
            "PostgreSQL",
            "Python",
            "Docker",
        ],
    },
}


RISING_SKILLS = {
    "Docker",
    "Kubernetes",
    "AWS",
    "Terraform",
    "CI/CD",
    "TypeScript",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Power BI",
}


SKILL_PHRASES = {
    "Java": [
        "Java",
        "Java programming",
    ],
    "Spring Boot": [
        "Spring Boot",
        "SpringBoot",
    ],
    "PostgreSQL": [
        "PostgreSQL",
        "Postgres",
    ],
    "Node.js": [
        "Node.js",
        "NodeJS",
    ],
    "REST API": [
        "REST API",
        "RESTful APIs",
    ],
    "React": [
        "React",
        "ReactJS",
    ],
    "JavaScript": [
        "JavaScript",
        "JS",
    ],
    "HTML": [
        "HTML",
        "HTML5",
    ],
    "CSS": [
        "CSS",
        "CSS3",
    ],
    "Docker": [
        "Docker",
        "containerized deployments",
    ],
    "Kubernetes": [
        "Kubernetes",
        "K8s",
    ],
    "AWS": [
        "AWS",
        "Amazon Web Services",
    ],
    "Azure": [
        "Azure",
        "Microsoft Azure",
    ],
    "GCP": [
        "GCP",
        "Google Cloud Platform",
    ],
    "Git": [
        "Git",
        "Git version control",
    ],
    "Power BI": [
        "Power BI",
        "PowerBI",
    ],
    "Excel": [
        "Excel",
        "Microsoft Excel",
    ],
    "Machine Learning": [
        "Machine Learning",
        "ML",
    ],
    "Deep Learning": [
        "Deep Learning",
        "DL",
    ],
    "Natural Language Processing": [
        "Natural Language Processing",
        "NLP",
    ],
    "Data Analysis": [
        "Data Analysis",
        "data analytics",
    ],
    "Data Visualization": [
        "Data Visualization",
        "visualization",
    ],
    "FastAPI": [
        "FastAPI",
        "Fast API",
    ],
    "Express.js": [
        "Express.js",
        "Express",
    ],
    "CI/CD": [
        "CI/CD",
        "continuous integration and deployment",
    ],
    "Jenkins": [
        "Jenkins",
    ],
    "Terraform": [
        "Terraform",
        "infrastructure as code",
    ],
    "PowerShell": [
        "PowerShell",
    ],
    "GitLab": [
        "GitLab",
    ],
    "Tailwind CSS": [
        "Tailwind CSS",
        "Tailwind",
    ],
    "Angular": [
        "Angular",
    ],
    "MongoDB": [
        "MongoDB",
        "Mongo",
    ],
    "Python": [
        "Python",
        "Python 3",
    ],
    "Pandas": [
        "Pandas",
    ],
    "NumPy": [
        "NumPy",
        "numpy",
    ],
    "SQL": [
        "SQL",
        "relational queries",
    ],
}


ROLE_INTROS = {
    "Backend": [
        "Build and maintain server-side applications for business products.",
        "Develop reliable backend services and APIs for production systems.",
        "Design and maintain scalable server-side components.",
    ],
    "Frontend": [
        "Develop responsive user interfaces for web products.",
        "Build accessible and performant frontend applications.",
        "Implement reusable interfaces for customer-facing web applications.",
    ],
    "Full Stack": [
        "Build end-to-end web applications across frontend and backend layers.",
        "Develop product features across the full application stack.",
        "Work across user interfaces, APIs, and data services.",
    ],
    "Data": [
        "Analyze business data and support data-driven product decisions.",
        "Work with structured datasets to produce actionable insights.",
        "Build data workflows and analytical solutions for business teams.",
    ],
    "DevOps": [
        "Build and maintain cloud infrastructure and deployment workflows.",
        "Improve reliability, automation, and deployment processes.",
        "Operate production infrastructure and engineering delivery pipelines.",
    ],
    "QA": [
        "Develop automated quality checks for software products.",
        "Improve test automation and software release quality.",
        "Create reliable automated validation workflows.",
    ],
    "Product": [
        "Work with engineering and business teams to define product priorities.",
        "Use product and business data to guide feature decisions.",
        "Translate customer needs into measurable product improvements.",
    ],
    "Support": [
        "Support production systems and troubleshoot technical issues.",
        "Assist customers and engineering teams with technical operations.",
        "Monitor application issues and help maintain reliable services.",
    ],
}


def role_group(title: str) -> str:
    if any(
        token in title
        for token in [
            "Backend",
            "Java Developer",
            "Node.js Developer",
            "API Developer",
        ]
    ):
        return "Backend"

    if any(
        token in title
        for token in [
            "Frontend",
            "React Developer",
            "UI Developer",
        ]
    ):
        return "Frontend"

    if "Full Stack" in title:
        return "Full Stack"

    if any(
        token in title
        for token in [
            "Data Analyst",
            "BI Analyst",
            "Data Scientist",
            "Data Engineer",
        ]
    ):
        return "Data"

    if any(
        token in title
        for token in [
            "DevOps",
            "Cloud Engineer",
            "Site Reliability",
        ]
    ):
        return "DevOps"

    if "QA" in title:
        return "QA"

    if "Product" in title:
        return "Product"

    if "Support" in title:
        return "Support"

    return "Backend"


def choose_skills(
    title: str,
    month_index: int,
    rng: random.Random,
) -> list[str]:

    template = TITLE_TEMPLATES[title]

    skills = list(template["required"])

    phase = month_index / 6.0

    optional = list(template["optional"])
    rng.shuffle(optional)

    for skill in optional:

        if skill in RISING_SKILLS:
            probability = 0.18 + (0.45 * phase)
        else:
            probability = 0.35

        if rng.random() < probability:
            skills.append(skill)

    if len(skills) < 5 and optional:
        for skill in optional:
            if skill not in skills:
                skills.append(skill)
                break

    return list(dict.fromkeys(skills))[:8]


def phrase_for_skill(
    skill: str,
    rng: random.Random,
) -> str:

    phrases = SKILL_PHRASES.get(
        skill,
        [skill],
    )

    return rng.choice(phrases)


def build_description(
    title: str,
    skills: list[str],
    industry: str,
    location: str,
    rng: random.Random,
) -> str:

    group = role_group(title)

    intro = rng.choice(
        ROLE_INTROS[group]
    )

    skill_phrases = [
        phrase_for_skill(skill, rng)
        for skill in skills
    ]

    if len(skill_phrases) >= 3:
        first_skills = ", ".join(
            skill_phrases[:-1]
        )
        first_sentence = (
            f"Key requirements include "
            f"{first_skills}, and "
            f"{skill_phrases[-1]}."
        )
    else:
        first_sentence = (
            "Key requirements include "
            + ", ".join(skill_phrases)
            + "."
        )

    context_templates = [
        (
            f"The role supports "
            f"{industry} products in {location}."
        ),
        (
            f"The team delivers technology "
            f"solutions for the {industry} sector."
        ),
        (
            f"The position contributes to "
            f"production systems serving {industry} customers."
        ),
    ]

    context = rng.choice(
        context_templates
    )

    closing_templates = [
        "Candidates should be comfortable working in agile engineering teams.",
        "Experience with production systems and collaborative development is expected.",
        "The role involves cross-functional collaboration and continuous improvement.",
        "Practical project experience and strong problem-solving skills are valued.",
    ]

    closing = rng.choice(
        closing_templates
    )

    return (
        f"{intro} "
        f"{first_sentence} "
        f"{context} "
        f"{closing}"
    )


def generate_date(
    year: int,
    month: int,
    rng: random.Random,
) -> str:

    last_day = calendar.monthrange(
        year,
        month,
    )[1]

    if year == 2026 and month == 9:
        last_day = 20

    day = rng.randint(
        1,
        last_day,
    )

    return (
        f"{year:04d}-"
        f"{month:02d}-"
        f"{day:02d}"
    )


def next_job_number(
    existing_ids: set[str],
) -> int:

    numeric_ids = []

    for job_id in existing_ids:

        match = re.fullmatch(
            r"J(\d+)",
            str(job_id).strip(),
        )

        if match:
            numeric_ids.append(
                int(match.group(1))
            )

    return (
        max(numeric_ids)
        if numeric_ids
        else 0
    ) + 1


def main():

    rng = random.Random(
        RANDOM_SEED
    )

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Missing source file: {SOURCE_PATH}"
        )

    jobs = pd.read_csv(
        SOURCE_PATH
    )

    if len(jobs) != 30:
        raise ValueError(
            "jobs.csv must contain the original 30-job "
            "base dataset before running this generator. "
            f"Found {len(jobs)} jobs."
        )

    required_columns = {
        "job_id",
        "title",
        "location",
        "industry",
        "description",
        "posted_date",
    }

    missing = (
        required_columns
        - set(jobs.columns)
    )

    if missing:
        raise ValueError(
            "jobs.csv is missing columns: "
            f"{sorted(missing)}"
        )

    existing_ids = set(
        jobs["job_id"]
        .astype(str)
    )

    start_id = next_job_number(
        existing_ids
    )

    # 22 titles x 10 jobs each = 220 new rows.
    titles = []

    for title in TITLE_TEMPLATES:
        titles.extend(
            [title] * 10
        )

    rng.shuffle(titles)

    # 30 jobs per month across 7 months = 210
    # plus 10 jobs distributed into September
    # through the title list naturally.
    month_specs = [
        (2026, 3, 30),
        (2026, 4, 30),
        (2026, 5, 30),
        (2026, 6, 30),
        (2026, 7, 30),
        (2026, 8, 30),
        (2026, 9, 40),
    ]

    month_slots = []

    for year, month, count in month_specs:
        month_slots.extend(
            [
                (year, month)
            ] * count
        )

    month_slots = month_slots[
        : len(titles)
    ]

    rng.shuffle(month_slots)

    location_pool = (
        LOCATIONS * 60
    )

    rng.shuffle(
        location_pool
    )

    industry_pool = (
        INDUSTRIES * 40
    )

    rng.shuffle(
        industry_pool
    )

    new_rows = []

    current_id = start_id

    for index, title in enumerate(
        titles
    ):

        year, month = month_slots[
            index
        ]

        location = location_pool[
            index
        ]

        industry = industry_pool[
            index
        ]

        skills = choose_skills(
            title,
            month_index=month - 3,
            rng=rng,
        )

        description = build_description(
            title=title,
            skills=skills,
            industry=industry,
            location=location,
            rng=rng,
        )

        new_rows.append(
            {
                "job_id": f"J{current_id:03d}",
                "title": title,
                "location": location,
                "industry": industry,
                "description": description,
                "posted_date": generate_date(
                    year,
                    month,
                    rng,
                ),
            }
        )

        current_id += 1

    generated = pd.DataFrame(
        new_rows
    )

    expanded = pd.concat(
        [
            jobs,
            generated,
        ],
        ignore_index=True,
    )

    expanded["posted_date"] = pd.to_datetime(
        expanded["posted_date"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    expanded.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("=" * 70)
    print("SkillSync - Prototype Job Dataset Generator")
    print("=" * 70)

    print(
        f"\nOriginal jobs: "
        f"{len(jobs)}"
    )

    print(
        f"Generated jobs: "
        f"{len(generated)}"
    )

    print(
        f"Expanded total: "
        f"{len(expanded)}"
    )

    print(
        f"\nSaved to:\n"
        f"{OUTPUT_PATH}"
    )

    print("\nGenerated jobs by location:")
    print(
        generated["location"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nGenerated jobs by month:")
    print(
        pd.to_datetime(
            generated["posted_date"]
        )
        .dt.to_period("M")
        .value_counts()
        .sort_index()
        .to_string()
    )


if __name__ == "__main__":
    main()
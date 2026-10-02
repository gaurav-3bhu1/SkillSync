from pathlib import Path
import random
import pandas as pd

path = Path("data/external/maharashtra_job_market_demand_10k.csv")
df = pd.read_csv(path)

random.seed(26134)

districts = [
    ("Pune", "Pune IT Corridor"),
    ("Mumbai", "Mumbai IT & Services"),
    ("Thane", "Thane Digital Services"),
    ("Navi Mumbai", "Navi Mumbai IT"),
    ("Nagpur", "Nagpur IT Services"),
    ("Nashik", "Nashik Digital Services"),
    ("Chhatrapati Sambhajinagar", "Aurangabad IT Services"),
    ("Kolhapur", "Kolhapur IT Services"),
    ("Ahmednagar", "Ahmednagar Digital Services"),
    ("Satara", "Satara Digital Services"),
]

roles = [
    ("Software Developer",
     ["Java", "Python", "SQL", "Git", "REST API"], 36000, 65000),

    ("Backend Developer",
     ["Java", "Spring Boot", "SQL", "REST API", "Git"], 42000, 75000),

    ("Java Developer",
     ["Java", "Spring Boot", "SQL", "REST API", "Git"], 42000, 78000),

    ("Python Developer",
     ["Python", "SQL", "REST API", "Git", "PostgreSQL"], 40000, 72000),

    ("Full Stack Developer",
     ["JavaScript", "React", "Node.js", "SQL", "Git"], 42000, 80000),

    ("Frontend Developer",
     ["JavaScript", "React", "HTML", "CSS", "Git"], 35000, 65000),

    ("Data Analyst",
     ["Python", "SQL", "Pandas", "Excel", "Power BI"], 35000, 65000),

    ("Data Engineer",
     ["Python", "SQL", "PostgreSQL", "Docker", "AWS"], 50000, 90000),

    ("ML Engineer",
     ["Python", "NumPy", "Pandas", "Scikit-learn", "SQL"], 50000, 95000),

    ("DevOps Engineer",
     ["Linux", "Git", "Docker", "AWS", "CI/CD"], 50000, 90000),

    ("Cloud Engineer",
     ["Linux", "AWS", "Docker", "Networking", "Git"], 48000, 88000),

    ("QA Automation Engineer",
     ["Java", "Selenium", "SQL", "Git", "API Testing"], 36000, 68000),

    ("Cybersecurity Analyst",
     ["Linux", "Networking", "Cybersecurity", "Python", "SIEM"], 40000, 75000),

    ("System Administrator",
     ["Linux", "Networking", "Windows Server", "Python", "Cloud"], 33000, 62000),
]

companies = [
    "Prototype Software Solutions",
    "Prototype Digital Systems",
    "Prototype Technology Services",
    "Prototype Cloud Labs",
    "Prototype Data Systems",
    "Prototype IT Services",
]

# Detect existing skill separator
sample = str(df["required_micro_skills"].dropna().iloc[0])

if ";" in sample:
    separator = "; "
elif "|" in sample:
    separator = " | "
else:
    separator = ", "

rows = []

for i in range(1800):

    district, cluster = random.choice(districts)
    role, skills, low, high = random.choice(roles)

    rows.append({
        "job_id": f"ITP{i + 1:05d}",
        "job_title": role,
        "sector": "IT & Software",
        "district": district,
        "industrial_cluster": cluster,
        "required_micro_skills": separator.join(skills),
        "nsqf_level": random.choice([4, 5, 6]),
        "proficiency_demanded": random.choice(
            ["Basic", "Intermediate", "Advanced"]
        ),
        "experience_required_years": random.choice(
            [0, 0, 1, 1, 2, 2, 3]
        ),
        "education_required": random.choice([
            "B.E./B.Tech",
            "BCA/MCA",
            "B.Sc./M.Sc. Computer Science",
            "Diploma / Degree in Computer Science",
        ]),
        "salary_monthly_inr": random.randrange(
            low, high + 1000, 1000
        ),
        "company_name": random.choice(companies),
        "employment_type": random.choice(
            ["Full-time", "Full-time", "Contract"]
        ),
        "posting_source": "Prototype IT labour-market sample",
        "demand_trend": random.choice(
            ["emerging", "emerging", "stable"]
        ),
        "automation_risk_index": random.randint(10, 35),
        "job_description_snippet": (
            f"{role} requiring "
            f"{', '.join(skills[:3])} and related "
            "software-development skills."
        ),
    })

new_df = pd.DataFrame(rows)

# Backup original dataset
backup = path.with_name(
    "maharashtra_job_market_demand_10k_backup.csv"
)

if not backup.exists():
    df.to_csv(backup, index=False)

# Append IT data
combined = pd.concat(
    [df, new_df],
    ignore_index=True
)

combined.to_csv(path, index=False)

print("Original rows:", len(df))
print("IT rows added:", len(new_df))
print("New total:", len(combined))

print("\nSector distribution:")
print(combined["sector"].value_counts())
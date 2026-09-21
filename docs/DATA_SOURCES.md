# SkillSync Data Sources

## 1. Maharashtra Job Market Dataset

File:

`data/external/maharashtra_job_market_demand_10k.csv`

Validated records:

- 10,250 job records
- 10,250 unique job IDs
- 35 districts
- 7 sectors
- 6 posting sources

Important fields:

- job_id
- job_title
- sector
- district
- industrial_cluster
- required_micro_skills
- nsqf_level
- proficiency_demanded
- experience_required_years
- education_required
- salary_monthly_inr
- company_name
- employment_type
- posting_source
- demand_trend
- automation_risk_index
- job_description_snippet

## 2. Maharashtra ITI Training Supply Dataset

File:

`data/external/maharashtra_iti_courses_supply.csv`

Validated records:

- 436 course/institute records
- 158 unique ITIs
- 34 districts
- 20 unique course names

Important fields:

- iti_id
- iti_name
- district
- industrial_cluster
- tier
- iti_type
- course_name
- sector
- nsqf_level
- duration_months
- annual_intake_seats
- placement_rate_pct
- skills_taught
- skills_gap
- demand_alignment
- mismatch_flag

## Data provenance

The datasets were supplied to the SkillSync team and are being treated as the primary prototype data source for the expanded MVP.

Before making external/public claims about official provenance, the team should retain documentation of the original source, collection method, collection date and any transformations applied.

## Important distinction

The current 250-job and 10-course datasets under `data/raw/` remain as stable regression/prototype data.

The datasets under `data/external/` are the expanded Maharashtra-scale data source.

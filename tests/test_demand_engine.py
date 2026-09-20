import pandas as pd

from src.demand_engine import calculate_skill_demand


def main() -> None:

    data = [
        {
            "job_id": "J001",
            "role": "Backend Developer",
            "location": "Pune",
            "skill": "Java",
        },
        {
            "job_id": "J001",
            "role": "Backend Developer",
            "location": "Pune",
            "skill": "SQL",
        },
        {
            "job_id": "J002",
            "role": "Backend Developer",
            "location": "Pune",
            "skill": "Java",
        },
        {
            "job_id": "J002",
            "role": "Backend Developer",
            "location": "Pune",
            "skill": "Docker",
        },
        {
            "job_id": "J003",
            "role": "Backend Developer",
            "location": "Pune",
            "skill": "Java",
        },
    ]

    df = pd.DataFrame(data)

    result = calculate_skill_demand(df)

    print(result)

    java_demand = result.loc[
        result["skill"] == "Java",
        "demand_percentage",
    ].iloc[0]

    assert java_demand == 100.0

    sql_demand = result.loc[
        result["skill"] == "SQL",
        "demand_percentage",
    ].iloc[0]

    assert sql_demand == 33.33

    print("\nDemand engine tests passed.")


if __name__ == "__main__":
    main()
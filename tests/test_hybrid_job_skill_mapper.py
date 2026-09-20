import pandas as pd

from src.hybrid_job_skill_mapper import (
    build_hybrid_job_skill_mapping,
)


class FakeHybridExtractor:

    def extract_with_metadata(self, text):

        return [
            {
                "skill": "Java",
                "source": "exact",
                "confidence": 1.0,
            },
            {
                "skill": "Docker",
                "source": "semantic",
                "confidence": 0.5629,
            },
        ]


def test_hybrid_job_skill_mapping():

    jobs = pd.DataFrame(
        [
            {
                "job_id": "J001",
                "title": "Backend Developer",
                "location": "Pune",
                "industry": "IT",
                "description": (
                    "Java backend development."
                ),
                "posted_date": "2026-08-01",
            }
        ]
    )

    extractor = FakeHybridExtractor()

    result = build_hybrid_job_skill_mapping(
        jobs,
        extractor,
    )

    print("\nHybrid mapping:")
    print(result)

    assert len(result) == 2

    assert set(result["skill"]) == {
        "Java",
        "Docker",
    }

    assert set(result["source"]) == {
        "exact",
        "semantic",
    }

    docker = result[
        result["skill"] == "Docker"
    ].iloc[0]

    assert docker["source"] == "semantic"
    assert docker["confidence"] == 0.5629


if __name__ == "__main__":

    test_hybrid_job_skill_mapping()

    print(
        "\nHybrid job-skill mapper tests passed."
    )
from src.skill_normalizer import normalize_skill


TEST_SKILLS = [
    "Allen-Bradley/Siemens S7 PLC",
    "Ladder Logic Troubleshooting",
    "VFD Parameter Configuration",
    "GTAW Pipe 6G Position",
    "G-Code & M-Code Programming",
    "Coordinate Measuring Machine (CMM)",
    "PV Module String Inverter Wiring",
    "MC4 Connector Crimping",
    "SCADA Valve Control",
    "Automated Guided Vehicle (AGV) Routing",
    "KUKA/ABB Teach Pendant",
    "AI-Quality Inspection",
    "random totally unrelated phrase",
]


def main():
    print("=" * 80)
    print("SkillSync - Skill Normalizer Test")
    print("=" * 80)

    for raw_skill in TEST_SKILLS:
        result = normalize_skill(raw_skill)

        print(
            f"\nRaw:        {result.raw_skill}"
            f"\nCanonical:  {result.canonical_skill}"
            f"\nFamily:     {result.skill_family}"
            f"\nSector:     {result.sector}"
            f"\nMethod:     {result.method}"
            f"\nConfidence: {result.confidence:.4f}"
        )


if __name__ == "__main__":
    main()
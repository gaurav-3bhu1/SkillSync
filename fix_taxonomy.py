import pandas as pd

path = "data/processed/skill_taxonomy.csv"

df = pd.read_csv(path)

fixes = {
    "SK020": (
        "Coordinate Measuring Machine (CMM)",
        "CMM inspection|coordinate measuring machine|CMM operation"
    ),
    "SK025": (
        "CAD/CAM Toolpath Reading",
        "Cimatron / Delcam 3D Reading|Cimatron|Delcam|3D drawing reading|CAD/CAM basics|Mastercam post-processing|2D blueprint reading|3D CAD modelling (SolidWorks/CATIA)|blueprint reading"
    ),
    "SK026": (
        "PV System Wiring",
        "PV Module String Inverter Wiring|PV wiring|solar PV wiring|panel wiring|solar grid interconnection"
    ),
    "SK028": (
        "Roof-Mounted Solar Installation",
        "Roof Mounting Clamping & Anchoring|solar roof mounting|PV roof mounting|rooftop module mounting|agrivoltaic installation"
    ),
    "SK029": (
        "Net Metering",
        "Net-Metering Synchronization|net metering|grid synchronization|smart metering"
    ),
    "SK030": (
        "Electrical Earthing Testing",
        "Earthing Pit Resistance Testing|earthing resistance testing|earth pit testing|earthing|earthing & bonding"
    ),
    "SK048": (
        "Machine Vision",
        "vision-guided robotics|machine vision|computer vision inspection|computer vision basics"
    ),
    "SK070": (
        "Shorthand",
        "shorthand|stenography|Pitman shorthand"
    ),
}

for skill_id, (canonical, aliases) in fixes.items():
    mask = df["skill_id"] == skill_id

    if not mask.any():
        print(f"ERROR: {skill_id} not found")
        continue

    df.loc[mask, "canonical_skill"] = canonical
    df.loc[mask, "aliases"] = aliases

df.to_csv(path, index=False)

print("\nTaxonomy repaired:\n")
print(
    df[df["skill_id"].isin(fixes.keys())][
        ["skill_id", "canonical_skill", "aliases"]
    ].to_string(index=False)
)
import pandas as pd
import json
from pathlib import Path

# Paths
CSV_PATH = Path("Dataset/railway_schedule.csv")
OUTPUT_PATH = Path("Dataset/pune_schedule.json")

# Load original railway schedule
df = pd.read_csv(CSV_PATH)

# Select Pune Junction records
pune = df[
    df["Station Code"]
    .astype(str)
    .str.strip()
    .str.upper()
    == "PUNE"
].copy()

# Clean column names
pune.columns = [col.strip() for col in pune.columns]

# Convert NaN values to None for JSON
pune = pune.where(pd.notna(pune), None)

# Convert to records
records = pune.to_dict(orient="records")

# Create output directory if needed
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Save JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print("=" * 50)
print("RailMind Pune Schedule Dataset")
print("=" * 50)
print(f"Records: {len(records)}")
print(f"Unique trains: {pune['Train No'].nunique()}")
print(f"Output: {OUTPUT_PATH.resolve()}")
print("=" * 50)
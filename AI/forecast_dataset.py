import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# RAILMIND AI - FORECAST DATASET BUILDER
# ============================================================

CROWD_PATH = Path(
    r"D:\RailMindAI\data\crowd_timeseries\crowd_features.csv"
)

OUTPUT_PATH = Path(
    r"D:\RailMindAI\data\forecast_dataset.csv"
)


# ============================================================
# LOAD CROWD DATA
# ============================================================

print("=" * 70)
print("RAILMIND AI - FORECAST DATASET BUILDER")
print("=" * 70)

df = pd.read_csv(CROWD_PATH)

print(f"\nTotal crowd rows: {len(df)}")


# ============================================================
# REMOVE ROWS WITHOUT ENOUGH HISTORY
# ============================================================

df = df[
    df["growth_rate_5s"].notna()
].copy()

df = df[
    df["crowd_mean_5s"].notna()
].copy()

print(
    f"Usable rows: {len(df)}"
)


# ============================================================
# CLEAN NUMERIC FEATURES
# ============================================================

numeric_columns = [
    "observed_crowd",
    "crowd_mean_5s",
    "crowd_max_5s",
    "crowd_min_5s",
    "crowd_change_1s",
    "crowd_change_3s",
    "crowd_change_5s",
    "growth_rate_5s",
    "acceleration"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df = df.dropna(
    subset=[
        "observed_crowd",
        "crowd_mean_5s",
        "growth_rate_5s"
    ]
).copy()


# ============================================================
# SCHEDULE PRESSURE FEATURES
# ============================================================
#
# These are scenario inputs.
#
# They represent increasing train activity around
# the current observation.
#
# Later these values will come directly from
# schedule_features.py.
# ============================================================

rng = np.random.default_rng(42)

df["schedule_movements_5min"] = rng.integers(
    0,
    6,
    size=len(df)
)

df["schedule_movements_10min"] = (
    df["schedule_movements_5min"]
    +
    rng.integers(
        0,
        7,
        size=len(df)
    )
)

df["schedule_movements_15min"] = (
    df["schedule_movements_10min"]
    +
    rng.integers(
        0,
        7,
        size=len(df)
    )
)

df["schedule_movements_30min"] = (
    df["schedule_movements_15min"]
    +
    rng.integers(
        0,
        10,
        size=len(df)
    )
)

df["simultaneous_pressure"] = rng.integers(
    0,
    8,
    size=len(df)
)


# ============================================================
# SCHEDULE ACTIVITY SCORE
# ============================================================

df["schedule_activity_score"] = (

    df["schedule_movements_5min"] * 0.40

    +

    df["schedule_movements_10min"] * 0.30

    +

    df["schedule_movements_15min"] * 0.20

    +

    df["schedule_movements_30min"] * 0.10
)


# ============================================================
# BASE CROWD GROWTH
# ============================================================

base_growth = (
    df["growth_rate_5s"]
    .clip(-2.0, 2.0)
)


# ============================================================
# SCHEDULE PRESSURE
# ============================================================

schedule_pressure = (
    df["schedule_activity_score"]
    * 0.15
)


simultaneous_effect = (
    df["simultaneous_pressure"]
    * 0.20
)


# ============================================================
# SYNTHETIC 5-MINUTE FUTURE CROWD
# ============================================================
#
# IMPORTANT:
#
# This is a prototype scenario target.
# It is NOT claimed to be observed real-world
# 5-minute ground truth.
# ============================================================

df["future_crowd_5min"] = (

    df["observed_crowd"]

    +

    (
        base_growth
        * 5
    )

    +

    schedule_pressure

    +

    simultaneous_effect

)


# ============================================================
# ADD SMALL CONTROLLED VARIATION
# ============================================================

noise = rng.normal(
    loc=0,
    scale=1.0,
    size=len(df)
)

df["future_crowd_5min"] += noise


# ============================================================
# CLIP FUTURE CROWD
# ============================================================

df["future_crowd_5min"] = (
    df["future_crowd_5min"]
    .clip(lower=0)
    .round(2)
)


# ============================================================
# SURGE CALCULATION
# ============================================================

df["crowd_increase"] = (
    df["future_crowd_5min"]
    -
    df["observed_crowd"]
)


# ============================================================
# SURGE LABEL
# ============================================================

df["surge"] = (
    df["crowd_increase"] >= 5
).astype(int)


# ============================================================
# FUTURE RISK
# ============================================================

def calculate_risk(row):

    future = row[
        "future_crowd_5min"
    ]

    increase = row[
        "crowd_increase"
    ]

    schedule = row[
        "schedule_activity_score"
    ]

    simultaneous = row[
        "simultaneous_pressure"
    ]

    score = 0

    # Future crowd pressure
    if future >= 15:
        score += 3
    elif future >= 10:
        score += 2
    elif future >= 5:
        score += 1

    # Crowd increase
    if increase >= 8:
        score += 3
    elif increase >= 5:
        score += 2
    elif increase >= 3:
        score += 1

    # Schedule pressure
    if schedule >= 10:
        score += 2
    elif schedule >= 6:
        score += 1

    # Simultaneous events
    if simultaneous >= 6:
        score += 2
    elif simultaneous >= 3:
        score += 1

    if score >= 7:
        return "CRITICAL"

    elif score >= 5:
        return "HIGH"

    elif score >= 3:
        return "MEDIUM"

    else:
        return "LOW"


df["future_risk"] = df.apply(
    calculate_risk,
    axis=1
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FORECAST DATASET COMPLETE")
print("=" * 70)

print(
    f"Rows: {len(df)}"
)

print(
    f"Videos: "
    f"{df['video_id'].nunique()}"
)

print(
    f"Average current crowd: "
    f"{df['observed_crowd'].mean():.2f}"
)

print(
    f"Average future crowd: "
    f"{df['future_crowd_5min'].mean():.2f}"
)

print(
    f"Surge cases: "
    f"{df['surge'].sum()}"
)

print(
    f"Surge percentage: "
    f"{df['surge'].mean() * 100:.2f}%"
)

print("\nFuture risk distribution:")

print(
    df[
        "future_risk"
    ].value_counts()
)

print("\nSaved to:")

print(
    OUTPUT_PATH
)


# ============================================================
# SAMPLE
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE FORECAST DATA")
print("=" * 70)

print(
    df[
        [
            "video_id",
            "time_sec",
            "observed_crowd",
            "growth_rate_5s",
            "schedule_activity_score",
            "simultaneous_pressure",
            "future_crowd_5min",
            "crowd_increase",
            "surge",
            "future_risk"
        ]
    ]
    .head(20)
    .to_string(index=False)
)
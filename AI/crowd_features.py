import pandas as pd
from pathlib import Path


# ============================================================
# RAILMIND AI - CROWD FEATURE ENGINE
# ============================================================

CROWD_DATA = Path(
    r"D:\RailMindAI\data\crowd_timeseries\combined_pune_crowd_dataset.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("RAILMIND AI - CROWD FEATURE ENGINE")
print("=" * 70)

df = pd.read_csv(CROWD_DATA)

print(f"\nRows loaded: {len(df)}")
print(
    f"Videos: "
    f"{df['video_id'].nunique()}"
)


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    ["video_id", "time_sec"]
).reset_index(drop=True)


# ============================================================
# NUMERIC CONVERSION
# ============================================================

df["observed_crowd"] = pd.to_numeric(
    df["observed_crowd"],
    errors="coerce"
)

df["crowd_change"] = pd.to_numeric(
    df["crowd_change"],
    errors="coerce"
)


# ============================================================
# FEATURE CALCULATION PER VIDEO
# ============================================================

feature_rows = []


for video_id, group in df.groupby(
    "video_id"
):

    group = group.copy()

    group = group.sort_values(
        "time_sec"
    )

    crowd = group[
        "observed_crowd"
    ]

    # --------------------------------------------------------
    # Rolling statistics
    # --------------------------------------------------------

    group[
        "crowd_mean_5s"
    ] = crowd.rolling(
        window=5,
        min_periods=1
    ).mean()

    group[
        "crowd_max_5s"
    ] = crowd.rolling(
        window=5,
        min_periods=1
    ).max()

    group[
        "crowd_min_5s"
    ] = crowd.rolling(
        window=5,
        min_periods=1
    ).min()


    # --------------------------------------------------------
    # Crowd change
    # --------------------------------------------------------

    group[
        "crowd_change_1s"
    ] = crowd.diff()


    group[
        "crowd_change_3s"
    ] = crowd.diff(
        periods=3
    )


    group[
        "crowd_change_5s"
    ] = crowd.diff(
        periods=5
    )


    # --------------------------------------------------------
    # Growth rate
    # --------------------------------------------------------

    group[
        "growth_rate_5s"
    ] = (
        group[
            "crowd_change_5s"
        ]
        /
        5
    )


    # --------------------------------------------------------
    # Acceleration
    # --------------------------------------------------------

    group[
        "acceleration"
    ] = group[
        "crowd_change_1s"
    ].diff()


    # --------------------------------------------------------
    # Recent trend
    # --------------------------------------------------------

    def trend(row):

        growth = row[
            "growth_rate_5s"
        ]

        if pd.isna(growth):

            return "UNKNOWN"

        if growth >= 1.0:

            return "RAPIDLY RISING"

        elif growth >= 0.3:

            return "RISING"

        elif growth <= -1.0:

            return "RAPIDLY FALLING"

        elif growth <= -0.3:

            return "FALLING"

        else:

            return "STABLE"


    group[
        "trend"
    ] = group.apply(
        trend,
        axis=1
    )


    # --------------------------------------------------------
    # Crowd level
    # --------------------------------------------------------

    def crowd_level(value):

        if pd.isna(value):

            return "UNKNOWN"

        if value >= 15:

            return "CRITICAL"

        elif value >= 10:

            return "HIGH"

        elif value >= 5:

            return "MEDIUM"

        else:

            return "LOW"


    group[
        "crowd_level"
    ] = group[
        "observed_crowd"
    ].apply(
        crowd_level
    )


    feature_rows.append(
        group
    )


# ============================================================
# COMBINE
# ============================================================

features = pd.concat(
    feature_rows,
    ignore_index=True
)


# ============================================================
# SAVE
# ============================================================

output_path = Path(
    r"D:\RailMindAI\data\crowd_timeseries\crowd_features.csv"
)

features.to_csv(
    output_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CROWD FEATURE ENGINE COMPLETE")
print("=" * 70)

print(
    f"Rows: {len(features)}"
)

print(
    f"Videos: "
    f"{features['video_id'].nunique()}"
)

print("\nNew features:")

new_features = [
    "crowd_mean_5s",
    "crowd_max_5s",
    "crowd_min_5s",
    "crowd_change_1s",
    "crowd_change_3s",
    "crowd_change_5s",
    "growth_rate_5s",
    "acceleration",
    "trend",
    "crowd_level"
]

for feature in new_features:

    print(
        f"  - {feature}"
    )


print("\nSaved to:")
print(output_path)


# ============================================================
# SAMPLE
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE CROWD FEATURES")
print("=" * 70)

print(
    features[
        [
            "video_id",
            "time_sec",
            "observed_crowd",
            "crowd_mean_5s",
            "crowd_change_5s",
            "growth_rate_5s",
            "acceleration",
            "trend",
            "crowd_level"
        ]
    ].head(20).to_string(
        index=False
    )
)
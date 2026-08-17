from pathlib import Path
import sys

# ============================================================
# RAILMIND AI - LIVE INTEGRATED ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

sys.path.append(str(BASE_DIR))

from schedule_features import calculate_features
from scenario_engine import (
    forecast_crowd,
    calculate_surge_score,
    classify_risk,
    recommend_action,
)


# ============================================================
# CONFIGURATION
# ============================================================

CROWD_DATA = Path(
    r"D:\RailMindAI\data\crowd_timeseries\crowd_features.csv"
)


# ============================================================
# FIND LATEST CROWD STATE
# ============================================================

def get_latest_crowd_state():

    import pandas as pd

    df = pd.read_csv(
        CROWD_DATA
    )

    df = df.dropna(
        subset=[
            "observed_crowd",
            "growth_rate_5s"
        ]
    )

    if df.empty:
        raise ValueError(
            "No usable crowd observations found."
        )

    latest = df.iloc[-1]

    return {
        "video_id":
            latest["video_id"],

        "time_sec":
            float(latest["time_sec"]),

        "current_crowd":
            float(latest["observed_crowd"]),

        "growth_rate":
            float(latest["growth_rate_5s"]),

        "acceleration":
            float(
                latest["acceleration"]
                if not pd.isna(
                    latest["acceleration"]
                )
                else 0
            ),

        "trend":
            latest["trend"],

        "crowd_level":
            latest["crowd_level"]
    }


# ============================================================
# ANALYZE LIVE STATE
# ============================================================

def analyze_live_state(
    current_time,
    current_crowd,
    growth_rate,
    acceleration
):

    # --------------------------------------------------------
    # REAL SCHEDULE DATA
    # --------------------------------------------------------

    schedule = calculate_features(
        current_time
    )


    # --------------------------------------------------------
    # FORECAST
    # --------------------------------------------------------

    future_crowd = forecast_crowd(
        current_crowd,
        growth_rate,
        acceleration,
        schedule
    )


    # --------------------------------------------------------
    # SURGE SCORE
    # --------------------------------------------------------

    surge_score = calculate_surge_score(
        current_crowd,
        future_crowd,
        growth_rate,
        schedule
    )


    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk = classify_risk(
        surge_score
    )


    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    action = recommend_action(
        risk,
        future_crowd,
        schedule
    )


    return {

        "current_time":
            current_time,

        "current_crowd":
            current_crowd,

        "growth_rate":
            growth_rate,

        "acceleration":
            acceleration,

        "future_crowd_5min":
            future_crowd,

        "crowd_increase":
            round(
                future_crowd
                -
                current_crowd,
                2
            ),

        "surge_score":
            surge_score,

        "risk":
            risk,

        "action":
            action,

        "schedule":
            schedule
    }


# ============================================================
# DISPLAY
# ============================================================

def display_result(result):

    schedule = result[
        "schedule"
    ]

    print("\n")
    print("=" * 75)
    print("RAILMIND AI - LIVE CONGESTION INTELLIGENCE")
    print("=" * 75)

    print(
        f"\nStation: PUNE JUNCTION"
    )

    print(
        f"Current time: "
        f"{result['current_time']}"
    )

    print("\n" + "-" * 75)
    print("CURRENT CROWD")
    print("-" * 75)

    print(
        f"Current crowd: "
        f"{result['current_crowd']:.0f}"
    )

    print(
        f"Growth rate: "
        f"{result['growth_rate']:+.2f}/sec"
    )

    print(
        f"Acceleration: "
        f"{result['acceleration']:+.2f}"
    )


    print("\n" + "-" * 75)
    print("TRAIN PRESSURE")
    print("-" * 75)

    print(
        f"5-min movements: "
        f"{schedule['total_movements_5min']}"
    )

    print(
        f"10-min movements: "
        f"{schedule['total_movements_10min']}"
    )

    print(
        f"15-min movements: "
        f"{schedule['total_movements_15min']}"
    )

    print(
        f"30-min movements: "
        f"{schedule['total_movements_30min']}"
    )

    print(
        f"Simultaneous pressure: "
        f"{schedule['simultaneous_pressure']}"
    )

    print(
        f"Activity level: "
        f"{schedule['activity_level']}"
    )

    print(
        f"Next train event: "
        f"{schedule['next_event_time']} | "
        f"{schedule['next_event_type']} | "
        f"{schedule['next_train_no']} | "
        f"{schedule['next_train_name']}"
    )


    print("\n" + "-" * 75)
    print("5-MINUTE FORECAST")
    print("-" * 75)

    print(
        f"Predicted crowd: "
        f"{result['future_crowd_5min']:.2f}"
    )

    print(
        f"Predicted increase: "
        f"{result['crowd_increase']:+.2f}"
    )

    print(
        f"Surge score: "
        f"{result['surge_score']}/100"
    )


    print("\n" + "-" * 75)
    print("RISK ASSESSMENT")
    print("-" * 75)

    print(
        f"RISK LEVEL: "
        f"{result['risk']}"
    )


    print("\n" + "-" * 75)
    print("RECOMMENDED ACTION")
    print("-" * 75)

    print(
        result["action"]
    )


    print("\n" + "=" * 75)
    print("RAILMIND ANALYSIS COMPLETE")
    print("=" * 75)


# ============================================================
# DEMO MODE
# ============================================================

if __name__ == "__main__":

    print("=" * 75)
    print("RAILMIND AI - LIVE ENGINE TEST")
    print("=" * 75)

    print(
        "\nThis test uses manually supplied "
        "crowd conditions with REAL Pune schedule data."
    )


    # --------------------------------------------------------
    # TEST CASE
    # --------------------------------------------------------

    current_time = "18:40"

    current_crowd = 12

    growth_rate = 1.0

    acceleration = 0.2


    result = analyze_live_state(

        current_time,

        current_crowd,

        growth_rate,

        acceleration
    )


    display_result(
        result
    )
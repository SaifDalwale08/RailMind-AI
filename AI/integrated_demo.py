import sys
from pathlib import Path
import pandas as pd

# ============================================================
# RAILMIND AI - COMPLETE INTEGRATED DEMO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

sys.path.append(str(BASE_DIR))

from announcement_engine import generate_alert


# ============================================================
# CONFIGURATION
# ============================================================

LIVE_SIGNAL = (
    PROJECT_DIR
    / "data"
    / "live"
    / "live_crowd_signal.csv"
)


# ============================================================
# LOAD LIVE CROWD SIGNAL
# ============================================================

def load_latest_valid_state():

    if not LIVE_SIGNAL.exists():

        raise FileNotFoundError(
            f"Live crowd signal not found:\n"
            f"{LIVE_SIGNAL}\n\n"
            f"Run live_video_engine.py first."
        )


    df = pd.read_csv(
        LIVE_SIGNAL
    )


    if df.empty:

        raise ValueError(
            "Live crowd signal is empty."
        )


    # --------------------------------------------------------
    # We need forecasting-ready observations.
    # --------------------------------------------------------

    valid = df[
        df["growth_rate_5s"].notna()
    ].copy()


    if valid.empty:

        raise ValueError(
            "No forecasting-ready crowd observations."
        )


    # --------------------------------------------------------
    # Prefer observations with valid acceleration.
    # If unavailable, use growth-only observation.
    # --------------------------------------------------------

    valid_acceleration = valid[
        valid["acceleration"].notna()
    ]


    if not valid_acceleration.empty:

        latest = valid_acceleration.iloc[-1]

    else:

        latest = valid.iloc[-1]


    current_crowd = float(
        latest["crowd"]
    )

    growth_rate = float(
        latest["growth_rate_5s"]
    )


    if pd.isna(
        latest["acceleration"]
    ):

        acceleration = 0.0

    else:

        acceleration = float(
            latest["acceleration"]
        )


    return {

        "time_sec":
            int(
                latest["time_sec"]
            ),

        "current_crowd":
            current_crowd,

        "growth_rate":
            growth_rate,

        "acceleration":
            acceleration,

        "trend":
            latest["trend"],

        "crowd_level":
            latest["crowd_level"]
    }


# ============================================================
# CONVERT VIDEO TIME TO DEMO STATION TIME
# ============================================================

def get_demo_station_time():

    # --------------------------------------------------------
    # For this first integrated demo we use the same
    # high-pressure Pune scenario time.
    #
    # Later this will come from the real station clock.
    # --------------------------------------------------------

    return "18:40"


# ============================================================
# DISPLAY VIDEO STATE
# ============================================================

def display_video_state(
    state
):

    print("\n")
    print("=" * 80)
    print(
        "RAILMIND AI - REAL VIDEO CROWD STATE"
    )
    print("=" * 80)

    print(
        f"Video timestamp: "
        f"{state['time_sec']} sec"
    )

    print(
        f"Current crowd: "
        f"{state['current_crowd']:.0f}"
    )

    print(
        f"Growth rate: "
        f"{state['growth_rate']:+.2f}/sec"
    )

    print(
        f"Acceleration: "
        f"{state['acceleration']:+.2f}"
    )

    print(
        f"Trend: "
        f"{state['trend']}"
    )

    print(
        f"Crowd level: "
        f"{state['crowd_level']}"
    )


# ============================================================
# DISPLAY FINAL INTEGRATED RESULT
# ============================================================

def display_integrated_summary(
    state,
    result
):

    baseline = result[
        "baseline"
    ]

    best = result[
        "best_intervention"
    ]

    alert = result[
        "operator_alert"
    ]


    print("\n")
    print("=" * 80)
    print(
        "RAILMIND AI - COMPLETE DECISION"
    )
    print("=" * 80)


    print(
        f"\nStation: "
        f"PUNE JUNCTION"
    )

    print(
        f"Station time: "
        f"{baseline['current_time']}"
    )


    print("\n" + "-" * 80)
    print("REAL VIDEO INPUT")
    print("-" * 80)

    print(
        f"Crowd: "
        f"{state['current_crowd']:.0f}"
    )

    print(
        f"Trend: "
        f"{state['trend']}"
    )

    print(
        f"Growth: "
        f"{state['growth_rate']:+.2f}/sec"
    )


    print("\n" + "-" * 80)
    print("SCHEDULE INTELLIGENCE")
    print("-" * 80)

    schedule = baseline[
        "schedule"
    ]

    print(
        f"5-min movements: "
        f"{schedule['total_movements_5min']}"
    )

    print(
        f"10-min movements: "
        f"{schedule['total_movements_10min']}"
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
        f"Activity: "
        f"{schedule['activity_level']}"
    )


    print("\n" + "-" * 80)
    print("AI FORECAST")
    print("-" * 80)

    print(
        f"5-min predicted crowd: "
        f"{baseline['future_crowd_5min']:.2f}"
    )

    print(
        f"Predicted increase: "
        f"{baseline['future_crowd_5min'] - baseline['current_crowd']:+.2f}"
    )

    print(
        f"Surge score: "
        f"{baseline['surge_score']}/100"
    )

    print(
        f"Risk: "
        f"{baseline['risk']}"
    )


    print("\n" + "-" * 80)
    print("INTERVENTION DECISION")
    print("-" * 80)

    print(
        f"Recommended: "
        f"{best['intervention']}"
    )

    print(
        f"Projected crowd: "
        f"{best['predicted_crowd']:.2f}"
    )

    print(
        f"Projected reduction: "
        f"{best['crowd_reduction']:.2f}"
    )

    print(
        f"Projected risk: "
        f"{best['risk']}"
    )


    print("\n" + "-" * 80)
    print("FINAL OPERATOR ALERT")
    print("-" * 80)

    print(
        f"Risk: "
        f"{alert['risk']}"
    )

    print(
        f"Action: "
        f"{alert['recommended_intervention']}"
    )


    print("\n" + "-" * 80)
    print("ANNOUNCEMENT PREVIEW")
    print("-" * 80)

    print(
        "\nENGLISH:"
    )

    print(
        result["english"]
    )

    print(
        "\nHINDI:"
    )

    print(
        result["hindi"]
    )

    print(
        "\nMARATHI:"
    )

    print(
        result["marathi"]
    )


    print("\n" + "=" * 80)
    print(
        "RAILMIND END-TO-END DEMO COMPLETE"
    )
    print("=" * 80)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print(
        "RAILMIND AI - END-TO-END INTEGRATION"
    )
    print("=" * 80)


    # --------------------------------------------------------
    # 1. Get real video-derived crowd state
    # --------------------------------------------------------

    state = load_latest_valid_state()


    display_video_state(
        state
    )


    # --------------------------------------------------------
    # 2. Station time
    # --------------------------------------------------------

    station_time = (
        get_demo_station_time()
    )


    # --------------------------------------------------------
    # 3. Feed REAL crowd state into complete
    #    RailMind intelligence pipeline
    # --------------------------------------------------------

    result = generate_alert(

        station_time,

        state["current_crowd"],

        state["growth_rate"],

        state["acceleration"]
    )


    # --------------------------------------------------------
    # 4. Display complete decision
    # --------------------------------------------------------

    display_integrated_summary(

        state,

        result
    )
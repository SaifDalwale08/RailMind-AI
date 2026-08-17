import sys
from pathlib import Path

# ============================================================
# RAILMIND AI - 5 MINUTE CONGESTION SCENARIO ENGINE
# ============================================================

# Allow importing our existing schedule engine
sys.path.append(
    str(Path(__file__).resolve().parent)
)

from schedule_features import calculate_features


# ============================================================
# CONFIGURATION
# ============================================================

FORECAST_MINUTES = 5


# ============================================================
# FORECAST FUNCTION
# ============================================================

def forecast_crowd(
    current_crowd,
    growth_rate,
    acceleration,
    schedule
):
    """
    Estimate short-term future crowd using:

    1. Current observed crowd
    2. Recent crowd growth
    3. Crowd acceleration
    4. Real train schedule pressure
    5. Simultaneous train-event pressure

    IMPORTANT:
    This is a prototype scenario model.
    It is NOT trained ML ground truth.
    """

    # --------------------------------------------------------
    # 1. Base trend projection
    # --------------------------------------------------------

    # Limit extreme vision-derived growth values
    # so a single noisy detection cannot explode
    # the forecast.

    safe_growth = max(
        -1.5,
        min(
            float(growth_rate),
            1.5
        )
    )

    trend_component = (
        safe_growth
        * FORECAST_MINUTES
    )


    # --------------------------------------------------------
    # 2. Acceleration component
    # --------------------------------------------------------

    safe_acceleration = max(
        -0.5,
        min(
            float(acceleration),
            0.5
        )
    )

    acceleration_component = (
        safe_acceleration
        * 0.8
    )


    # --------------------------------------------------------
    # 3. Schedule pressure
    # --------------------------------------------------------

    activity_score = float(
        schedule[
            "activity_score"
        ]
    )

    simultaneous_pressure = int(
        schedule[
            "simultaneous_pressure"
        ]
    )

    # Train activity contributes to future
    # passenger pressure.

    schedule_component = (
        activity_score
        * 0.35
    )

    simultaneous_component = (
        simultaneous_pressure
        * 0.45
    )


    # --------------------------------------------------------
    # 4. Calculate forecast
    # --------------------------------------------------------

    future_crowd = (

        current_crowd

        +

        trend_component

        +

        acceleration_component

        +

        schedule_component

        +

        simultaneous_component
    )


    # Never predict negative people
    future_crowd = max(
        0,
        future_crowd
    )


    return round(
        future_crowd,
        2
    )


# ============================================================
# SURGE SCORE
# ============================================================

def calculate_surge_score(
    current_crowd,
    future_crowd,
    growth_rate,
    schedule
):

    increase = (
        future_crowd
        -
        current_crowd
    )

    activity_score = float(
        schedule[
            "activity_score"
        ]
    )

    simultaneous = int(
        schedule[
            "simultaneous_pressure"
        ]
    )


    score = 0


    # --------------------------------------------------------
    # Future crowd
    # --------------------------------------------------------

    if future_crowd >= 20:

        score += 35

    elif future_crowd >= 15:

        score += 25

    elif future_crowd >= 10:

        score += 15

    elif future_crowd >= 5:

        score += 7


    # --------------------------------------------------------
    # Crowd increase
    # --------------------------------------------------------

    if increase >= 10:

        score += 30

    elif increase >= 7:

        score += 25

    elif increase >= 5:

        score += 18

    elif increase >= 3:

        score += 10


    # --------------------------------------------------------
    # Growth
    # --------------------------------------------------------

    if growth_rate >= 1.0:

        score += 20

    elif growth_rate >= 0.5:

        score += 12

    elif growth_rate > 0:

        score += 5


    # --------------------------------------------------------
    # Train pressure
    # --------------------------------------------------------

    if activity_score >= 15:

        score += 15

    elif activity_score >= 10:

        score += 12

    elif activity_score >= 6:

        score += 7

    elif activity_score >= 3:

        score += 3


    # --------------------------------------------------------
    # Simultaneous pressure
    # --------------------------------------------------------

    if simultaneous >= 7:

        score += 10

    elif simultaneous >= 5:

        score += 7

    elif simultaneous >= 3:

        score += 4


    return min(
        100,
        int(score)
    )


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_risk(score):

    if score >= 75:

        return "CRITICAL"

    elif score >= 55:

        return "HIGH"

    elif score >= 30:

        return "MEDIUM"

    else:

        return "LOW"


# ============================================================
# ACTION RECOMMENDATION
# ============================================================

def recommend_action(
    risk,
    future_crowd,
    schedule
):

    activity = schedule[
        "activity_level"
    ]

    simultaneous = schedule[
        "simultaneous_pressure"
    ]

    if risk == "CRITICAL":

        return (
            "ACTIVATE CROWD CONTROL: "
            "restrict incoming passenger flow, "
            "deploy staff at platform access points, "
            "protect emergency corridor, "
            "and issue passenger guidance announcement."
        )


    elif risk == "HIGH":

        return (
            "PREPARE CROWD CONTROL: "
            "deploy staff near platform/gate bottlenecks, "
            "guide passengers toward alternate routes, "
            "and prepare announcement."
        )


    elif risk == "MEDIUM":

        return (
            "MONITOR CLOSELY: "
            "increase operator observation, "
            "prepare passenger guidance, "
            "and monitor upcoming train movements."
        )


    else:

        return (
            "NORMAL MONITORING: "
            "continue live crowd observation "
            "and schedule monitoring."
        )


# ============================================================
# FULL ANALYSIS
# ============================================================

def analyze(
    current_time,
    current_crowd,
    growth_rate,
    acceleration
):

    # Get REAL schedule features
    schedule = calculate_features(
        current_time
    )


    # Forecast
    future_crowd = forecast_crowd(
        current_crowd,
        growth_rate,
        acceleration,
        schedule
    )


    # Surge
    surge_score = calculate_surge_score(
        current_crowd,
        future_crowd,
        growth_rate,
        schedule
    )


    # Risk
    risk = classify_risk(
        surge_score
    )


    # Action
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
# DEMO
# ============================================================

if __name__ == "__main__":

    print("=" * 75)
    print(
        "RAILMIND AI - 5 MINUTE "
        "CONGESTION SCENARIO ENGINE"
    )
    print("=" * 75)


    # --------------------------------------------------------
    # Scenario 1
    # --------------------------------------------------------

    scenarios = [

        {
            "name":
                "NORMAL",

            "time":
                "06:00",

            "crowd":
                4,

            "growth":
                0.1,

            "acceleration":
                0.0
        },


        {
            "name":
                "RISING CROWD",

            "time":
                "10:30",

            "crowd":
                8,

            "growth":
                0.8,

            "acceleration":
                0.1
        },


        {
            "name":
                "HIGH PRESSURE",

            "time":
                "18:40",

            "crowd":
                12,

            "growth":
                1.0,

            "acceleration":
                0.2
        }
    ]


    for scenario in scenarios:

        result = analyze(

            scenario["time"],

            scenario["crowd"],

            scenario["growth"],

            scenario["acceleration"]
        )


        schedule = result[
            "schedule"
        ]


        print("\n")
        print("-" * 75)

        print(
            f"SCENARIO: "
            f"{scenario['name']}"
        )

        print(
            f"Current time: "
            f"{result['current_time']}"
        )

        print(
            f"Current crowd: "
            f"{result['current_crowd']}"
        )

        print(
            f"Crowd growth: "
            f"{result['growth_rate']}"
        )

        print(
            f"5-min predicted crowd: "
            f"{result['future_crowd_5min']}"
        )

        print(
            f"Predicted increase: "
            f"{result['crowd_increase']}"
        )

        print(
            f"Schedule activity: "
            f"{schedule['activity_level']}"
        )

        print(
            f"5-min train movements: "
            f"{schedule['total_movements_5min']}"
        )

        print(
            f"10-min train movements: "
            f"{schedule['total_movements_10min']}"
        )

        print(
            f"30-min train movements: "
            f"{schedule['total_movements_30min']}"
        )

        print(
            f"Simultaneous pressure: "
            f"{schedule['simultaneous_pressure']}"
        )

        print(
            f"Surge score: "
            f"{result['surge_score']}/100"
        )

        print(
            f"RISK: "
            f"{result['risk']}"
        )

        print(
            f"ACTION: "
            f"{result['action']}"
        )


    print("\n")
    print("=" * 75)
    print(
        "SCENARIO ENGINE COMPLETE"
    )
    print("=" * 75)
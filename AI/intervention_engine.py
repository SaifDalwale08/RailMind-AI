import sys
from pathlib import Path

# ============================================================
# RAILMIND AI - INTERVENTION SIMULATION ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from live_engine import analyze_live_state


# ============================================================
# INTERVENTIONS
# ============================================================

INTERVENTIONS = {

    "NO ACTION": {
        "inflow_reduction": 0.00,
        "description":
            "Continue normal passenger movement."
    },

    "GATE CONTROL": {
        "inflow_reduction": 0.20,
        "description":
            "Temporarily regulate incoming passenger flow."
    },

    "PLATFORM GUIDANCE": {
        "inflow_reduction": 0.15,
        "description":
            "Redirect passengers toward less-loaded platform areas."
    },

    "GATE CONTROL + PLATFORM GUIDANCE": {
        "inflow_reduction": 0.35,
        "description":
            "Regulate entry and redirect passenger movement."
    }
}


# ============================================================
# RISK SCORE
# ============================================================

def calculate_intervention_risk(
    current_crowd,
    future_crowd,
    baseline_growth,
    schedule
):

    score = 0

    increase = (
        future_crowd
        - current_crowd
    )

    activity = float(
        schedule["activity_score"]
    )

    simultaneous = int(
        schedule["simultaneous_pressure"]
    )


    # --------------------------------------------------------
    # FUTURE CROWD PRESSURE
    # --------------------------------------------------------

    if future_crowd >= 25:
        score += 40

    elif future_crowd >= 20:
        score += 32

    elif future_crowd >= 15:
        score += 24

    elif future_crowd >= 10:
        score += 15

    elif future_crowd >= 5:
        score += 7


    # --------------------------------------------------------
    # FUTURE CROWD INCREASE
    # --------------------------------------------------------

    if increase >= 10:
        score += 30

    elif increase >= 7:
        score += 24

    elif increase >= 5:
        score += 17

    elif increase >= 3:
        score += 10

    elif increase > 0:
        score += 5


    # --------------------------------------------------------
    # EFFECTIVE GROWTH
    #
    # Intervention reduces the effective passenger influx.
    # --------------------------------------------------------

    if baseline_growth >= 1.0:
        score += 15

    elif baseline_growth >= 0.5:
        score += 10

    elif baseline_growth > 0:
        score += 5


    # --------------------------------------------------------
    # TRAIN PRESSURE
    #
    # This remains because trains are still arriving.
    # --------------------------------------------------------

    if activity >= 15:
        score += 10

    elif activity >= 10:
        score += 8

    elif activity >= 6:
        score += 5

    elif activity >= 3:
        score += 2


    # --------------------------------------------------------
    # SIMULTANEOUS EVENTS
    # --------------------------------------------------------

    if simultaneous >= 7:
        score += 5

    elif simultaneous >= 5:
        score += 4

    elif simultaneous >= 3:
        score += 2


    return min(
        100,
        int(score)
    )


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_risk(score):

    if score >= 70:
        return "CRITICAL"

    elif score >= 50:
        return "HIGH"

    elif score >= 30:
        return "MEDIUM"

    else:
        return "LOW"


# ============================================================
# SIMULATE INTERVENTION
# ============================================================

def simulate_intervention(
    baseline,
    intervention_name
):

    config = INTERVENTIONS[
        intervention_name
    ]

    reduction = config[
        "inflow_reduction"
    ]

    current_crowd = baseline[
        "current_crowd"
    ]

    baseline_forecast = baseline[
        "future_crowd_5min"
    ]

    baseline_increase = (
        baseline_forecast
        - current_crowd
    )


    # --------------------------------------------------------
    # Apply intervention only to future influx.
    #
    # Existing passengers are NOT removed.
    # --------------------------------------------------------

    adjusted_increase = (
        baseline_increase
        *
        (1 - reduction)
    )

    adjusted_forecast = (
        current_crowd
        +
        adjusted_increase
    )


    # --------------------------------------------------------
    # Effective growth after intervention
    # --------------------------------------------------------

    effective_growth = (
        baseline["growth_rate"]
        *
        (1 - reduction)
    )


    # --------------------------------------------------------
    # Recalculate risk
    # --------------------------------------------------------

    risk_score = calculate_intervention_risk(

        current_crowd,

        adjusted_forecast,

        effective_growth,

        baseline["schedule"]
    )


    risk = classify_risk(
        risk_score
    )


    return {

        "intervention":
            intervention_name,

        "reduction":
            reduction,

        "predicted_crowd":
            round(
                adjusted_forecast,
                2
            ),

        "crowd_reduction":
            round(
                baseline_forecast
                -
                adjusted_forecast,
                2
            ),

        "effective_growth":
            round(
                effective_growth,
                2
            ),

        "risk_score":
            risk_score,

        "risk":
            risk,

        "description":
            config[
                "description"
            ]
    }


# ============================================================
# RUN SIMULATION
# ============================================================

def run_simulation(
    current_time,
    current_crowd,
    growth_rate,
    acceleration
):

    baseline = analyze_live_state(

        current_time,

        current_crowd,

        growth_rate,

        acceleration
    )


    results = []

    for intervention in INTERVENTIONS:

        results.append(
            simulate_intervention(
                baseline,
                intervention
            )
        )


    return baseline, results


# ============================================================
# SELECT BEST ACTION
# ============================================================

def select_best_intervention(
    results
):

    risk_priority = {

        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
        "CRITICAL": 3
    }


    return sorted(

        results,

        key=lambda result: (

            risk_priority[
                result["risk"]
            ],

            result["predicted_crowd"],

            result["risk_score"]
        )

    )[0]


# ============================================================
# DISPLAY
# ============================================================

def display_results(
    baseline,
    results,
    best
):

    schedule = baseline[
        "schedule"
    ]


    print("\n")
    print("=" * 80)
    print(
        "RAILMIND AI - INTERVENTION SIMULATION"
    )
    print("=" * 80)


    print(
        "\nStation: PUNE JUNCTION"
    )

    print(
        f"Current time: "
        f"{baseline['current_time']}"
    )

    print(
        f"Current crowd: "
        f"{baseline['current_crowd']:.0f}"
    )

    print(
        f"Baseline 5-min forecast: "
        f"{baseline['future_crowd_5min']:.2f}"
    )

    print(
        f"Baseline risk: "
        f"{baseline['risk']}"
    )


    print("\n" + "-" * 80)
    print("TRAIN PRESSURE")
    print("-" * 80)

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
        f"Activity: "
        f"{schedule['activity_level']}"
    )


    print("\n" + "-" * 80)
    print("INTERVENTION COMPARISON")
    print("-" * 80)

    print(
        f"{'INTERVENTION':<32}"
        f"{'FORECAST':>12}"
        f"{'REDUCTION':>12}"
        f"{'SCORE':>10}"
        f"{'RISK':>12}"
    )

    print("-" * 80)


    for result in results:

        print(
            f"{result['intervention']:<32}"
            f"{result['predicted_crowd']:>12.2f}"
            f"{result['crowd_reduction']:>12.2f}"
            f"{result['risk_score']:>10}"
            f"{result['risk']:>12}"
        )


    print("\n" + "-" * 80)
    print("RECOMMENDED INTERVENTION")
    print("-" * 80)

    print(
        f"Action: "
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

    print(
        f"Effective growth: "
        f"{best['effective_growth']:+.2f}/sec"
    )

    print(
        f"Simulation assumption: "
        f"{best['reduction'] * 100:.0f}% reduction "
        f"in projected incoming pressure"
    )

    print(
        f"\nOperational recommendation:\n"
        f"{best['description']}"
    )


    print("\n" + "=" * 80)
    print(
        "INTERVENTION SIMULATION COMPLETE"
    )
    print("=" * 80)


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    current_time = "18:40"

    current_crowd = 12

    growth_rate = 1.0

    acceleration = 0.2


    baseline, results = run_simulation(

        current_time,

        current_crowd,

        growth_rate,

        acceleration
    )


    best = select_best_intervention(
        results
    )


    display_results(
        baseline,
        results,
        best
    )
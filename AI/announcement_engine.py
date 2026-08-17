import sys
from pathlib import Path

# ============================================================
# RAILMIND AI - ANNOUNCEMENT & OPERATOR ALERT ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from intervention_engine import (
    run_simulation,
    select_best_intervention
)


# ============================================================
# RISK EMOJI / LABEL
# ============================================================

RISK_LABELS = {
    "LOW": "LOW",
    "MEDIUM": "MEDIUM",
    "HIGH": "HIGH",
    "CRITICAL": "CRITICAL"
}


# ============================================================
# BUILD REASONS
# ============================================================

def build_reasons(baseline):

    schedule = baseline["schedule"]

    reasons = []

    current_crowd = baseline[
        "current_crowd"
    ]

    growth = baseline[
        "growth_rate"
    ]

    movements_5 = schedule[
        "total_movements_5min"
    ]

    simultaneous = schedule[
        "simultaneous_pressure"
    ]

    activity = schedule[
        "activity_level"
    ]


    # Crowd condition

    if current_crowd >= 15:

        reasons.append(
            "Current passenger density is elevated."
        )

    elif current_crowd >= 10:

        reasons.append(
            "Passenger density is increasing."
        )


    # Crowd trend

    if growth >= 1.0:

        reasons.append(
            "Crowd growth is rapid."
        )

    elif growth >= 0.5:

        reasons.append(
            "Crowd trend is rising."
        )


    # Schedule pressure

    if movements_5 >= 10:

        reasons.append(
            f"{movements_5} train movements "
            "are expected within the next 5 minutes."
        )

    elif movements_5 >= 5:

        reasons.append(
            f"{movements_5} train movements "
            "are expected within the next 5 minutes."
        )


    # Simultaneous pressure

    if simultaneous >= 7:

        reasons.append(
            f"{simultaneous} simultaneous train events "
            "are contributing to passenger pressure."
        )

    elif simultaneous >= 3:

        reasons.append(
            f"{simultaneous} simultaneous train events "
            "are contributing to passenger pressure."
        )


    # Activity

    if activity == "VERY HIGH":

        reasons.append(
            "Overall railway activity is VERY HIGH."
        )

    elif activity == "HIGH":

        reasons.append(
            "Overall railway activity is HIGH."
        )


    if not reasons:

        reasons.append(
            "No significant congestion trigger detected."
        )


    return reasons


# ============================================================
# ACTION TEXT
# ============================================================

def action_text(intervention):

    if intervention == "GATE CONTROL":

        return (
            "Temporarily regulate incoming passenger "
            "flow at station access points."
        )

    elif intervention == "PLATFORM GUIDANCE":

        return (
            "Redirect passengers toward less-loaded "
            "platform areas and available routes."
        )

    elif intervention == "GATE CONTROL + PLATFORM GUIDANCE":

        return (
            "Regulate incoming passenger flow and "
            "redirect passengers toward less-loaded "
            "platform areas."
        )

    else:

        return (
            "Continue normal monitoring and maintain "
            "operator awareness."
        )


# ============================================================
# ENGLISH ANNOUNCEMENT
# ============================================================

def english_announcement(
    risk,
    current_crowd,
    future_crowd,
    reasons,
    intervention
):

    if risk == "CRITICAL":

        opening = (
            "Attention passengers. "
            "Crowd management measures are currently "
            "being activated at Pune Junction."
        )

    elif risk == "HIGH":

        opening = (
            "Attention passengers. "
            "Please follow railway staff instructions "
            "and use designated passenger routes."
        )

    elif risk == "MEDIUM":

        opening = (
            "Attention passengers. "
            "Please follow railway staff instructions "
            "and avoid unnecessary crowding."
        )

    else:

        opening = (
            "Attention passengers. "
            "Please follow railway staff instructions."
        )


    action = action_text(
        intervention
    )


    return (
        opening
        + " "
        + action
        + " Please remain calm and keep "
          "emergency access routes clear."
    )


# ============================================================
# HINDI ANNOUNCEMENT
# ============================================================

def hindi_announcement(
    risk,
    intervention
):

    if risk == "CRITICAL":

        opening = (
            "यात्रियों का ध्यान आकर्षित किया जाता है। "
            "पुणे जंक्शन पर भीड़ प्रबंधन के उपाय "
            "सक्रिय किए जा रहे हैं।"
        )

    elif risk == "HIGH":

        opening = (
            "यात्रियों से अनुरोध है कि रेलवे कर्मचारियों "
            "के निर्देशों का पालन करें और निर्धारित "
            "मार्गों का उपयोग करें।"
        )

    elif risk == "MEDIUM":

        opening = (
            "यात्रियों से अनुरोध है कि रेलवे कर्मचारियों "
            "के निर्देशों का पालन करें और अनावश्यक "
            "भीड़ से बचें।"
        )

    else:

        opening = (
            "यात्रियों से अनुरोध है कि रेलवे कर्मचारियों "
            "के निर्देशों का पालन करें।"
        )


    if intervention == "GATE CONTROL":

        action = (
            "प्रवेश द्वारों पर यात्रियों के प्रवेश को "
            "अस्थायी रूप से नियंत्रित किया जा सकता है।"
        )

    elif intervention == "PLATFORM GUIDANCE":

        action = (
            "कृपया कम भीड़ वाले प्लेटफॉर्म क्षेत्रों "
            "और निर्धारित मार्गों का उपयोग करें।"
        )

    elif intervention == "GATE CONTROL + PLATFORM GUIDANCE":

        action = (
            "प्रवेश को नियंत्रित किया जा सकता है और "
            "यात्रियों को कम भीड़ वाले क्षेत्रों की ओर "
            "निर्देशित किया जा सकता है।"
        )

    else:

        action = (
            "कृपया सामान्य यात्री मार्गों का उपयोग करें।"
        )


    return (
        opening
        + " "
        + action
        + " कृपया शांत रहें और आपातकालीन "
          "मार्गों को खाली रखें।"
    )


# ============================================================
# MARATHI ANNOUNCEMENT
# ============================================================

def marathi_announcement(
    risk,
    intervention
):

    if risk == "CRITICAL":

        opening = (
            "प्रवाशांचे लक्ष वेधण्यात येत आहे. "
            "पुणे जंक्शनवर गर्दी नियंत्रणाच्या "
            "उपाययोजना सक्रिय करण्यात येत आहेत."
        )

    elif risk == "HIGH":

        opening = (
            "प्रवाशांनी रेल्वे कर्मचाऱ्यांच्या सूचनांचे "
            "पालन करावे आणि निर्धारित मार्गांचा "
            "वापर करावा."
        )

    elif risk == "MEDIUM":

        opening = (
            "प्रवाशांनी रेल्वे कर्मचाऱ्यांच्या सूचनांचे "
            "पालन करावे आणि अनावश्यक गर्दी टाळावी."
        )

    else:

        opening = (
            "प्रवाशांनी रेल्वे कर्मचाऱ्यांच्या "
            "सूचनांचे पालन करावे."
        )


    if intervention == "GATE CONTROL":

        action = (
            "प्रवेशद्वारांवर प्रवाशांच्या प्रवेशाचे "
            "तात्पुरते नियमन करण्यात येईल."
        )

    elif intervention == "PLATFORM GUIDANCE":

        action = (
            "कमी गर्दी असलेल्या प्लॅटफॉर्मच्या "
            "भागांचा आणि निर्धारित मार्गांचा वापर करावा."
        )

    elif intervention == "GATE CONTROL + PLATFORM GUIDANCE":

        action = (
            "प्रवेश नियंत्रित करण्यात येईल आणि "
            "प्रवाशांना कमी गर्दी असलेल्या भागांकडे "
            "मार्गदर्शन केले जाईल."
        )

    else:

        action = (
            "कृपया सामान्य प्रवासी मार्गांचा वापर करावा."
        )


    return (
        opening
        + " "
        + action
        + " कृपया शांत राहावे आणि आपत्कालीन "
          "मार्ग मोकळे ठेवावेत."
    )


# ============================================================
# OPERATOR ALERT
# ============================================================

def build_operator_alert(
    baseline,
    best_intervention,
    reasons
):

    schedule = baseline[
        "schedule"
    ]

    return {

        "station":
            "PUNE JUNCTION",

        "time":
            baseline[
                "current_time"
            ],

        "risk":
            baseline[
                "risk"
            ],

        "current_crowd":
            baseline[
                "current_crowd"
            ],

        "forecast_5min":
            baseline[
                "future_crowd_5min"
            ],

        "surge_score":
            baseline[
                "surge_score"
            ],

        "train_movements_5min":
            schedule[
                "total_movements_5min"
            ],

        "simultaneous_pressure":
            schedule[
                "simultaneous_pressure"
            ],

        "activity":
            schedule[
                "activity_level"
            ],

        "reasons":
            reasons,

        "recommended_intervention":
            best_intervention[
                "intervention"
            ],

        "simulated_forecast_after_action":
            best_intervention[
                "predicted_crowd"
            ],

        "simulated_risk_after_action":
            best_intervention[
                "risk"
            ]
    }


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def generate_alert(
    current_time,
    current_crowd,
    growth_rate,
    acceleration
):

    baseline, results = run_simulation(

        current_time,

        current_crowd,

        growth_rate,

        acceleration
    )


    best = select_best_intervention(
        results
    )


    reasons = build_reasons(
        baseline
    )


    alert = build_operator_alert(

        baseline,

        best,

        reasons
    )


    english = english_announcement(

        baseline["risk"],

        current_crowd,

        baseline["future_crowd_5min"],

        reasons,

        best["intervention"]
    )


    hindi = hindi_announcement(

        baseline["risk"],

        best["intervention"]
    )


    marathi = marathi_announcement(

        baseline["risk"],

        best["intervention"]
    )


    return {

        "baseline":
            baseline,

        "intervention_results":
            results,

        "best_intervention":
            best,

        "operator_alert":
            alert,

        "english":
            english,

        "hindi":
            hindi,

        "marathi":
            marathi
    }


# ============================================================
# DISPLAY
# ============================================================

def display_alert(result):

    baseline = result[
        "baseline"
    ]

    alert = result[
        "operator_alert"
    ]

    best = result[
        "best_intervention"
    ]


    print("\n")
    print("=" * 80)
    print(
        "RAILMIND AI - OPERATOR ALERT & ANNOUNCEMENT ENGINE"
    )
    print("=" * 80)


    # --------------------------------------------------------
    # ALERT
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("OPERATOR ALERT")
    print("-" * 80)

    print(
        f"Station: {alert['station']}"
    )

    print(
        f"Time: {alert['time']}"
    )

    print(
        f"Risk: {alert['risk']}"
    )

    print(
        f"Current crowd: "
        f"{alert['current_crowd']:.0f}"
    )

    print(
        f"5-min forecast: "
        f"{alert['forecast_5min']:.2f}"
    )

    print(
        f"Surge score: "
        f"{alert['surge_score']}/100"
    )

    print(
        f"Train movements in 5 min: "
        f"{alert['train_movements_5min']}"
    )

    print(
        f"Simultaneous pressure: "
        f"{alert['simultaneous_pressure']}"
    )

    print(
        f"Activity: "
        f"{alert['activity']}"
    )


    # --------------------------------------------------------
    # WHY?
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("WHY IS THE SYSTEM ALERTING?")
    print("-" * 80)

    for number, reason in enumerate(
        alert["reasons"],
        start=1
    ):

        print(
            f"{number}. {reason}"
        )


    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("RECOMMENDED ACTION")
    print("-" * 80)

    print(
        best["intervention"]
    )

    print(
        best["description"]
    )

    print(
        f"\nSimulated crowd after intervention: "
        f"{best['predicted_crowd']:.2f}"
    )

    print(
        f"Simulated risk after intervention: "
        f"{best['risk']}"
    )


    # --------------------------------------------------------
    # ENGLISH
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("ENGLISH ANNOUNCEMENT")
    print("-" * 80)

    print(
        result["english"]
    )


    # --------------------------------------------------------
    # HINDI
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("HINDI ANNOUNCEMENT")
    print("-" * 80)

    print(
        result["hindi"]
    )


    # --------------------------------------------------------
    # MARATHI
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("MARATHI ANNOUNCEMENT")
    print("-" * 80)

    print(
        result["marathi"]
    )


    print("\n" + "=" * 80)
    print(
        "ANNOUNCEMENT ENGINE COMPLETE"
    )
    print("=" * 80)


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # Same scenario used throughout our testing

    current_time = "18:40"

    current_crowd = 12

    growth_rate = 1.0

    acceleration = 0.2


    result = generate_alert(

        current_time,

        current_crowd,

        growth_rate,

        acceleration
    )


    display_alert(
        result
    )
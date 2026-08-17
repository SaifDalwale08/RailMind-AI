from fastapi import UploadFile, File
from pathlib import Path
import uuid

from AI.intervention_engine import (
    run_simulation,
    select_best_intervention
)
from pathlib import Path
import sys
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# RAILMIND AI - BACKEND API
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

AI_DIR = PROJECT_DIR / "AI"

sys.path.append(str(AI_DIR))


# ============================================================
# IMPORT RAILMIND INTELLIGENCE
# ============================================================

from announcement_engine import generate_alert


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="RailMind AI API",
    description=(
        "Backend API for RailMind AI railway "
        "crowd congestion intelligence."
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================
# Required so Faizan's frontend can communicate with
# the Python backend during development.
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# DATA PATH
# ============================================================

LIVE_SIGNAL = (
    PROJECT_DIR
    / "data"
    / "live"
    / "live_crowd_signal.csv"
)


# ============================================================
# LOAD LIVE CROWD STATE
# ============================================================

def get_live_crowd_state():

    if not LIVE_SIGNAL.exists():

        return {
            "available": False,
            "error": (
                "live_crowd_signal.csv not found"
            )
        }


    df = pd.read_csv(
        LIVE_SIGNAL
    )


    if df.empty:

        return {
            "available": False,
            "error": (
                "Live crowd signal is empty"
            )
        }


    # --------------------------------------------------------
    # Forecasting-ready observations
    # --------------------------------------------------------

    valid = df[
        df["growth_rate_5s"].notna()
    ].copy()


    if valid.empty:

        latest = df.iloc[-1]

    else:

        valid_acceleration = valid[
            valid["acceleration"].notna()
        ]

        if not valid_acceleration.empty:

            latest = valid_acceleration.iloc[-1]

        else:

            latest = valid.iloc[-1]


    # --------------------------------------------------------
    # Safe numeric extraction
    # --------------------------------------------------------

    crowd = float(
        latest["crowd"]
    )


    growth = float(
        latest["growth_rate_5s"]
    ) if pd.notna(
        latest["growth_rate_5s"]
    ) else 0.0


    acceleration = float(
        latest["acceleration"]
    ) if pd.notna(
        latest["acceleration"]
    ) else 0.0


    return {

        "available": True,

        "video_timestamp": int(
            latest["time_sec"]
        ),

        "crowd": round(
            crowd,
            2
        ),

        "growth_rate": round(
            growth,
            2
        ),

        "acceleration": round(
            acceleration,
            2
        ),

        "trend": str(
            latest["trend"]
        ),

        "crowd_level": str(
            latest["crowd_level"]
        )
    }


# ============================================================
# BUILD DASHBOARD STATE
# ============================================================

def build_dashboard_state():

    crowd = get_live_crowd_state()


    if not crowd["available"]:

        return {
            "status": "NO_DATA",
            "message": crowd["error"]
        }


    # --------------------------------------------------------
    # Demo station time
    #
    # Later this will come from station/system clock.
    # --------------------------------------------------------

    station_time = "18:40"


    # --------------------------------------------------------
    # Run complete RailMind intelligence
    # --------------------------------------------------------

    result = generate_alert(

        station_time,

        crowd["crowd"],

        crowd["growth_rate"],

        crowd["acceleration"]
    )


    baseline = result[
        "baseline"
    ]

    schedule = baseline[
        "schedule"
    ]

    best = result[
        "best_intervention"
    ]

    alert = result[
        "operator_alert"
    ]


    # ========================================================
    # RETURN CLEAN API CONTRACT
    # ========================================================

    return {

        "status": "OK",

        "station": {

            "name":
                "PUNE JUNCTION",

            "code":
                "PUNE",

            "time":
                station_time
        },


        # ----------------------------------------------------
        # LIVE CROWD
        # ----------------------------------------------------

        "crowd": {

            "current":
                crowd["crowd"],

            "growth_rate":
                crowd["growth_rate"],

            "acceleration":
                crowd["acceleration"],

            "trend":
                crowd["trend"],

            "level":
                crowd["crowd_level"],

            "video_timestamp":
                crowd["video_timestamp"]
        },


        # ----------------------------------------------------
        # SCHEDULE
        # ----------------------------------------------------

        "schedule": {

            "movements_5min":
                schedule[
                    "total_movements_5min"
                ],

            "movements_10min":
                schedule[
                    "total_movements_10min"
                ],

            "movements_15min":
                schedule[
                    "total_movements_15min"
                ],

            "movements_30min":
                schedule[
                    "total_movements_30min"
                ],

            "simultaneous_pressure":
                schedule[
                    "simultaneous_pressure"
                ],

            "activity_level":
                schedule[
                    "activity_level"
                ],

            "next_event": {

                "time":
                    schedule[
                        "next_event_time"
                    ],

                "type":
                    schedule[
                        "next_event_type"
                    ],

                "train_number":
                    schedule[
                        "next_train_no"
                    ],

                "train_name":
                    schedule[
                        "next_train_name"
                    ]
            }
        },


        # ----------------------------------------------------
        # FORECAST
        # ----------------------------------------------------

        "forecast": {

            "horizon_minutes":
                5,

            "predicted_crowd":
                round(
                    baseline[
                        "future_crowd_5min"
                    ],
                    2
                ),

            "predicted_increase":
                round(
                    baseline[
                        "future_crowd_5min"
                    ]
                    -
                    baseline[
                        "current_crowd"
                    ],
                    2
                ),

            "surge_score":
                baseline[
                    "surge_score"
                ]
        },


        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        "risk": {

            "level":
                baseline[
                    "risk"
                ],

            "score":
                baseline[
                    "surge_score"
                ]
        },


        # ----------------------------------------------------
        # INTERVENTION
        # ----------------------------------------------------

        "intervention": {

            "recommended":
                best[
                    "intervention"
                ],

            "description":
                best[
                    "description"
                ],

            "projected_crowd":
                best[
                    "predicted_crowd"
                ],

            "projected_reduction":
                best[
                    "crowd_reduction"
                ],

            "projected_risk":
                best[
                    "risk"
                ],

            "assumption":
                (
                    best[
                        "reduction"
                    ] * 100
                )
        },


        # ----------------------------------------------------
        # OPERATOR ALERT
        # ----------------------------------------------------

        "operator_alert": {

            "risk":
                alert[
                    "risk"
                ],

            "reasons":
                alert[
                    "reasons"
                ],

            "recommended_action":
                alert[
                    "recommended_intervention"
                ]
        },


        # ----------------------------------------------------
        # ANNOUNCEMENTS
        # ----------------------------------------------------

        "announcements": {

            "english":
                result[
                    "english"
                ],

            "hindi":
                result[
                    "hindi"
                ],

            "marathi":
                result[
                    "marathi"
                ]
        }

    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "project":
            "RailMind AI",

        "status":
            "Backend online",

        "version":
            "1.0.0",

        "station":
            "PUNE JUNCTION"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    crowd = get_live_crowd_state()

    return {

        "status":
            "healthy",

        "service":
            "RailMind AI Backend",

        "crowd_data":
            crowd["available"]
    }


# ============================================================
# DASHBOARD API
# ============================================================

@app.get("/api/dashboard")
def dashboard():

    return build_dashboard_state()

# ============================================================
# CROWD HISTORY API
# ============================================================

@app.get("/api/crowd/history")
def crowd_history():

    if not LIVE_SIGNAL.exists():

        return {
            "status": "NO_DATA",
            "history": []
        }


    df = pd.read_csv(
        LIVE_SIGNAL
    )


    if df.empty:

        return {
            "status": "NO_DATA",
            "history": []
        }


    history = []


    for _, row in df.iterrows():

        history.append({

            "time_sec":
                int(row["time_sec"]),

            "crowd":
                round(
                    float(row["crowd"]),
                    2
                ),

            "crowd_mean_5s":
                round(
                    float(
                        row["crowd_mean_5s"]
                    ),
                    2
                )
                if pd.notna(
                    row["crowd_mean_5s"]
                )
                else None,

            "growth_rate":
                round(
                    float(
                        row["growth_rate_5s"]
                    ),
                    2
                )
                if pd.notna(
                    row["growth_rate_5s"]
                )
                else None,

            "trend":
                str(
                    row["trend"]
                ),

            "level":
                str(
                    row["crowd_level"]
                )
        })


    return {

        "status": "OK",

        "total_points":
            len(history),

        "history":
            history
    }
# ============================================================
# SCHEDULE INTELLIGENCE API
# ============================================================

@app.get("/api/schedule")
def schedule_api():

    # Use the same station time as the current dashboard demo.
    station_time = "18:40"

    # Run the existing RailMind intelligence engine.
    crowd = get_live_crowd_state()

    if not crowd["available"]:
        return {
            "status": "NO_DATA",
            "message": crowd["error"]
        }

    result = generate_alert(
        station_time,
        crowd["crowd"],
        crowd["growth_rate"],
        crowd["acceleration"]
    )

    schedule = result["baseline"]["schedule"]

    return {
        "status": "OK",

        "station": {
            "name": "PUNE JUNCTION",
            "code": "PUNE",
            "time": station_time
        },

        "movements": {
            "5min": schedule["total_movements_5min"],
            "10min": schedule["total_movements_10min"],
            "15min": schedule["total_movements_15min"],
            "30min": schedule["total_movements_30min"]
        },

        "simultaneous_pressure":
            schedule["simultaneous_pressure"],

        "activity_level":
            schedule["activity_level"],

        "next_event": {
            "time":
                schedule["next_event_time"],

            "type":
                schedule["next_event_type"],

            "train_number":
                schedule["next_train_no"],

            "train_name":
                schedule["next_train_name"]
        }
    }
# ============================================================
# UPCOMING TRAIN EVENTS API
# ============================================================

# ============================================================
# UPCOMING TRAIN EVENTS API
# ============================================================

SCHEDULE_FILE = (
    PROJECT_DIR
    / "Dataset"
    / "railway_schedule.csv"
)


@app.get("/api/trains/next")
def upcoming_trains():

    if not SCHEDULE_FILE.exists():

        return {
            "status": "NO_DATA",
            "message": "railway_schedule.csv not found",
            "trains": []
        }


    # --------------------------------------------------------
    # Load railway schedule
    # --------------------------------------------------------

    df = pd.read_csv(
        SCHEDULE_FILE
    )


    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
    )


    required_columns = [
        "Train No",
        "Train Name",
        "Station Code",
        "Station Name",
        "Arrival time",
        "Departure Time"
    ]


    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]


    if missing:

        return {
            "status": "ERROR",
            "message": (
                "Missing required columns"
            ),
            "missing_columns": missing,
            "trains": []
        }


    # --------------------------------------------------------
    # Pune Junction only
    # --------------------------------------------------------

    pune = df[
        df["Station Code"]
        .astype(str)
        .str.strip()
        .str.upper()
        == "PUNE"
    ].copy()


    if pune.empty:

        return {
            "status": "NO_DATA",
            "message": (
                "No Pune Junction records found"
            ),
            "trains": []
        }


    # --------------------------------------------------------
    # Demo station time
    # --------------------------------------------------------

    station_time = "18:40:00"


    current_time = pd.to_datetime(
        station_time,
        format="%H:%M:%S"
    )


    # --------------------------------------------------------
    # Convert arrival/departure to datetime
    # --------------------------------------------------------

    pune["arrival_dt"] = pd.to_datetime(
        pune["Arrival time"].astype(str),
        format="%H:%M:%S",
        errors="coerce"
    )


    pune["departure_dt"] = pd.to_datetime(
        pune["Departure Time"].astype(str),
        format="%H:%M:%S",
        errors="coerce"
    )


    # --------------------------------------------------------
    # Build event list
    # --------------------------------------------------------

    events = []


    for _, row in pune.iterrows():

        train_no = str(
            row["Train No"]
        ).strip()

        train_name = str(
            row["Train Name"]
        ).strip()


        # ----------------------------------------------------
        # Arrival event
        # ----------------------------------------------------

        arrival = row["arrival_dt"]


        if pd.notna(arrival):

            if (
                arrival >= current_time
                and
                arrival <= current_time
                + pd.Timedelta(minutes=30)
            ):

                events.append({

                    "time":
                        arrival.strftime(
                            "%H:%M"
                        ),

                    "type":
                        "ARRIVAL",

                    "train_number":
                        train_no,

                    "train_name":
                        train_name
                })


        # ----------------------------------------------------
        # Departure event
        # ----------------------------------------------------

        departure = row["departure_dt"]


        if pd.notna(departure):

            if (
                departure >= current_time
                and
                departure <= current_time
                + pd.Timedelta(minutes=30)
            ):

                events.append({

                    "time":
                        departure.strftime(
                            "%H:%M"
                        ),

                    "type":
                        "DEPARTURE",

                    "train_number":
                        train_no,

                    "train_name":
                        train_name
                })


    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    events.sort(
        key=lambda x: (
            x["time"],
            0 if x["type"] == "ARRIVAL" else 1
        )
    )


    # --------------------------------------------------------
    # Remove exact duplicate events
    # --------------------------------------------------------

    unique_events = []

    seen = set()


    for event in events:

        key = (
            event["time"],
            event["type"],
            event["train_number"]
        )


        if key not in seen:

            seen.add(key)

            unique_events.append(
                event
            )


    # --------------------------------------------------------
    # Return API response
    # --------------------------------------------------------

    return {

        "status": "OK",

        "station": {

            "name":
                "PUNE JUNCTION",

            "code":
                "PUNE",

            "time":
                "18:40"
        },

        "window_minutes":
            30,

        "total_events":
            len(unique_events),

        "trains":
            unique_events
    }
# ============================================================
# INTERVENTION SIMULATION API
# ============================================================

@app.get("/api/interventions")
def intervention_api():

    # --------------------------------------------------------
    # Get current live crowd state
    # --------------------------------------------------------

    crowd = get_live_crowd_state()

    if not crowd["available"]:

        return {
            "status": "NO_DATA",
            "message": crowd["error"]
        }


    # --------------------------------------------------------
    # Current RailMind demo scenario
    # --------------------------------------------------------

    current_time = "18:40"

    current_crowd = float(
        crowd["crowd"]
    )

    growth_rate = float(
        crowd["growth_rate"]
    )

    acceleration = float(
        crowd["acceleration"]
    )


    # --------------------------------------------------------
    # Run EXISTING intervention engine
    # --------------------------------------------------------

    baseline, results = run_simulation(

        current_time,

        current_crowd,

        growth_rate,

        acceleration
    )


    # --------------------------------------------------------
    # Select recommended intervention
    # --------------------------------------------------------

    best = select_best_intervention(
        results
    )


    # --------------------------------------------------------
    # Prepare frontend-safe results
    # --------------------------------------------------------

    interventions = []


    for result in results:

        interventions.append({

            "intervention":
                result["intervention"],

            "reduction":
                result["reduction"],

            "predicted_crowd":
                result["predicted_crowd"],

            "crowd_reduction":
                result["crowd_reduction"],

            "effective_growth":
                result["effective_growth"],

            "risk_score":
                result["risk_score"],

            "risk":
                result["risk"],

            "description":
                result["description"]
        })


    # --------------------------------------------------------
    # Return API response
    # --------------------------------------------------------

    return {

        "status": "OK",

        "station": {

            "name":
                "PUNE JUNCTION",

            "code":
                "PUNE",

            "time":
                current_time
        },

        "baseline": {

            "current_crowd":
                round(
                    baseline["current_crowd"],
                    2
                ),

            "predicted_crowd":
                round(
                    baseline["future_crowd_5min"],
                    2
                ),

            "growth_rate":
                round(
                    baseline["growth_rate"],
                    2
                ),

            "acceleration":
                round(
                    baseline["acceleration"],
                    2
                ),

            "risk":
                baseline["risk"]
        },

        "recommended_intervention": {

            "action":
                best["intervention"],

            "predicted_crowd":
                best["predicted_crowd"],

            "crowd_reduction":
                best["crowd_reduction"],

            "risk_score":
                best["risk_score"],

            "risk":
                best["risk"],

            "effective_growth":
                best["effective_growth"],

            "description":
                best["description"]
        },

        "interventions":
            interventions
    }
# ============================================================
# MULTILINGUAL ANNOUNCEMENT API
# ============================================================

# ============================================================
# MULTILINGUAL ANNOUNCEMENT API
# ============================================================

@app.get("/api/announcements")
def announcements_api():

    crowd = get_live_crowd_state()

    if not crowd["available"]:
        return {
            "status": "NO_DATA",
            "announcements": {}
        }

    current_time = "18:40"

    # Use the existing RailMind decision engine.
    result = generate_alert(
        current_time,
        crowd["crowd"],
        crowd["growth_rate"],
        crowd["acceleration"]
    )

    # --------------------------------------------------------
    # Extract values safely from the existing result
    # --------------------------------------------------------

    risk = (
        result.get("risk")
        or result.get("risk_level")
        or result.get("baseline", {}).get("risk")
        or "UNKNOWN"
    )

    action = (
        result.get("action")
        or result.get("recommended_action")
        or result.get("baseline", {}).get("action")
        or "MONITOR CROWD CONDITIONS"
    )

    # --------------------------------------------------------
    # Multilingual announcements
    # --------------------------------------------------------

    english = (
        "Attention passengers. "
        "Crowd management measures are currently being activated "
        "at Pune Junction. "
        "Regulate incoming passenger flow and redirect passengers "
        "toward less-loaded platform areas. "
        "Please remain calm and keep emergency access routes clear."
    )

    hindi = (
        "यात्रियों का ध्यान आकर्षित किया जाता है। "
        "पुणे जंक्शन पर भीड़ प्रबंधन के उपाय सक्रिय किए जा रहे हैं। "
        "प्रवेश को नियंत्रित किया जा सकता है और यात्रियों को "
        "कम भीड़ वाले क्षेत्रों की ओर निर्देशित किया जा सकता है। "
        "कृपया शांत रहें और आपातकालीन मार्गों को खाली रखें।"
    )

    marathi = (
        "प्रवाशांचे लक्ष वेधण्यात येत आहे. "
        "पुणे जंक्शनवर गर्दी नियंत्रणाच्या उपाययोजना सक्रिय "
        "करण्यात येत आहेत. "
        "प्रवेश नियंत्रित करण्यात येईल आणि प्रवाशांना "
        "कमी गर्दी असलेल्या भागांकडे मार्गदर्शन केले जाईल. "
        "कृपया शांत राहावे आणि आपत्कालीन मार्ग मोकळे ठेवावेत."
    )

    return {

        "status": "OK",

        "station": {
            "name": "PUNE JUNCTION",
            "code": "PUNE",
            "time": current_time
        },

        "risk": risk,

        "action": action,

        "announcements": {

            "english": english,

            "hindi": hindi,

            "marathi": marathi
        }
    }
# ============================================================
# RAILMIND AI - STATION INTELLIGENCE
# ============================================================

@app.get("/api/station/state")
def station_state():

    # --------------------------------------------------------
    # Current RailMind state
    # --------------------------------------------------------

    crowd = get_live_crowd_state()

    if not crowd["available"]:
        return {
            "status": "NO_DATA",
            "message": crowd["error"]
        }

    current_crowd = float(crowd["crowd"])
    growth_rate = float(crowd["growth_rate"])

    # --------------------------------------------------------
    # DEMO STATION MODEL
    #
    # Platform-level data is currently simulated.
    # It will later be replaced by camera-zone inputs.
    # --------------------------------------------------------

    platforms = [
        {
            "platform": 1,
            "status": "LOW",
            "crowd_index": 28,
            "recommended": False
        },
        {
            "platform": 2,
            "status": "MEDIUM",
            "crowd_index": 52,
            "recommended": True
        },
        {
            "platform": 3,
            "status": "HIGH",
            "crowd_index": 76,
            "recommended": False
        },
        {
            "platform": 4,
            "status": "LOW",
            "crowd_index": 31,
            "recommended": False
        },
        {
            "platform": 5,
            "status": "CRITICAL",
            "crowd_index": 91,
            "recommended": False
        }
    ]

    # --------------------------------------------------------
    # Bottlenecks
    # --------------------------------------------------------

    bottlenecks = [
        {
            "location": "Platform 5 access",
            "status": "CRITICAL",
            "reason": "High passenger concentration"
        },
        {
            "location": "Main footbridge",
            "status": "AT RISK",
            "reason": "Increasing passenger flow"
        },
        {
            "location": "Platform 2 entry",
            "status": "CLEAR",
            "reason": "Available movement capacity"
        }
    ]

    # --------------------------------------------------------
    # Emergency corridor
    # --------------------------------------------------------

    if current_crowd >= 15 or growth_rate >= 1.0:
        emergency_status = "BLOCKED"
    elif current_crowd >= 8 or growth_rate > 0.5:
        emergency_status = "AT RISK"
    else:
        emergency_status = "CLEAR"

    # --------------------------------------------------------
    # Recommended platform
    # --------------------------------------------------------

    available_platforms = [
        p for p in platforms
        if p["status"] in ["LOW", "MEDIUM"]
    ]

    if available_platforms:
        recommended_platform = min(
            available_platforms,
            key=lambda x: x["crowd_index"]
        )["platform"]
    else:
        recommended_platform = None

    # --------------------------------------------------------
    # Recommended gate
    # --------------------------------------------------------

    if emergency_status == "BLOCKED":
        recommended_gate = "OPEN GATE B"
    elif emergency_status == "AT RISK":
        recommended_gate = "REGULATE GATE A"
    else:
        recommended_gate = "NORMAL GATE OPERATION"

    # --------------------------------------------------------
    # Station safety state
    # --------------------------------------------------------

    if emergency_status == "BLOCKED":
        safety_status = "CRITICAL"
    elif emergency_status == "AT RISK":
        safety_status = "HIGH"
    else:
        safety_status = "NORMAL"

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "status": "OK",

        "station": {
            "name": "PUNE JUNCTION",
            "code": "PUNE",
            "mode": "DEMO"
        },

        "crowd": {
            "current": round(current_crowd, 2),
            "growth_rate": round(growth_rate, 2)
        },

        "platforms": platforms,

        "bottlenecks": bottlenecks,

        "emergency_corridor": {
            "status": emergency_status,
            "location": "Main emergency access corridor"
        },

        "recommendation": {
            "platform": recommended_platform,
            "gate": recommended_gate
        },

        "station_safety": {
            "status": safety_status
        }
    }
# ============================================================
# RAILMIND AI - SMART PASSENGER ALERT SYSTEM
# ============================================================

@app.get("/api/passenger-alerts")
def passenger_alerts_api():

    # Get current station intelligence
    station = station_state()

    if station.get("status") != "OK":
        return station

    platforms = station["platforms"]
    emergency = station["emergency_corridor"]
    recommendation = station["recommendation"]
    safety = station["station_safety"]

    # --------------------------------------------------------
    # Identify critical/high-risk platforms
    # --------------------------------------------------------

    critical_platforms = [
        p["platform"]
        for p in platforms
        if p["status"] == "CRITICAL"
    ]

    high_platforms = [
        p["platform"]
        for p in platforms
        if p["status"] == "HIGH"
    ]

    recommended_platform = recommendation["platform"]

    # --------------------------------------------------------
    # Location-specific passenger message
    # --------------------------------------------------------

    if critical_platforms and recommended_platform:

        platform_text = ", ".join(
            f"Platform {p}" for p in critical_platforms
        )

        english = (
            f"Passenger advisory for {platform_text}. "
            f"These areas currently have high crowd concentration. "
            f"Passengers are advised to use Platform {recommended_platform} "
            f"where possible. Please follow railway staff instructions "
            f"and keep emergency access routes clear."
        )

        hindi = (
            f"{platform_text} पर यात्रियों के लिए सूचना। "
            f"इन क्षेत्रों में वर्तमान में अधिक भीड़ है। "
            f"यात्रियों से अनुरोध है कि संभव हो तो "
            f"प्लेटफॉर्म {recommended_platform} का उपयोग करें। "
            f"कृपया रेलवे कर्मचारियों के निर्देशों का पालन करें "
            f"और आपातकालीन मार्ग खुले रखें।"
        )

        marathi = (
            f"{platform_text} वरील प्रवाशांसाठी सूचना. "
            f"या भागात सध्या मोठ्या प्रमाणात गर्दी आहे. "
            f"शक्य असल्यास प्रवाशांनी प्लॅटफॉर्म "
            f"{recommended_platform} चा वापर करावा. "
            f"कृपया रेल्वे कर्मचाऱ्यांच्या सूचनांचे पालन करावे "
            f"आणि आपत्कालीन मार्ग मोकळे ठेवावेत."
        )

    else:

        english = (
            "Passenger movement is currently being monitored. "
            "Please follow railway staff instructions and "
            "keep emergency access routes clear."
        )

        hindi = (
            "यात्रियों की आवाजाही पर वर्तमान में निगरानी रखी जा रही है। "
            "कृपया रेलवे कर्मचारियों के निर्देशों का पालन करें "
            "और आपातकालीन मार्ग खुले रखें।"
        )

        marathi = (
            "प्रवाशांच्या हालचालींवर सध्या लक्ष ठेवले जात आहे. "
            "कृपया रेल्वे कर्मचाऱ्यांच्या सूचनांचे पालन करावे "
            "आणि आपत्कालीन मार्ग मोकळे ठेवावेत."
        )

    # --------------------------------------------------------
    # Emergency corridor alert
    # --------------------------------------------------------

    if emergency["status"] == "BLOCKED":

        emergency_alert = (
            "Emergency corridor is currently blocked. "
            "Passengers must immediately clear the marked "
            "emergency access route."
        )

    elif emergency["status"] == "AT RISK":

        emergency_alert = (
            "Emergency corridor is at risk. "
            "Please avoid stopping or waiting in the marked "
            "emergency access route."
        )

    else:

        emergency_alert = (
            "Emergency access corridor is currently clear."
        )

    # --------------------------------------------------------
    # Delivery channels
    #
    # These are prototype/demo delivery states.
    # --------------------------------------------------------

    channels = {
        "public_announcement": {
            "available": True,
            "status": "READY"
        },

        "display_board": {
            "available": True,
            "status": "READY"
        },

        "mobile_alert": {
            "available": True,
            "status": "DEMO"
        },

        "sms": {
            "available": True,
            "status": "DEMO"
        },

        "whatsapp": {
            "available": True,
            "status": "DEMO"
        }
    }

    # --------------------------------------------------------
    # Alert priority
    # --------------------------------------------------------

    if safety["status"] == "CRITICAL":
        priority = "CRITICAL"
    elif safety["status"] == "HIGH":
        priority = "HIGH"
    else:
        priority = "NORMAL"

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "status": "OK",

        "station": {
            "name": station["station"]["name"],
            "code": station["station"]["code"]
        },

        "priority": priority,

        "affected_platforms": {
            "critical": critical_platforms,
            "high": high_platforms
        },

        "recommended_platform": recommended_platform,

        "emergency_corridor": emergency,

        "emergency_alert": emergency_alert,

        "alerts": {
            "english": english,
            "hindi": hindi,
            "marathi": marathi
        },

        "delivery_channels": channels,

        "location_specific": True,

        "prototype_note": (
            "Passenger communication channels are represented "
            "as prototype/demo outputs. Production deployment "
            "would connect them to authorized railway systems."
        )
    }
# ============================================================
# RAILMIND AI - VIDEO UPLOAD
# ============================================================

VIDEO_UPLOAD_DIR = Path("data/live/uploads")
VIDEO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/api/video/upload")
async def upload_video(file: UploadFile = File(...)):

    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv"}

    original_name = file.filename or "uploaded_video.mp4"
    extension = Path(original_name).suffix.lower()

    if extension not in allowed_extensions:
        return {
            "status": "ERROR",
            "message": "Unsupported video format.",
            "allowed_formats": [
                ".mp4",
                ".avi",
                ".mov",
                ".mkv"
            ]
        }

    # --------------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------------

    video_id = uuid.uuid4().hex[:12]

    saved_name = f"{video_id}{extension}"
    saved_path = VIDEO_UPLOAD_DIR / saved_name

    # --------------------------------------------------------
    # Save uploaded video
    # --------------------------------------------------------

    try:

        with open(saved_path, "wb") as buffer:

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception as e:

        return {
            "status": "ERROR",
            "message": f"Could not save video: {str(e)}"
        }

    # --------------------------------------------------------
    # Return upload information
    # --------------------------------------------------------

    return {

        "status": "OK",

        "video": {
            "video_id": video_id,
            "original_name": original_name,
            "saved_name": saved_name,
            "path": str(saved_path),
            "size_bytes": saved_path.stat().st_size
        },

        "message": "Video uploaded successfully."
    }
# ============================================================
# RAILMIND AI - VIDEO YOLO ANALYSIS
# ============================================================

from ultralytics import YOLO
import cv2
import pandas as pd
import numpy as np


# Load trained RailMind model once when backend starts
YOLO_MODEL_PATH = Path(
    "runs/RailMind/pune_person/weights/best.pt"
)

rail_mind_model = YOLO(str(YOLO_MODEL_PATH))


@app.post("/api/video/analyze")
# ============================================================
# RAILMIND AI - VIDEO YOLO ANALYSIS
# ============================================================

@app.post("/api/video/analyze")
def analyze_uploaded_video(video_id: str):

    # --------------------------------------------------------
    # 1. Find uploaded video
    # --------------------------------------------------------

    upload_dir = Path("data/live/uploads")

    matching_files = list(
        upload_dir.glob(f"{video_id}.*")
    )

    if not matching_files:
        return {
            "status": "ERROR",
            "message": "Uploaded video not found.",
            "video_id": video_id
        }

    video_path = matching_files[0]

    # --------------------------------------------------------
    # 2. Open video
    # --------------------------------------------------------

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return {
            "status": "ERROR",
            "message": "Could not open video.",
            "video_id": video_id
        }

    fps = cap.get(cv2.CAP_PROP_FPS)

    if not fps or fps <= 0:
        fps = 30.0

    frame_count = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = frame_count / fps

    # --------------------------------------------------------
    # 3. Analyze approximately one frame per second
    # --------------------------------------------------------

    results = []

    second = 0

    while True:

        target_frame = int(second * fps)

        if target_frame >= frame_count:
            break

        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            target_frame
        )

        success, frame = cap.read()

        if not success:
            break

        # ----------------------------------------------------
        # YOLO inference
        # ----------------------------------------------------

        prediction = rail_mind_model(
            frame,
            verbose=False,
            conf=0.25
        )[0]

        # ----------------------------------------------------
        # Count detected people
        # ----------------------------------------------------

        person_count = 0

        if prediction.boxes is not None:

            for cls in prediction.boxes.cls:

                if int(cls) == 0:
                    person_count += 1

        results.append({
            "time_sec": second,
            "crowd": person_count
        })

        second += 1

    cap.release()

    # --------------------------------------------------------
    # 4. Check whether frames were analyzed
    # --------------------------------------------------------

    if not results:
        return {
            "status": "ERROR",
            "message": "No frames could be analyzed.",
            "video_id": video_id
        }

    # --------------------------------------------------------
    # 5. Create dataframe
    # --------------------------------------------------------

    df = pd.DataFrame(results)

    # --------------------------------------------------------
    # 6. QUALITY-AWARE CROWD STATISTICS
    # --------------------------------------------------------

    # Do NOT trust only the final frame.
    # Use the median of the latest 5 seconds.

    recent_window_size = min(
        5,
        len(df)
    )

    recent_values = (
        df["crowd"]
        .tail(recent_window_size)
        .astype(float)
    )

    current_crowd = float(
        recent_values.median()
    )

    average_crowd = float(
        df["crowd"].mean()
    )

    maximum_crowd = int(
        df["crowd"].max()
    )

    minimum_crowd = int(
        df["crowd"].min()
    )

    # --------------------------------------------------------
    # 7. Calculate short-term growth
    # --------------------------------------------------------

    if len(df) >= 10:

        recent_mean = float(
            df["crowd"]
            .tail(5)
            .mean()
        )

        previous_mean = float(
            df["crowd"]
            .iloc[-10:-5]
            .mean()
        )

        growth = (
            recent_mean -
            previous_mean
        )

    else:

        growth = 0.0

    # --------------------------------------------------------
    # 8. Determine trend
    # --------------------------------------------------------

    if growth >= 1.0:

        trend = "RISING"

    elif growth <= -1.0:

        trend = "FALLING"

    else:

        trend = "STABLE"

    # --------------------------------------------------------
    # 9. Save crowd signal
    # --------------------------------------------------------

    output_dir = Path(
        "data/live/analysis"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    signal_path = (
        output_dir /
        f"{video_id}_crowd.csv"
    )

    df.to_csv(
        signal_path,
        index=False
    )

    # --------------------------------------------------------
    # 10. Final response
    # --------------------------------------------------------

    return {

        "status": "OK",

        "video": {

            "video_id": video_id,

            "filename": video_path.name,

            "duration_sec": round(
                duration,
                2
            ),

            "analyzed_seconds": len(df)
        },

        "crowd": {

            "current": round(
                current_crowd,
                2
            ),

            "average": round(
                average_crowd,
                2
            ),

            "minimum": minimum_crowd,

            "maximum": maximum_crowd,

            "trend": trend,

            "growth": round(
                growth,
                2
            )
        },

        "signal_file": str(
            signal_path
        ),

        "message":
            "Video analyzed successfully using RailMind YOLO model."
    }
# ============================================================
# RAILMIND AI - MASTER VIDEO TO DECISION API
# ============================================================

@app.post("/api/demo/analyze")
# ============================================================
# RAILMIND AI - MASTER VIDEO TO DECISION API
# ============================================================

@app.post("/api/demo/analyze")
def demo_analyze(video_id: str):

    # --------------------------------------------------------
    # 1. Find uploaded video's analysis CSV
    # --------------------------------------------------------

    analysis_dir = Path("data/live/analysis")

    signal_path = (
        analysis_dir / f"{video_id}_crowd.csv"
    )

    if not signal_path.exists():
        return {
            "status": "ERROR",
            "message": "Video analysis not found.",
            "video_id": video_id
        }

    # --------------------------------------------------------
    # 2. Load YOLO crowd signal
    # --------------------------------------------------------

    df = pd.read_csv(signal_path)

    if df.empty:
        return {
            "status": "ERROR",
            "message": "Crowd analysis is empty.",
            "video_id": video_id
        }

    # --------------------------------------------------------
    # 3. Calculate current crowd
    # --------------------------------------------------------

    recent_values = (
        df["crowd"]
        .tail(min(5, len(df)))
        .astype(float)
    )

    current_crowd = float(
        recent_values.median()
    )

    # --------------------------------------------------------
    # 4. Calculate growth rate
    # --------------------------------------------------------

    if len(df) >= 10:

        recent_mean = float(
            df["crowd"]
            .tail(5)
            .mean()
        )

        previous_mean = float(
            df["crowd"]
            .iloc[-10:-5]
            .mean()
        )

        growth_rate = (
            recent_mean -
            previous_mean
        )

    else:

        growth_rate = 0.0

    # --------------------------------------------------------
    # 5. Calculate acceleration
    # --------------------------------------------------------

    if len(df) >= 15:

        first_mean = float(
            df["crowd"]
            .iloc[-15:-10]
            .mean()
        )

        second_mean = float(
            df["crowd"]
            .iloc[-10:-5]
            .mean()
        )

        third_mean = float(
            df["crowd"]
            .tail(5)
            .mean()
        )

        acceleration = (
            (third_mean - second_mean)
            -
            (second_mean - first_mean)
        )

    else:

        acceleration = 0.0

    # --------------------------------------------------------
    # 6. Determine trend
    # --------------------------------------------------------

    if growth_rate >= 1.0:

        trend = "RISING"

    elif growth_rate <= -1.0:

        trend = "FALLING"

    else:

        trend = "STABLE"

    # --------------------------------------------------------
    # 7. Run existing RailMind intelligence engine
    # --------------------------------------------------------

    station_time = "18:40"

    result = generate_alert(
        station_time,
        current_crowd,
        growth_rate,
        acceleration
    )

    # --------------------------------------------------------
    # 8. Extract existing intelligence
    # --------------------------------------------------------

    baseline = result["baseline"]

    schedule = baseline["schedule"]

    best = result["best_intervention"]

    operator_alert = result["operator_alert"]

    # --------------------------------------------------------
    # 9. Get station intelligence
    # --------------------------------------------------------

    station = station_state()

    if station.get("status") != "OK":

        station = {
            "status": "NO_DATA"
        }

    # Use uploaded video's crowd values
    # so the master response remains consistent.

    if station.get("status") == "OK":

        station["crowd"]["current"] = round(
            current_crowd,
            2
        )

        station["crowd"]["growth_rate"] = round(
            growth_rate,
            2
        )

    # --------------------------------------------------------
    # 10. Get passenger alerts
    # --------------------------------------------------------

    passenger_alerts = passenger_alerts_api()

    # --------------------------------------------------------
    # 11. Get uploaded video information
    # --------------------------------------------------------

    upload_dir = Path("data/live/uploads")

    matching_files = list(
        upload_dir.glob(f"{video_id}.*")
    )

    if matching_files:

        filename = matching_files[0].name

    else:

        filename = video_id

    # --------------------------------------------------------
    # 12. Final master response
    # --------------------------------------------------------

    return {

        "status": "OK",

        # ----------------------------------------------------
        # STATION
        # ----------------------------------------------------

        "station": {

            "name": "PUNE JUNCTION",

            "code": "PUNE",

            "time": station_time
        },

        # ----------------------------------------------------
        # VIDEO
        # ----------------------------------------------------

        "video": {

            "video_id": video_id,

            "filename": filename
        },

        # ----------------------------------------------------
        # CROWD
        # ----------------------------------------------------

        "crowd": {

            "current":
                round(
                    current_crowd,
                    2
                ),

            "growth_rate":
                round(
                    growth_rate,
                    2
                ),

            "acceleration":
                round(
                    acceleration,
                    2
                ),

            "trend": trend
        },

        # ----------------------------------------------------
        # RAILWAY SCHEDULE
        # ----------------------------------------------------

        "schedule": {

            "movements_5min":
                schedule[
                    "total_movements_5min"
                ],

            "movements_10min":
                schedule[
                    "total_movements_10min"
                ],

            "movements_15min":
                schedule[
                    "total_movements_15min"
                ],

            "movements_30min":
                schedule[
                    "total_movements_30min"
                ],

            "simultaneous_pressure":
                schedule[
                    "simultaneous_pressure"
                ],

            "activity_level":
                schedule[
                    "activity_level"
                ],

            "next_event": {

                "time":
                    schedule[
                        "next_event_time"
                    ],

                "type":
                    schedule[
                        "next_event_type"
                    ],

                "train_number":
                    schedule[
                        "next_train_no"
                    ],

                "train_name":
                    schedule[
                        "next_train_name"
                    ]
            }
        },

        # ----------------------------------------------------
        # FORECAST
        # ----------------------------------------------------

        "forecast": {

            "horizon_minutes": 5,

            "predicted_crowd":
                round(
                    baseline[
                        "future_crowd_5min"
                    ],
                    2
                ),

            "predicted_increase":
                round(
                    baseline[
                        "future_crowd_5min"
                    ]
                    -
                    baseline[
                        "current_crowd"
                    ],
                    2
                ),

            "surge_score":
                baseline[
                    "surge_score"
                ]
        },

        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        "risk": {

            "level":
                baseline[
                    "risk"
                ],

            "score":
                baseline[
                    "surge_score"
                ]
        },

        # ----------------------------------------------------
        # INTERVENTION
        # ----------------------------------------------------

        "intervention": {

            "recommended":
                best[
                    "intervention"
                ],

            "description":
                best[
                    "description"
                ],

            "projected_crowd":
                best[
                    "predicted_crowd"
                ],

            "projected_reduction":
                best[
                    "crowd_reduction"
                ],

            "projected_risk":
                best[
                    "risk"
                ],

            "assumption":
                best[
                    "reduction"
                ] * 100
        },

        # ----------------------------------------------------
        # OPERATOR ALERT
        # ----------------------------------------------------

        "operator_alert":
            operator_alert,

        # ----------------------------------------------------
        # PLATFORM / STATION INTELLIGENCE
        # ----------------------------------------------------

        "platforms":
            station,

        # ----------------------------------------------------
        # PASSENGER ALERTS
        # ----------------------------------------------------

        "passenger_alerts":
            passenger_alerts,

        # ----------------------------------------------------
        # MULTILINGUAL ANNOUNCEMENTS
        # ----------------------------------------------------

        "announcements": {

            "english":
                result["english"],

            "hindi":
                result["hindi"],

            "marathi":
                result["marathi"]
        }
    }
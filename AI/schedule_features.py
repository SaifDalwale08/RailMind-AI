import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


# ============================================================
# RAILMIND AI - PUNE SCHEDULE FEATURE ENGINE
# ============================================================

SCHEDULE_PATH = Path(
    r"D:\RailMindAI\Dataset\railway_schedule.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("RAILMIND AI - PUNE SCHEDULE FEATURE ENGINE")
print("=" * 70)

df = pd.read_csv(
    SCHEDULE_PATH
)

# Clean column names
df.columns = df.columns.str.strip()

# Keep only Pune Junction records
pune = df[
    df["Station Code"]
    .astype(str)
    .str.strip()
    .str.upper()
    == "PUNE"
].copy()

print(f"\nPune records: {len(pune)}")
print(
    f"Unique trains: "
    f"{pune['Train No'].nunique()}"
)


# ============================================================
# TIME CONVERSION
# ============================================================

def time_to_minutes(value):

    try:

        value = str(value).strip()

        if value in [
            "",
            "nan",
            "00:00:00"
        ]:
            return None

        parts = value.split(":")

        hour = int(parts[0])
        minute = int(parts[1])

        return hour * 60 + minute

    except Exception:

        return None


pune["arrival_minutes"] = (
    pune["Arrival time"]
    .apply(time_to_minutes)
)

pune["departure_minutes"] = (
    pune["Departure Time"]
    .apply(time_to_minutes)
)


# ============================================================
# CREATE EVENT TABLE
# ============================================================

events = []

for _, row in pune.iterrows():

    train_no = str(
        row["Train No"]
    ).strip()

    train_name = str(
        row["Train Name"]
    ).strip()

    arrival = row[
        "arrival_minutes"
    ]

    departure = row[
        "departure_minutes"
    ]


    # --------------------------------------------------------
    # ARRIVAL EVENT
    # --------------------------------------------------------

    if arrival is not None:

        events.append({

            "train_no":
                train_no,

            "train_name":
                train_name,

            "event_type":
                "ARRIVAL",

            "time_minutes":
                arrival,

            "station":
                "PUNE"
        })


    # --------------------------------------------------------
    # DEPARTURE EVENT
    # --------------------------------------------------------

    if departure is not None:

        events.append({

            "train_no":
                train_no,

            "train_name":
                train_name,

            "event_type":
                "DEPARTURE",

            "time_minutes":
                departure,

            "station":
                "PUNE"
        })


events_df = pd.DataFrame(
    events
)


# ============================================================
# REMOVE INVALID EVENTS
# ============================================================

events_df = events_df[
    events_df["time_minutes"]
    .notna()
].copy()


events_df[
    "time_minutes"
] = events_df[
    "time_minutes"
].astype(int)


# ============================================================
# TIME FORMAT
# ============================================================

def minutes_to_time(minutes):

    minutes = int(minutes) % 1440

    hour = minutes // 60

    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


events_df[
    "time"
] = events_df[
    "time_minutes"
].apply(
    minutes_to_time
)


# ============================================================
# FEATURE ENGINE
# ============================================================

def calculate_features(
    current_time,
    window_5=5,
    window_10=10,
    window_15=15,
    window_30=30
):

    current_minutes = (
        time_to_minutes(
            current_time
        )
    )

    if current_minutes is None:

        raise ValueError(
            "Invalid time. "
            "Use HH:MM or HH:MM:SS."
        )


    # --------------------------------------------------------
    # Handle midnight
    # --------------------------------------------------------

    temp = events_df.copy()

    temp[
        "relative_time"
    ] = (
        temp["time_minutes"]
        -
        current_minutes
    )

    # Events after midnight are treated as next-day events
    temp.loc[
        temp["relative_time"] < -720,
        "relative_time"
    ] += 1440

    # Events far in the future that became positive
    # remain correctly positioned.


    # --------------------------------------------------------
    # Count events
    # --------------------------------------------------------

    def window_events(minutes):

        return temp[
            (
                temp[
                    "relative_time"
                ] >= 0
            )
            &
            (
                temp[
                    "relative_time"
                ] <= minutes
            )
        ]


    w5 = window_events(
        window_5
    )

    w10 = window_events(
        window_10
    )

    w15 = window_events(
        window_15
    )

    w30 = window_events(
        window_30
    )


    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    arrivals_5 = len(
        w5[
            w5["event_type"]
            == "ARRIVAL"
        ]
    )

    departures_5 = len(
        w5[
            w5["event_type"]
            == "DEPARTURE"
        ]
    )


    arrivals_10 = len(
        w10[
            w10["event_type"]
            == "ARRIVAL"
        ]
    )

    departures_10 = len(
        w10[
            w10["event_type"]
            == "DEPARTURE"
        ]
    )


    arrivals_15 = len(
        w15[
            w15["event_type"]
            == "ARRIVAL"
        ]
    )

    departures_15 = len(
        w15[
            w15["event_type"]
            == "DEPARTURE"
        ]
    )


    arrivals_30 = len(
        w30[
            w30["event_type"]
            == "ARRIVAL"
        ]
    )

    departures_30 = len(
        w30[
            w30["event_type"]
            == "DEPARTURE"
        ]
    )


    total_5 = (
        arrivals_5
        +
        departures_5
    )

    total_10 = (
        arrivals_10
        +
        departures_10
    )

    total_15 = (
        arrivals_15
        +
        departures_15
    )

    total_30 = (
        arrivals_30
        +
        departures_30
    )


    # --------------------------------------------------------
    # NEXT EVENT
    # --------------------------------------------------------

    future = temp[
        temp["relative_time"]
        >= 0
    ].sort_values(
        "relative_time"
    )


    if len(future) > 0:

        next_event = future.iloc[0]

        next_event_time = (
            next_event["time"]
        )

        next_event_type = (
            next_event[
                "event_type"
            ]
        )

        next_train_no = (
            next_event[
                "train_no"
            ]
        )

        next_train_name = (
            next_event[
                "train_name"
            ]
        )

        next_event_in = int(
            next_event[
                "relative_time"
            ]
        )

    else:

        next_event_time = None
        next_event_type = None
        next_train_no = None
        next_train_name = None
        next_event_in = None


    # --------------------------------------------------------
    # ACTIVITY SCORE
    # --------------------------------------------------------

    # Weighted toward immediate activity.
    #
    # 5 min  = strongest signal
    # 10 min = strong
    # 15 min = moderate
    # 30 min = background pressure

    activity_score = (

        total_5 * 0.40

        +

        total_10 * 0.30

        +

        total_15 * 0.20

        +

        total_30 * 0.10
    )


    # --------------------------------------------------------
    # ACTIVITY LEVEL
    # --------------------------------------------------------

    if activity_score >= 10:

        activity_level = (
            "VERY HIGH"
        )

    elif activity_score >= 6:

        activity_level = (
            "HIGH"
        )

    elif activity_score >= 3:

        activity_level = (
            "MEDIUM"
        )

    else:

        activity_level = (
            "LOW"
        )


    # --------------------------------------------------------
    # SIMULTANEOUS PRESSURE
    # --------------------------------------------------------

    # Count events occurring within
    # the same 5-minute interval.

    pressure = 0

    for _, event in w5.iterrows():

        close_events = w5[
            abs(
                w5[
                    "relative_time"
                ]
                -
                event[
                    "relative_time"
                ]
            ) <= 2
        ]

        pressure = max(
            pressure,
            len(close_events)
        )


    # --------------------------------------------------------
    # RETURN FEATURES
    # --------------------------------------------------------

    return {

        "current_time":
            current_time,

        "arrivals_5min":
            arrivals_5,

        "departures_5min":
            departures_5,

        "total_movements_5min":
            total_5,

        "arrivals_10min":
            arrivals_10,

        "departures_10min":
            departures_10,

        "total_movements_10min":
            total_10,

        "arrivals_15min":
            arrivals_15,

        "departures_15min":
            departures_15,

        "total_movements_15min":
            total_15,

        "arrivals_30min":
            arrivals_30,

        "departures_30min":
            departures_30,

        "total_movements_30min":
            total_30,

        "simultaneous_pressure":
            pressure,

        "activity_score":
            round(
                activity_score,
                2
            ),

        "activity_level":
            activity_level,

        "next_event_time":
            next_event_time,

        "next_event_type":
            next_event_type,

        "next_train_no":
            next_train_no,

        "next_train_name":
            next_train_name,

        "next_event_in_min":
            next_event_in
    }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("SCHEDULE INTELLIGENCE TEST")
    print("=" * 70)

    test_times = [
        "06:00",
        "10:00",
        "10:30",
        "18:20",
        "18:40"
    ]

    for test_time in test_times:

        result = calculate_features(
            test_time
        )

        print("\n" + "-" * 70)

        print(
            f"TIME: "
            f"{result['current_time']}"
        )

        print(
            f"5-min movements: "
            f"{result['total_movements_5min']}"
        )

        print(
            f"10-min movements: "
            f"{result['total_movements_10min']}"
        )

        print(
            f"15-min movements: "
            f"{result['total_movements_15min']}"
        )

        print(
            f"30-min movements: "
            f"{result['total_movements_30min']}"
        )

        print(
            f"Simultaneous pressure: "
            f"{result['simultaneous_pressure']}"
        )

        print(
            f"Activity score: "
            f"{result['activity_score']}"
        )

        print(
            f"Activity level: "
            f"{result['activity_level']}"
        )

        print(
            f"Next event: "
            f"{result['next_event_time']} | "
            f"{result['next_event_type']} | "
            f"{result['next_train_no']} | "
            f"{result['next_train_name']}"
        )
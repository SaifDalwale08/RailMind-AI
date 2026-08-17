import json
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

SCHEDULE_PATH = Path("Dataset/pune_schedule.json")


# ============================================================
# LOAD SCHEDULE
# ============================================================

def load_schedule():
    if not SCHEDULE_PATH.exists():
        raise FileNotFoundError(
            f"Schedule file not found: {SCHEDULE_PATH}"
        )

    with open(SCHEDULE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# TIME CONVERSION
# ============================================================

def time_to_minutes(time_string):
    """
    Convert HH:MM:SS into minutes from midnight.

    Example:
    18:40:00 -> 1120

    00:00:00 is treated as missing schedule information.
    """

    if not time_string:
        return None

    time_string = str(time_string).strip()

    if time_string == "00:00:00":
        return None

    try:
        time_obj = datetime.strptime(
            time_string,
            "%H:%M:%S"
        )

        return time_obj.hour * 60 + time_obj.minute

    except ValueError:
        return None


# ============================================================
# WINDOW CHECK
# ============================================================

def is_in_window(event_time, current_minutes, window_minutes):

    if event_time is None:
        return False

    end_minutes = current_minutes + window_minutes

    # Normal same-day window
    if end_minutes < 1440:

        return (
            current_minutes
            <= event_time
            <= end_minutes
        )

    # Window crosses midnight
    wrapped_end = end_minutes - 1440

    return (
        event_time >= current_minutes
        or event_time <= wrapped_end
    )


# ============================================================
# ACTIVITY CLASSIFICATION
# ============================================================

def calculate_activity(unique_trains, total_events):

    # Temporary prototype thresholds.
    # We will calibrate these later using real data.

    if unique_trains <= 2:
        return "LOW"

    elif unique_trains <= 5:
        return "MEDIUM"

    elif unique_trains <= 8:
        return "HIGH"

    else:
        return "VERY HIGH"


# ============================================================
# MAIN SCHEDULE ANALYSIS
# ============================================================

def get_schedule_activity(
    current_time,
    window_minutes=30
):

    schedule = load_schedule()

    current_minutes = time_to_minutes(current_time)

    if current_minutes is None:
        raise ValueError(
            "Invalid current time. Use HH:MM:SS"
        )

    arrivals = []
    departures = []

    # Used to prevent counting the same train twice
    unique_train_ids = set()

    events = []

    for train in schedule:

        train_no = str(
            train.get("Train No", "")
        ).strip()

        train_name = str(
            train.get("Train Name", "")
        ).strip()

        arrival = time_to_minutes(
            train.get("Arrival time")
        )

        departure = time_to_minutes(
            train.get("Departure Time")
        )

        # ----------------------------------------------------
        # ARRIVAL
        # ----------------------------------------------------

        if is_in_window(
            arrival,
            current_minutes,
            window_minutes
        ):

            unique_train_ids.add(train_no)

            event = {
                "time": train.get("Arrival time"),
                "type": "ARRIVAL",
                "train_no": train_no,
                "train_name": train_name,
                "source": train.get(
                    "Source Station Name"
                ),
                "destination": train.get(
                    "Destination Station Name"
                )
            }

            arrivals.append(event)
            events.append(event)

        # ----------------------------------------------------
        # DEPARTURE
        # ----------------------------------------------------

        if is_in_window(
            departure,
            current_minutes,
            window_minutes
        ):

            unique_train_ids.add(train_no)

            event = {
                "time": train.get("Departure Time"),
                "type": "DEPARTURE",
                "train_no": train_no,
                "train_name": train_name,
                "source": train.get(
                    "Source Station Name"
                ),
                "destination": train.get(
                    "Destination Station Name"
                )
            }

            departures.append(event)
            events.append(event)

    # ========================================================
    # SORT EVENTS BY TIME
    # ========================================================

    def sort_key(event):
        return time_to_minutes(event["time"])

    events.sort(key=sort_key)

    arrivals.sort(key=sort_key)
    departures.sort(key=sort_key)

    # ========================================================
    # UNIQUE TRAINS
    # ========================================================

    unique_trains = len(unique_train_ids)

    total_events = len(events)

    activity_level = calculate_activity(
        unique_trains,
        total_events
    )

    # ========================================================
    # NEXT EVENT
    # ========================================================

    next_event = events[0] if events else None

    # ========================================================
    # PEAK ACTIVITY
    # ========================================================

    peak_time = None

    if events:

        time_counts = {}

        for event in events:

            event_time = event["time"]

            time_counts[event_time] = (
                time_counts.get(event_time, 0) + 1
            )

        peak_time = max(
            time_counts,
            key=time_counts.get
        )

    # ========================================================
    # RESULT
    # ========================================================

    return {

        "station": "PUNE JUNCTION",

        "current_time": current_time,

        "window_minutes": window_minutes,

        "unique_trains": unique_trains,

        "arrival_events": len(arrivals),

        "departure_events": len(departures),

        "total_events": total_events,

        "activity_level": activity_level,

        "next_event": next_event,

        "peak_activity_time": peak_time,

        "events": events,

        "arrivals": arrivals,

        "departures": departures
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("RAILMIND AI - PUNE SCHEDULE INTELLIGENCE")
    print("=" * 65)

    # Test time
    current_time = "18:20:00"

    result = get_schedule_activity(
        current_time=current_time,
        window_minutes=30
    )

    print(f"\nStation: {result['station']}")
    print(f"Current Time: {result['current_time']}")
    print(f"Window: {result['window_minutes']} minutes")

    print("\n---------------- SUMMARY ----------------")

    print(
        f"Unique trains:     {result['unique_trains']}"
    )

    print(
        f"Arrival events:    {result['arrival_events']}"
    )

    print(
        f"Departure events:  {result['departure_events']}"
    )

    print(
        f"Total events:      {result['total_events']}"
    )

    print(
        f"Activity level:    {result['activity_level']}"
    )

    print("\n--------------- NEXT EVENT ---------------")

    if result["next_event"]:

        event = result["next_event"]

        print(
            f"{event['time']} | "
            f"{event['type']} | "
            f"{event['train_no']} | "
            f"{event['train_name']}"
        )

    else:

        print("No scheduled train event in this window.")

    print("\n------------ TRAIN TIMELINE --------------")

    for event in result["events"]:

        print(
            f"{event['time']} | "
            f"{event['type']:<9} | "
            f"{event['train_no']:<6} | "
            f"{event['train_name']}"
        )

    print("\n-------------------------------------------")
import cv2
import csv
from pathlib import Path
from collections import defaultdict
from statistics import median
from ultralytics import YOLO


# ============================================================
# RAILMIND AI - QUALITY-AWARE CROWD TIME-SERIES
# ============================================================

MODEL_PATH = Path(
    r"D:\RailMindAI\runs\detect\runs\RailMind\person_detector\weights\best.pt"
)

VIDEO_PATH = Path(
    r"D:\RailMindAI\Dataset\Pune_Junction\videos\1000321741.mp4"
)

OUTPUT_DIR = Path(
    r"D:\RailMindAI\data\crowd_timeseries"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_CSV = OUTPUT_DIR / "1000321741_crowd.csv"


# ============================================================
# SETTINGS
# ============================================================

CONFIDENCE = 0.25
IMG_SIZE = 640

# Minimum percentage of frames in a second
# that must contain detections for that second
# to be considered reliable.
MIN_COVERAGE = 0.50

# Maximum short gap that we are willing to interpolate.
MAX_INTERPOLATION_GAP = 3


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("RAILMIND AI - QUALITY-AWARE CROWD TIME-SERIES")
print("=" * 70)


# ============================================================
# GET REAL VIDEO FPS
# ============================================================

cap = cv2.VideoCapture(str(VIDEO_PATH))

if not cap.isOpened():
    raise RuntimeError(
        f"Could not open video:\n{VIDEO_PATH}"
    )

VIDEO_FPS = cap.get(cv2.CAP_PROP_FPS)

FRAME_COUNT = int(
    cap.get(cv2.CAP_PROP_FRAME_COUNT)
)

WIDTH = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

HEIGHT = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

cap.release()

if VIDEO_FPS <= 0:
    VIDEO_FPS = 30.0

DURATION = FRAME_COUNT / VIDEO_FPS


print(f"\nVideo:       {VIDEO_PATH.name}")
print(f"Resolution:  {WIDTH} x {HEIGHT}")
print(f"FPS:         {VIDEO_FPS:.2f}")
print(f"Frames:      {FRAME_COUNT}")
print(f"Duration:    {DURATION:.2f} seconds")


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading YOLO model...")

model = YOLO(str(MODEL_PATH))


# ============================================================
# RUN YOLO + BYTE TRACK
# ============================================================

print("\nRunning YOLO + ByteTrack...")
print("Processing every frame. Please wait...\n")

results = model.track(
    source=str(VIDEO_PATH),
    device=0,
    imgsz=IMG_SIZE,
    conf=CONFIDENCE,
    tracker="bytetrack.yaml",
    classes=[0],
    stream=True,
    verbose=False
)


# ============================================================
# COLLECT FRAME-LEVEL COUNTS
# ============================================================

second_counts = defaultdict(list)

frame_number = 0

for result in results:

    frame_number += 1

    timestamp = frame_number / VIDEO_FPS

    second = int(timestamp)

    count = 0

    # --------------------------------------------------------
    # Count tracked people
    # --------------------------------------------------------

    if (
        result.boxes is not None
        and result.boxes.id is not None
    ):

        count = len(result.boxes.id)

    second_counts[second].append(count)


# ============================================================
# CREATE SECOND-LEVEL DATA
# ============================================================

second_data = []

print("\n" + "=" * 70)
print("BUILDING 1-SECOND CROWD SIGNAL")
print("=" * 70)


for second in sorted(second_counts):

    values = second_counts[second]

    total_frames = len(values)

    positive_values = [
        value
        for value in values
        if value > 0
    ]

    positive_frames = len(
        positive_values
    )

    detection_coverage = (
        positive_frames / total_frames
        if total_frames > 0
        else 0
    )

    median_count = median(values)

    max_count = (
        max(values)
        if values
        else 0
    )

    # --------------------------------------------------------
    # QUALITY DECISION
    # --------------------------------------------------------

    if detection_coverage >= MIN_COVERAGE:

        # Ignore zero-detection frames when enough
        # positive frames exist.
        observed_crowd = int(
            round(
                median(positive_values)
            )
        )

        quality = "GOOD"

    else:

        observed_crowd = None

        quality = "LOW"


    second_data.append({

        "time_sec": second,

        "median_count": round(
            median_count,
            2
        ),

        "max_count": max_count,

        "positive_frames": positive_frames,

        "total_frames": total_frames,

        "detection_coverage": round(
            detection_coverage,
            3
        ),

        "observed_crowd": observed_crowd,

        "quality": quality,

        "crowd_change": None
    })


# ============================================================
# INTERPOLATE ONLY SHORT LOW-QUALITY GAPS
# ============================================================

for i in range(len(second_data)):

    row = second_data[i]

    if row["observed_crowd"] is not None:
        continue


    # --------------------------------------------------------
    # Find previous reliable observation
    # --------------------------------------------------------

    previous = None

    for j in range(
        i - 1,
        max(
            -1,
            i - MAX_INTERPOLATION_GAP - 1
        ),
        -1
    ):

        if (
            second_data[j][
                "observed_crowd"
            ]
            is not None
        ):

            previous = second_data[j]

            break


    # --------------------------------------------------------
    # Find next reliable observation
    # --------------------------------------------------------

    following = None

    for j in range(
        i + 1,
        min(
            len(second_data),
            i + MAX_INTERPOLATION_GAP + 1
        )
    ):

        if (
            second_data[j][
                "observed_crowd"
            ]
            is not None
        ):

            following = second_data[j]

            break


    # --------------------------------------------------------
    # Interpolate only when BOTH sides exist
    # --------------------------------------------------------

    if previous and following:

        gap = (
            following["time_sec"]
            -
            previous["time_sec"]
        )

        if gap <= (
            MAX_INTERPOLATION_GAP + 1
        ):

            position = (
                row["time_sec"]
                -
                previous["time_sec"]
            )

            start_value = (
                previous[
                    "observed_crowd"
                ]
            )

            end_value = (
                following[
                    "observed_crowd"
                ]
            )

            interpolated = (
                start_value
                +
                (
                    end_value
                    -
                    start_value
                )
                *
                position
                /
                gap
            )

            row[
                "observed_crowd"
            ] = int(
                round(
                    interpolated
                )
            )

            row[
                "quality"
            ] = "INTERPOLATED"


# ============================================================
# CALCULATE CROWD CHANGE
# ============================================================

previous_crowd = None

for row in second_data:

    current_crowd = (
        row["observed_crowd"]
    )

    if (
        current_crowd is not None
        and previous_crowd is not None
    ):

        row[
            "crowd_change"
        ] = (
            current_crowd
            -
            previous_crowd
        )

    else:

        row[
            "crowd_change"
        ] = None

    if current_crowd is not None:

        previous_crowd = (
            current_crowd
        )


# ============================================================
# SAVE CSV
# ============================================================

with open(
    OUTPUT_CSV,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(

        file,

        fieldnames=[

            "time_sec",

            "median_count",

            "max_count",

            "positive_frames",

            "total_frames",

            "detection_coverage",

            "observed_crowd",

            "quality",

            "crowd_change"
        ]
    )

    writer.writeheader()

    writer.writerows(
        second_data
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

valid_counts = [

    row["observed_crowd"]

    for row in second_data

    if row["observed_crowd"]
    is not None
]


good_count = sum(

    1

    for row in second_data

    if row["quality"] == "GOOD"
)


interpolated_count = sum(

    1

    for row in second_data

    if row["quality"]
    == "INTERPOLATED"
)


low_count = sum(

    1

    for row in second_data

    if row["quality"] == "LOW"
)


print("\n" + "=" * 70)
print("QUALITY-AWARE TIME-SERIES COMPLETE")
print("=" * 70)

print(
    f"Rows:                 "
    f"{len(second_data)}"
)

print(
    f"Good seconds:         "
    f"{good_count}"
)

print(
    f"Interpolated:         "
    f"{interpolated_count}"
)

print(
    f"Low-quality:          "
    f"{low_count}"
)


if valid_counts:

    print(
        f"Minimum observed:     "
        f"{min(valid_counts)}"
    )

    print(
        f"Maximum observed:     "
        f"{max(valid_counts)}"
    )

    print(
        f"Average observed:     "
        f"{sum(valid_counts) / len(valid_counts):.2f}"
    )


print("\nOutput CSV:")
print(OUTPUT_CSV)

print("\nDone.")
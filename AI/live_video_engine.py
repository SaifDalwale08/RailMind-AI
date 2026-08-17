import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from collections import deque
from ultralytics import YOLO

# ============================================================
# RAILMIND AI - LIVE VIDEO INTELLIGENCE ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# ============================================================
# MODEL
# ============================================================

MODEL_PATH = (
    PROJECT_DIR
    / "runs"
    / "RailMind"
    / "pune_person"
    / "weights"
    / "best.pt"
)

# ============================================================
# DEMO VIDEO
# ============================================================
# CHANGE ONLY THIS FILE NAME when testing another video.

VIDEO_PATH = (
    PROJECT_DIR
    / "Dataset"
    / "Pune_Junction"
    / "videos"
    / "1000321741.mp4"
)

# ============================================================
# SETTINGS
# ============================================================

CONFIDENCE = 0.35

WINDOW_SECONDS = 5

MAX_HISTORY = 10


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 75)
print("RAILMIND AI - LIVE VIDEO ENGINE")
print("=" * 75)

print("\nLoading trained YOLO model...")

model = YOLO(
    str(MODEL_PATH)
)

print("Model loaded:")
print(MODEL_PATH)


# ============================================================
# OPEN VIDEO
# ============================================================

cap = cv2.VideoCapture(
    str(VIDEO_PATH)
)

if not cap.isOpened():

    raise RuntimeError(
        f"Unable to open video:\n{VIDEO_PATH}"
    )


fps = cap.get(
    cv2.CAP_PROP_FPS
)

total_frames = int(
    cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )
)

duration = (
    total_frames / fps
    if fps > 0
    else 0
)

print("\nVideo:")
print(VIDEO_PATH)

print(
    f"FPS: {fps:.2f}"
)

print(
    f"Frames: {total_frames}"
)

print(
    f"Duration: {duration:.2f} seconds"
)


# ============================================================
# TIME-SERIES STORAGE
# ============================================================

second_counts = []

frame_counts = []

current_second = 0

frame_index = 0


# ============================================================
# PROCESS VIDEO
# ============================================================

print("\n" + "=" * 75)
print("PROCESSING VIDEO")
print("=" * 75)


while True:

    ret, frame = cap.read()

    if not ret:
        break


    # --------------------------------------------------------
    # YOLO detection
    # --------------------------------------------------------

    result = model.predict(
        frame,
        conf=CONFIDENCE,
        verbose=False
    )[0]


    # --------------------------------------------------------
    # Count detected persons
    # --------------------------------------------------------

    if result.boxes is not None:

        person_count = len(
            result.boxes
        )

    else:

        person_count = 0


    frame_counts.append(
        person_count
    )


    # --------------------------------------------------------
    # Check whether second changed
    # --------------------------------------------------------

    video_second = int(
        frame_index / fps
    )


    if video_second != current_second:

        if frame_counts:

            median_count = float(
                np.median(
                    frame_counts
                )
            )

            max_count = int(
                max(frame_counts)
            )

            second_counts.append({

                "time_sec":
                    current_second,

                "crowd":
                    median_count,

                "max_crowd":
                    max_count,

                "frames":
                    len(frame_counts)
            })


            print(
                f"{current_second:4d}s | "
                f"crowd={median_count:5.1f} | "
                f"max={max_count:3d} | "
                f"frames={len(frame_counts):3d}"
            )


        frame_counts = []

        current_second = video_second


    frame_index += 1


cap.release()


# ============================================================
# HANDLE FINAL SECOND
# ============================================================

if frame_counts:

    median_count = float(
        np.median(
            frame_counts
        )
    )

    max_count = int(
        max(frame_counts)
    )

    second_counts.append({

        "time_sec":
            current_second,

        "crowd":
            median_count,

        "max_crowd":
            max_count,

        "frames":
            len(frame_counts)
    })


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    second_counts
)


if df.empty:

    raise RuntimeError(
        "No crowd observations were generated."
    )


# ============================================================
# CALCULATE 5-SECOND FEATURES
# ============================================================

df["crowd_mean_5s"] = (
    df["crowd"]
    .rolling(
        WINDOW_SECONDS,
        min_periods=1
    )
    .mean()
)


df["crowd_change_5s"] = (
    df["crowd_mean_5s"]
    .diff(
        WINDOW_SECONDS
    )
)


df["growth_rate_5s"] = (
    df["crowd_change_5s"]
    / WINDOW_SECONDS
)


df["acceleration"] = (
    df["growth_rate_5s"]
    .diff()
)


# ============================================================
# TREND CLASSIFICATION
# ============================================================

def classify_trend(row):

    growth = row[
        "growth_rate_5s"
    ]

    if pd.isna(growth):

        return "UNKNOWN"

    if growth >= 1.0:

        return "RAPIDLY RISING"

    if growth >= 0.3:

        return "RISING"

    if growth <= -1.0:

        return "RAPIDLY FALLING"

    if growth <= -0.3:

        return "FALLING"

    return "STABLE"


df["trend"] = df.apply(
    classify_trend,
    axis=1
)


# ============================================================
# CROWD LEVEL
# ============================================================

def classify_crowd(crowd):

    if crowd >= 15:

        return "CRITICAL"

    if crowd >= 10:

        return "HIGH"

    if crowd >= 5:

        return "MEDIUM"

    return "LOW"


df["crowd_level"] = (
    df["crowd"]
    .apply(
        classify_crowd
    )
)


# ============================================================
# SAVE LIVE CROWD SIGNAL
# ============================================================

OUTPUT_DIR = (
    PROJECT_DIR
    / "data"
    / "live"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR
    / "live_crowd_signal.csv"
)


df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 75)
print("LIVE VIDEO PROCESSING COMPLETE")
print("=" * 75)

print(
    f"Seconds processed: {len(df)}"
)

print(
    f"Minimum crowd: "
    f"{df['crowd'].min():.0f}"
)

print(
    f"Maximum crowd: "
    f"{df['crowd'].max():.0f}"
)

print(
    f"Average crowd: "
    f"{df['crowd'].mean():.2f}"
)

print(
    f"\nSaved:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# SHOW LAST OBSERVATIONS
# ============================================================

print("\n" + "-" * 75)
print("LATEST CROWD SIGNAL")
print("-" * 75)

print(
    df.tail(10).to_string(
        index=False
    )
)

print("\n" + "=" * 75)
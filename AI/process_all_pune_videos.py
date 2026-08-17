import cv2
import csv
from pathlib import Path
from collections import defaultdict
from statistics import median
from ultralytics import YOLO


# ============================================================
# RAILMIND AI - BATCH PUNE VIDEO PROCESSOR
# ============================================================

MODEL_PATH = Path(
    r"D:\RailMindAI\runs\RailMind\pune_person\weights\best.pt"
)

VIDEO_DIR = Path(
    r"D:\RailMindAI\Dataset\Pune_Junction\videos"
)

OUTPUT_DIR = Path(
    r"D:\RailMindAI\data\crowd_timeseries_pune_model"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SETTINGS
# ============================================================

CONFIDENCE = 0.25
IMG_SIZE = 640

MIN_COVERAGE = 0.50

MAX_INTERPOLATION_GAP = 3


# ============================================================
# HEADER
# ============================================================

print("=" * 75)
print("RAILMIND AI - PUNE JUNCTION BATCH CROWD PROCESSOR")
print("=" * 75)


# ============================================================
# FIND VIDEOS
# ============================================================

videos = sorted(
    VIDEO_DIR.glob("*.mp4")
)

print(f"\nVideos found: {len(videos)}")

if not videos:

    raise RuntimeError(
        f"No MP4 videos found in:\n{VIDEO_DIR}"
    )


# ============================================================
# LOAD MODEL ONCE
# ============================================================

print("\nLoading YOLO model...")

model = YOLO(
    str(MODEL_PATH)
)

print("Model loaded.")


# ============================================================
# PROCESS EACH VIDEO
# ============================================================

all_rows = []

summary_rows = []


for video_index, video_path in enumerate(
    videos,
    start=1
):

    print("\n")
    print("=" * 75)

    print(
        f"[{video_index}/{len(videos)}] "
        f"{video_path.name}"
    )

    print("=" * 75)


    # --------------------------------------------------------
    # VIDEO INFORMATION
    # --------------------------------------------------------

    cap = cv2.VideoCapture(
        str(video_path)
    )

    if not cap.isOpened():

        print(
            "WARNING: Could not open video. Skipping."
        )

        continue


    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    frame_count = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    cap.release()


    if fps <= 0:

        fps = 30.0


    duration = (
        frame_count / fps
    )


    print(
        f"Resolution: {width}x{height}"
    )

    print(
        f"FPS: {fps:.2f}"
    )

    print(
        f"Duration: {duration:.2f}s"
    )


    # --------------------------------------------------------
    # TRACK VIDEO
    # --------------------------------------------------------

    second_counts = defaultdict(list)

    frame_number = 0


    print(
        "Running YOLO + ByteTrack..."
    )


    results = model.track(

        source=str(video_path),

        device=0,

        imgsz=IMG_SIZE,

        conf=CONFIDENCE,

        tracker="bytetrack.yaml",

        classes=[0],

        stream=True,

        verbose=False
    )


    for result in results:

        frame_number += 1

        timestamp = (
            frame_number / fps
        )

        second = int(
            timestamp
        )


        count = 0


        if (
            result.boxes is not None
            and result.boxes.id is not None
        ):

            count = len(
                result.boxes.id
            )


        second_counts[
            second
        ].append(
            count
        )


    # --------------------------------------------------------
    # SECOND LEVEL DATA
    # --------------------------------------------------------

    second_data = []


    for second in sorted(
        second_counts
    ):

        values = (
            second_counts[
                second
            ]
        )


        total_frames = len(
            values
        )


        positive_values = [

            value

            for value in values

            if value > 0
        ]


        positive_frames = len(
            positive_values
        )


        coverage = (

            positive_frames
            /
            total_frames

            if total_frames > 0
            else 0
        )


        median_count = median(
            values
        )


        max_count = max(
            values
        )


        # ----------------------------------------------------
        # QUALITY DECISION
        # ----------------------------------------------------

        if coverage >= MIN_COVERAGE:

            observed = int(
                round(
                    median(
                        positive_values
                    )
                )
            )

            quality = "GOOD"

        else:

            observed = None

            quality = "LOW"


        second_data.append({

            "time_sec":
                second,

            "median_count":
                round(
                    median_count,
                    2
                ),

            "max_count":
                max_count,

            "positive_frames":
                positive_frames,

            "total_frames":
                total_frames,

            "detection_coverage":
                round(
                    coverage,
                    3
                ),

            "observed_crowd":
                observed,

            "quality":
                quality,

            "crowd_change":
                None
        })


    # --------------------------------------------------------
    # INTERPOLATE SHORT GAPS
    # --------------------------------------------------------

    for i in range(
        len(second_data)
    ):

        row = second_data[i]


        if row[
            "observed_crowd"
        ] is not None:

            continue


        previous = None


        for j in range(

            i - 1,

            max(
                -1,
                i
                -
                MAX_INTERPOLATION_GAP
                -
                1
            ),

            -1

        ):

            if (
                second_data[j][
                    "observed_crowd"
                ]
                is not None
            ):

                previous = (
                    second_data[j]
                )

                break


        following = None


        for j in range(

            i + 1,

            min(
                len(second_data),

                i
                +
                MAX_INTERPOLATION_GAP
                +
                1
            )
        ):

            if (
                second_data[j][
                    "observed_crowd"
                ]
                is not None
            ):

                following = (
                    second_data[j]
                )

                break


        if previous and following:

            gap = (

                following[
                    "time_sec"
                ]
                -
                previous[
                    "time_sec"
                ]
            )


            if gap <= (
                MAX_INTERPOLATION_GAP
                +
                1
            ):

                position = (

                    row[
                        "time_sec"
                    ]
                    -
                    previous[
                        "time_sec"
                    ]
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


    # --------------------------------------------------------
    # CROWD CHANGE
    # --------------------------------------------------------

    previous_crowd = None


    for row in second_data:

        current = (
            row[
                "observed_crowd"
            ]
        )


        if (
            current is not None
            and previous_crowd is not None
        ):

            row[
                "crowd_change"
            ] = (

                current
                -
                previous_crowd
            )


        if current is not None:

            previous_crowd = current


    # --------------------------------------------------------
    # ADD VIDEO ID
    # --------------------------------------------------------

    for row in second_data:

        row[
            "video_id"
        ] = video_path.stem


    # --------------------------------------------------------
    # SAVE INDIVIDUAL CSV
    # --------------------------------------------------------

    output_csv = (
        OUTPUT_DIR
        /
        f"{video_path.stem}_crowd.csv"
    )


    with open(

        output_csv,

        "w",

        newline="",

        encoding="utf-8"

    ) as file:

        writer = csv.DictWriter(

            file,

            fieldnames=[

                "video_id",

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


    # --------------------------------------------------------
    # ADD TO COMBINED DATA
    # --------------------------------------------------------

    all_rows.extend(
        second_data
    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    valid = [

        row[
            "observed_crowd"
        ]

        for row in second_data

        if row[
            "observed_crowd"
        ] is not None
    ]


    good = sum(

        1

        for row in second_data

        if row[
            "quality"
        ] == "GOOD"
    )


    interpolated = sum(

        1

        for row in second_data

        if row[
            "quality"
        ] == "INTERPOLATED"
    )


    low = sum(

        1

        for row in second_data

        if row[
            "quality"
        ] == "LOW"
    )


    summary_rows.append({

        "video_id":
            video_path.stem,

        "duration_sec":
            round(
                duration,
                2
            ),

        "rows":
            len(second_data),

        "good_seconds":
            good,

        "interpolated_seconds":
            interpolated,

        "low_seconds":
            low,

        "min_crowd":
            min(valid)
            if valid
            else None,

        "max_crowd":
            max(valid)
            if valid
            else None,

        "average_crowd":
            round(
                sum(valid)
                /
                len(valid),
                2
            )
            if valid
            else None
    })


    print(
        f"Rows: {len(second_data)}"
    )

    print(
        f"Good: {good}"
    )

    print(
        f"Interpolated: {interpolated}"
    )

    print(
        f"Low: {low}"
    )


# ============================================================
# SAVE COMBINED DATASET
# ============================================================

combined_csv = (
    OUTPUT_DIR
    /
    "combined_pune_crowd_dataset.csv"
)


fieldnames = [

    "video_id",

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


with open(

    combined_csv,

    "w",

    newline="",

    encoding="utf-8"

) as file:

    writer = csv.DictWriter(

        file,

        fieldnames=fieldnames
    )


    writer.writeheader()

    writer.writerows(
        all_rows
    )


# ============================================================
# SAVE VIDEO SUMMARY
# ============================================================

summary_csv = (
    OUTPUT_DIR
    /
    "pune_video_summary.csv"
)


summary_fields = [

    "video_id",

    "duration_sec",

    "rows",

    "good_seconds",

    "interpolated_seconds",

    "low_seconds",

    "min_crowd",

    "max_crowd",

    "average_crowd"
]


with open(

    summary_csv,

    "w",

    newline="",

    encoding="utf-8"

) as file:

    writer = csv.DictWriter(

        file,

        fieldnames=summary_fields
    )


    writer.writeheader()

    writer.writerows(
        summary_rows
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

all_valid = [

    row[
        "observed_crowd"
    ]

    for row in all_rows

    if row[
        "observed_crowd"
    ] is not None
]


total_good = sum(

    1

    for row in all_rows

    if row[
        "quality"
    ] == "GOOD"
)


total_interpolated = sum(

    1

    for row in all_rows

    if row[
        "quality"
    ] == "INTERPOLATED"
)


total_low = sum(

    1

    for row in all_rows

    if row[
        "quality"
    ] == "LOW"
)


print("\n")
print("=" * 75)
print("RAILMIND - BATCH PROCESSING COMPLETE")
print("=" * 75)

print(
    f"Videos processed:       "
    f"{len(summary_rows)}"
)

print(
    f"Total time-series rows:  "
    f"{len(all_rows)}"
)

print(
    f"Good observations:      "
    f"{total_good}"
)

print(
    f"Interpolated:           "
    f"{total_interpolated}"
)

print(
    f"Low-quality:            "
    f"{total_low}"
)


if all_valid:

    print(
        f"Minimum crowd:          "
        f"{min(all_valid)}"
    )

    print(
        f"Maximum crowd:          "
        f"{max(all_valid)}"
    )

    print(
        f"Average crowd:          "
        f"{sum(all_valid) / len(all_valid):.2f}"
    )


print("\nIndividual CSVs:")
print(OUTPUT_DIR)

print("\nCombined dataset:")
print(combined_csv)

print("\nVideo summary:")
print(summary_csv)

print("\nDONE.")
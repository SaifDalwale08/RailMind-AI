from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "Dataset"
OUTPUT = DATASET / "RailMind_Person"

SOURCES = {
    "crowd": DATASET / "crowd-tracking-counting.v2i.yolov11",
    "railway": DATASET / "Indian Railway.v2i.yolov11",
}

# Recreate output safely
if OUTPUT.exists():
    shutil.rmtree(OUTPUT)

for split in ["train", "valid", "test"]:
    (OUTPUT / split / "images").mkdir(parents=True, exist_ok=True)
    (OUTPUT / split / "labels").mkdir(parents=True, exist_ok=True)


def process_dataset(source, split, prefix, keep_classes):
    image_dir = source / split / "images"
    label_dir = source / split / "labels"

    if not image_dir.exists() or not label_dir.exists():
        print(f"[SKIP] {source.name} -> {split} not found")
        return 0

    count = 0

    for image in image_dir.iterdir():
        if not image.is_file():
            continue

        label = label_dir / f"{image.stem}.txt"

        if not label.exists():
            continue

        new_lines = []

        for line in label.read_text().splitlines():
            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])

            # Keep only the requested person class
            if class_id in keep_classes:
                # Normalize every kept person class to class 0
                parts[0] = "0"
                new_lines.append(" ".join(parts))

        # Don't copy images containing no person annotation
        if not new_lines:
            continue

        new_name = f"{prefix}_{image.name}"
        new_label_name = f"{prefix}_{image.stem}.txt"

        shutil.copy2(
            image,
            OUTPUT / split / "images" / new_name
        )

        (OUTPUT / split / "labels" / new_label_name).write_text(
            "\n".join(new_lines) + "\n"
        )

        count += 1

    print(f"[OK] {source.name} | {split}: {count} images")
    return count


# Crowd Tracking & Counting
# Class 0 = people
for split in ["train", "valid", "test"]:
    process_dataset(
        SOURCES["crowd"],
        split,
        "crowd",
        {0}
    )

# Indian Railway
# Class 0 = People
# Class 1 = Train
# Class 2 = Train_Side_View
#
# We intentionally keep ONLY class 0.
for split in ["train", "valid", "test"]:
    process_dataset(
        SOURCES["railway"],
        split,
        "railway",
        {0}
    )


# Create YOLO dataset configuration
yaml_content = f"""path: {OUTPUT.as_posix()}
train: train/images
val: valid/images
test: test/images

nc: 1
names:
  0: person
"""

(OUTPUT / "data.yaml").write_text(yaml_content)

print("\n========================================")
print("RailMind person dataset created!")
print(f"Location: {OUTPUT}")
print("Class: person")
print("========================================")
import random
import shutil
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

SOURCE_IMAGES = Path(
    r"D:\RailMindAI\Dataset\Pune_Junction\images"
)

SOURCE_LABELS = Path(
    r"D:\RailMindAI\runs\detect\runs\RailMind\pune_annotation_clean\labels"
)

OUTPUT = Path(
    r"D:\RailMindAI\Dataset\Pune_YOLO"
)

TRAIN_RATIO = 0.80

SEED = 42


# ============================================================
# CREATE DIRECTORIES
# ============================================================

train_images = OUTPUT / "images" / "train"
val_images = OUTPUT / "images" / "val"

train_labels = OUTPUT / "labels" / "train"
val_labels = OUTPUT / "labels" / "val"

for folder in [
    train_images,
    val_images,
    train_labels,
    val_labels
]:
    folder.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# FIND MATCHING IMAGE-LABEL PAIRS
# ============================================================

image_extensions = {
    ".jpg",
    ".jpeg",
    ".png"
}

pairs = []

for label_path in SOURCE_LABELS.glob("*.txt"):

    stem = label_path.stem

    image_path = None

    for ext in image_extensions:

        candidate = (
            SOURCE_IMAGES
            /
            f"{stem}{ext}"
        )

        if candidate.exists():

            image_path = candidate

            break

    if image_path:

        pairs.append(
            (
                image_path,
                label_path
            )
        )


print("=" * 65)
print("RAILMIND - PUNE YOLO DATASET PREPARATION")
print("=" * 65)

print(
    f"\nMatched pairs: {len(pairs)}"
)


# ============================================================
# SHUFFLE
# ============================================================

random.seed(SEED)

random.shuffle(
    pairs
)


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

split_index = int(
    len(pairs) * TRAIN_RATIO
)

train_pairs = pairs[:split_index]

val_pairs = pairs[split_index:]


print(
    f"Training images:   {len(train_pairs)}"
)

print(
    f"Validation images: {len(val_pairs)}"
)


# ============================================================
# COPY FILES
# ============================================================

for image_path, label_path in train_pairs:

    shutil.copy2(
        image_path,
        train_images / image_path.name
    )

    shutil.copy2(
        label_path,
        train_labels / label_path.name
    )


for image_path, label_path in val_pairs:

    shutil.copy2(
        image_path,
        val_images / image_path.name
    )

    shutil.copy2(
        label_path,
        val_labels / label_path.name
    )


# ============================================================
# SUMMARY
# ============================================================

print("\nDataset created successfully.")

print(
    f"\nTrain images: "
    f"{len(list(train_images.iterdir()))}"
)

print(
    f"Train labels: "
    f"{len(list(train_labels.iterdir()))}"
)

print(
    f"Validation images: "
    f"{len(list(val_images.iterdir()))}"
)

print(
    f"Validation labels: "
    f"{len(list(val_labels.iterdir()))}"
)

print("\nLocation:")
print(OUTPUT)
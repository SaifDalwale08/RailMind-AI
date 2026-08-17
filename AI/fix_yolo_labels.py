import os

ROOTS = [
    r"D:\RailMindAI\Dataset\Pune_YOLO\labels\train",
    r"D:\RailMindAI\Dataset\Pune_YOLO\labels\val",
]

total_files = 0
fixed_files = 0
five_col_files = 0
six_col_files = 0
invalid_files = 0
total_boxes = 0

print("=" * 65)
print("RAILMIND - FIXING YOLO LABEL FORMAT")
print("=" * 65)

for root in ROOTS:
    for filename in os.listdir(root):

        if not filename.endswith(".txt"):
            continue

        path = os.path.join(root, filename)
        total_files += 1

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        changed = False

        for line in lines:
            parts = line.strip().split()

            if not parts:
                continue

            if len(parts) == 6:
                # Remove confidence column
                parts = parts[:5]
                changed = True
                six_col_files += 1

            if len(parts) == 5:
                five_col_files += 1
                total_boxes += 1
                new_lines.append(" ".join(parts))
            else:
                invalid_files += 1
                print("INVALID:", path, "->", len(parts), "columns")

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")

            fixed_files += 1

print()
print("=" * 65)
print("LABEL FIX COMPLETE")
print("=" * 65)

print("Label files:", total_files)
print("Files fixed:", fixed_files)
print("6-column labels found:", six_col_files)
print("Valid 5-column boxes:", total_boxes)
print("Invalid lines:", invalid_files)
from ultralytics import YOLO

# Load YOLO11
model = YOLO("yolo11n.pt")

# Run detection on a sample image
results = model.predict(
    source="https://ultralytics.com/images/bus.jpg",
    conf=0.4,
    save=True
)

print("Detection completed!")
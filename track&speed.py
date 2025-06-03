import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque

# Load YOLO model
model = YOLO("CBDbest.pt")

# Input and Output paths
video_path = "Dataset/03.mkv"
output_path = "output.avi"

# === Calibration ===
# Real pitch length in meters (between creases): 20.12m
# Pixel distance between creases (measured manually from calibration script)
pixel_distance = 1052.75  # <--- UPDATE this if your calibration changes
meters_per_pixel = 20.12 / pixel_distance

# Setup video capture and writer
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error opening video")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Variables for tracking
prev_center = None
trajectory = deque(maxlen=50)
last_speed_kmph = None
speed_log = []  #  To store all valid speeds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.25)
    center = None

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            center = (center_x, center_y)

            # Draw box and center
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

    if center and prev_center:
        dx = center[0] - prev_center[0]
        dy = center[1] - prev_center[1]
        pixel_dist = np.sqrt(dx**2 + dy**2)
        meters = pixel_dist * meters_per_pixel
        time_sec = 1 / fps
        speed_kmph = (meters / time_sec) * 3.6

        if speed_kmph < 200:  # realistic limit
            last_speed_kmph = speed_kmph
            speed_log.append(speed_kmph)  # Store speed
            print(f"Speed: {speed_kmph:.2f} km/h")
            cv2.putText(frame, f"Speed: {speed_kmph:.2f} km/h", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    if center:
        prev_center = center
        trajectory.append(center)

    for i in range(1, len(trajectory)):
        if trajectory[i - 1] and trajectory[i]:
            cv2.line(frame, trajectory[i - 1], trajectory[i], (0, 255, 255), 2)

    cv2.imshow("Ball Tracking", frame)
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Final speed frame
final_frame = np.zeros((height, width, 3), dtype=np.uint8)

if last_speed_kmph:
    msg = f"Final Ball Speed: {last_speed_kmph:.2f} km/h"
else:
    msg = "Ball Speed Not Detected"

cv2.putText(final_frame, msg, (60, height // 2), cv2.FONT_HERSHEY_SIMPLEX,
            1.5, (0, 255, 0), 3)

# Show final message frame for 3 seconds
for _ in range(int(fps * 3)):
    out.write(final_frame)
    cv2.imshow("Ball Tracking", final_frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

#  Print all tracked speeds after video ends
print("\n All Tracked Speeds (km/h):")
for i, s in enumerate(speed_log, start=1):
    print(f"Frame {i}: {s:.2f} km/h")

print(" Final speed shown in last frame of output.avi")

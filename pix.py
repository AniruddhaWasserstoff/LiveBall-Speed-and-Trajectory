import cv2
import math

# ---------- SETTINGS ----------
video_path = 'Dataset/03.mkv'  # Path to your video
frame_number = 100     # Frame to extract
frame_save_path = 'calibration_frame.jpg'

# ---------- EXTRACT AND SAVE FRAME ----------
cap = cv2.VideoCapture(video_path)
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Error: Could not read frame")
    exit()

cv2.imwrite(frame_save_path, frame)
print(f"Frame saved as {frame_save_path}")

# ---------- MEASURE DISTANCE ----------
points = []

def click_event(event, x, y, flags, param):
    global points, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Select Two Points", frame)

        if len(points) == 2:
            # Draw a line between the two points
            cv2.line(frame, points[0], points[1], (255, 0, 0), 2)
            dist = math.dist(points[0], points[1])
            print(f"Distance between points: {dist:.2f} pixels")
            cv2.putText(frame, f"{dist:.2f}px", (points[1][0]+10, points[1][1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.imshow("Select Two Points", frame)

# ---------- DISPLAY AND CLICK ----------
cv2.imshow("Select Two Points", frame)
cv2.setMouseCallback("Select Two Points", click_event)

print("Click two points on the image to measure pixel distance.")
cv2.waitKey(0)
cv2.destroyAllWindows()

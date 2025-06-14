from collections import deque
from ultralytics import YOLO
import math
import time
import cv2
import os

def angle_between_lines(m1, m2=1):
    if m1 != -1 / m2:
        angle = math.degrees(math.atan(abs((m2 - m1) / (1 + m1 * m2))))
        return angle
    else:
        return 90.0

class FixedSizeQueue:
    def __init__(self, max_size):
        self.queue = deque(maxlen=max_size)
    
    def add(self, item):
        self.queue.append(item)
    
    def pop(self):
        self.queue.popleft()
        
    def clear(self):
        self.queue.clear()

    def get_queue(self):
        return self.queue
    
    def __len__(self):
        return len(self.queue)

# 🔽 Load your custom YOLOv8 model
model = YOLO("CBDbest.pt")  # Make sure this file is in the current directory

# 🔽 Load input video
video_path = os.path.join('Dataset', '03.mp4')  # Change path if needed
cap = cv2.VideoCapture(video_path)

# 🔽 Set up output video writer
output_dir = 'Output'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'predicted_trajectory.mp4')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps_output = int(cap.get(cv2.CAP_PROP_FPS)) or 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(output_path, fourcc, fps_output, (width, height))

# 🔽 Initialize tracking variables
ret = True
centroid_history = FixedSizeQueue(10)
start_time = time.time()
interval = 0.6
paused = False
angle = 0
prev_frame_time = 0 
new_frame_time = 0

# 🔽 Start processing
while ret:
    ret, frame = cap.read()
    if not ret:
        break

    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time + 1e-6)
    prev_frame_time = new_frame_time

    current_time = time.time()
    if current_time - start_time >= interval and len(centroid_history) > 0:
        centroid_history.pop()
        start_time = current_time

    results = model.track(frame, persist=True, conf=0.35, verbose=False)
    boxes = results[0].boxes
    box = boxes.xyxy

    if len(box) != 0:
        for i in range(box.shape[0]):
            x1, y1, x2, y2 = box[i]
            x1, y1, x2, y2 = x1.item(), y1.item(), x2.item(), y2.item()

            centroid_x = int((x1 + x2) / 2)
            centroid_y = int((y1 + y2) / 2)

            centroid_history.add((centroid_x, centroid_y))
            cv2.circle(frame, (centroid_x, centroid_y), radius=3, color=(0, 0, 255), thickness=-1)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

    if len(centroid_history) > 1:
        centroid_list = list(centroid_history.get_queue())
        for i in range(1, len(centroid_list)):
            cv2.line(frame, centroid_list[i - 1], centroid_list[i], (255, 0, 0), 4)

        # 🔽 Direction and future prediction
        x_diff = centroid_list[-1][0] - centroid_list[-2][0]
        y_diff = centroid_list[-1][1] - centroid_list[-2][1]

        if x_diff != 0:
            m1 = y_diff / x_diff
            if m1 == 1:
                angle = 90
            elif m1 != 0:
                angle = 90 - angle_between_lines(m1)

            if angle >= 45:
                print("Ball bounced")

        # 🔽 Predict future positions
        future_positions = [centroid_list[-1]]
        for i in range(1, 5):
            future_positions.append((
                centroid_list[-1][0] + x_diff * i,
                centroid_list[-1][1] + y_diff * i
            ))
        print("Future Positions:", future_positions)

        for i in range(1, len(future_positions)):
            cv2.line(frame, future_positions[i - 1], future_positions[i], (0, 255, 0), 4)
            cv2.circle(frame, future_positions[i], radius=3, color=(0, 0, 255), thickness=-1)

    # 🔽 Display angle and FPS
    text = "Angle: {:.2f} degrees".format(angle)
    cv2.putText(frame, text, (20, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # 🔽 Show and save output
    frame_resized = cv2.resize(frame, (1000, 600))
    cv2.imshow('frame', frame_resized)
    out.write(frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord(' '):
        paused = not paused
        while paused:
            key = cv2.waitKey(30) & 0xFF
            if key == ord(' '):
                paused = False
            elif key == ord('q'):
                ret = False
                break

cap.release()
out.release()
cv2.destroyAllWindows()

# LiveBall-Speed-and-Trajectory 

LiveBall Speed and Trajectory is a computer vision-based projetect a cricket ball in a video, track its motion, and estimate its speed and trajectory using real-world calibration.

![image](https://github.com/user-attachments/assets/1918670a-75f5-4daf-aacd-2c758bea8902)


![image](https://github.com/user-attachments/assets/d1fbed66-ceb4-4ff3-ba7a-ad613168690b)


# Model
This project uses a custom-trained YOLOv8 model (CBDbest.pt) trained specifically on cricket ball data from this repo:

 https://github.com/HarshSingh18/CV_Project/tree/main


# Requirements
Install all dependencies from requirements.txt:

```
pip install -r requirements.txt
```
# Features
1.Detects a cricket ball in each frame using YOLOv8
<br>
2.Tracks the ball’s motion over time
<br>
3.Calculates ball speed using pixel-to-meter calibration
<br>
4.Draws the trajectory and bounding boxes in real-time
<br>
5.Overlays the final speed on the last frame
<br>
6.Outputs a new video (output.avi) with full annotations
<br>
7.Logs all frame-wise ball speeds to the terminal


# Folder structure

![image](https://github.com/user-attachments/assets/292a5ac6-777a-4150-9753-7ec3d4444258)


# 1. Pixel Calibration
   
Use pix.py to manually select two points (typically the crease lines on a cricket pitch) and compute the pixel distance corresponding to the real-world pitch length (20.12 meters).
```
python pix.py
```

This gives you a scale:
meters_per_pixel = 20.12 / pixel_distance

# 2. Ball Tracking & Speed Estimation
Run the main script on your input video. It uses the YOLO model (CBDbest.pt) to detect the ball, track its path, and compute its speed.
```
python track\&speed.py
```
This will:

1.Detect the cricket ball in each frame.
<br>
2.Draw its trajectory.
<br>
3.Estimate the speed using frame-to-frame movement.
<br>
4.Save the annotated video as output.avi inside the root directory.
<br>
5.Show final ball speed in a black frame for 3 seconds at the end of the video.
<br>
6.Print all tracked speeds in the terminal.
<br>


![image](https://github.com/user-attachments/assets/9020dce3-7639-4b90-8095-a07374970847)


![image](https://github.com/user-attachments/assets/97e9338a-b35d-4715-b2ec-8fab3ebd6b22)


# Output
Annotated Video: Trajectory path and bounding boxes around the ball.
<br>
Speed Overlay: Real-time speed display on each frame.
<br>
Final Speed Summary: Displayed at the end of video and logged in terminal.
<br>


# Notes
The system assumes the ball is visible for at least a few consecutive frames.
<br>
Speeds >200 km/h are filtered as noise.
<br>
Output video is always saved in .avi format regardless of input format (.mp4, .mkv, etc.).
<br>
















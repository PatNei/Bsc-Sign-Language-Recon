import cv2 as cv
from typing import Any
from mediapipe.python.solutions import drawing_utils as mp_drawing, drawing_styles as mp_drawing_styles, holistic as mp_holi
import argparse

import time

parser = argparse.ArgumentParser()
parser.add_argument("filename", default="video.avi", help="It's the filename to process")
args = parser.parse_args()

target = args.filename
print(f"Looking at file {target}")

# For webcam input:
cap = cv.VideoCapture(target)
#writer = cv.VideoWriter("output.avi", -1, 20.0, (640, 480))

pose = mp_holi.Holistic(
  min_detection_confidence=0.5,
  min_tracking_confidence=0.5)

while cap.isOpened():
  ret, frame = cap.read()
 
  # if frame is read correctly ret is True
  if not ret:
    print("Hol up, cv failed to capture stuff - EXITING")
    break
  if cv.waitKey(1) == ord('q'):
    break
  
  frame.flags.writeable = False
  img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
  results: Any = pose.process(img)

  mp_drawing.draw_landmarks(
    img,
    results.pose_landmarks,
    mp_holi.POSE_CONNECTIONS, # type: ignore
    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
  mp_drawing.draw_landmarks(
    img,
    results.right_hand_landmarks,
    mp_holi.HAND_CONNECTIONS, # type: ignore
    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
  mp_drawing.draw_landmarks(
    img,
    results.left_hand_landmarks,
    mp_holi.HAND_CONNECTIONS, # type: ignore
    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
  #writer.write(img)
  cv.imshow('frame', img)
  time.sleep(0.1)
cap.release()
cv.destroyAllWindows()
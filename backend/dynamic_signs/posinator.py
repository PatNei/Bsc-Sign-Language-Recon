#Simple python script to paint MediaPipe landmarks onto an img.
import cv2 as cv
from pathlib import Path
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("filename", help="img to process through mp")
parser.add_argument("out_name", help="the ouput", default="out.jpg")
args = parser.parse_args()

target = args.filename
if not Path(target).exists():
    print(f"ERROR: File {target} does not exist")
    exit(1)
print(f"Looking at file {target}")

from mediapipe.python.solutions import drawing_utils as mp_drawing, drawing_styles as mp_drawing_styles, hands as mp_hands
num_hands = 1
use_static_image_mode = True
min_detection_confidence = 0.7
min_tracking_confidence = 0.5
hands  = mp_hands.Hands(
    static_image_mode=use_static_image_mode,
    max_num_hands=num_hands,
    min_detection_confidence=min_detection_confidence, 
    min_tracking_confidence=min_tracking_confidence,
)


img = cv.cvtColor(cv.imread(target), cv.COLOR_BGR2RGB)
res = hands.process(img)
img.flags.writeable = True

multi_hand_landmarks = "multi_hand_landmarks"
if hasattr(res, multi_hand_landmarks) and getattr(res, multi_hand_landmarks):
      for hand_landmarks in getattr(res, multi_hand_landmarks):
        mp_drawing.draw_landmarks(
            img,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS, #type: ignore
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
      img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
      cv.imwrite(args.out_name, img)
      print(f"SUCCESS: output to {args.out_name}")
else:
      print(f"ERROR: Found no hands - {multi_hand_landmarks} is empty")
      exit(1)


# from mediapipe.python.solutions import drawing_utils as mp_drawing, drawing_styles as mp_drawing_styles, holistic as mp_holi
# # For webcam input:
# cap = cv.VideoCapture(target)
# #writer = cv.VideoWriter("output.avi", -1, 20.0, (640, 480))

# while cap.isOpened():
#   ret, frame = cap.read()
 
#   # if frame is read correctly ret is True
#   if not ret:
#     print("Hol up, cv failed to capture stuff - EXITING")
#     break
#   if cv.waitKey(1) == ord('q'):
#     break
  
#   frame.flags.writeable = False
#   img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#   results: Any = pose.process(img)

#   mp_drawing.draw_landmarks(
#     img,
#     results.pose_landmarks,
#     mp_holi.POSE_CONNECTIONS, # type: ignore
#     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
#   mp_drawing.draw_landmarks(
#     img,
#     results.right_hand_landmarks,
#     mp_holi.HAND_CONNECTIONS, # type: ignore
#     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
#   mp_drawing.draw_landmarks(
#     img,
#     results.left_hand_landmarks,
#     mp_holi.HAND_CONNECTIONS, # type: ignore
#     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
#   #writer.write(img)
#   cv.imshow('frame', img)
#   time.sleep(0.1)
# cap.release()
# cv.destroyAllWindows()
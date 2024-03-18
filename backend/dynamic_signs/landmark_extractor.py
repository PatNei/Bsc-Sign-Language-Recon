import csv
import os
from pathlib import Path
import re
from zipfile import ZipFile
import cv2
import numpy as np
import numpy.typing as npt
from sign.training.landmark_extraction.MediaPiper import MediaPiper
import shutil

LandmarksCSV = list[npt.NDArray[np.float32]]

def process_video_frames(letter: str, id: str):
    try:
        vc = cv2.VideoCapture('video.avi')
        i = 0
        if vc.isOpened():
            rval , frame = vc.read()
        else:
            rval = False
            
        path = f"./dynamic_signs/frames/{letter}"
        if not os.path.exists(path):
            os.makedirs(path)
            
        while rval:
            rval, frame = vc.read()
            if frame is None or frame.size == 0:
                continue
            cv2.imwrite(f"{path}/{id}_{i}.png", frame)
            i = i + 1
        vc.release()
        res = mediapiper.process_dynamic_gestures_from_folder("./dynamic_signs/frames/")
    finally:
        with open("out.csv", 'a', newline="") as f:
            for dynamic_gesture in res:
                writer = csv.writer(f)
                for gesture_sequence in dynamic_gesture.results:
                    for landmarks in gesture_sequence:
                        x = landmarks.multi_hand_landmarks
                        if x is not None:
                            writer.writerow([dynamic_gesture.label, *[[landmark.x, landmark.y, landmark.z] for landmark in x], len(landmarks.multi_handedness if landmarks.multi_handedness is not None else [])])
        shutil.rmtree(path)
    
    
regex = r".*\/*(.+)\/(.+)\.avi"
mediapiper = MediaPiper()
with ZipFile(str(Path.cwd().absolute().joinpath("videos.zip")), 'r') as myzip:
    try:
        for file in myzip.filelist:
            match = re.match(regex, file.filename)
            if match is not None:
                letter = match.group(1)
                id = match.group(2)
                video = myzip.open(file.filename).read()
                with open("video.avi", "wb") as video_file:
                    video_file.write(video)
                process_video_frames(letter, id)
    finally:
        os.remove("video.avi")  # Clean up after ourselves
    
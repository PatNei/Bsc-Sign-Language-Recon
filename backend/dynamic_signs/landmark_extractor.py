import argparse
from genericpath import isfile
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("zip_file", 
                    help="The .zip file containing videos.",
                    type=str)
parser.add_argument("-holi", "--holistic", 
                    dest="is_holistic", 
                    help="Extract holistic landmarks.",
                    action=argparse.BooleanOptionalAction,
                    default=False,
                    type=bool)
parser.add_argument("--out", 
                    help="name of the out file. Must be a folder when combined with --holistic flag.",
                    dest="out", 
                    default="landmarks_out.csv",
                    type=str)
args = parser.parse_args()

out_path = Path(args.out)
target_path = Path(args.zip_file)
if args.is_holistic and out_path.is_file():
    raise ValueError(f"--out must set to a directory when using the holistic flag")
elif not args.is_holistic and out_path.suffix != '.csv':
    raise ValueError(f"--out must set to a .csv file when using MP hands")
elif not target_path.exists() or target_path.suffix != '.zip':
    raise ValueError(f"videoes must be in a .zip file AND exists :thinking:")

if not out_path.exists():
    print(f"Couldn't find {out_path.absolute()}, so created it.")
    if args.is_holistic:
        out_path.mkdir()
    else:
        out_path.touch()

print(f"About to process {args.zip_file} using {'Holistic' if args.is_holistic else 'Hands'}, outputting to [{args.out}]")

import re
from zipfile import ZipFile
import cv2
from sign.training.landmark_extraction.MediaPiper import MediaPiper
from sign.training.landmark_extraction.HolisticPiper import HolisticPiper
import shutil

mediapiper = MediaPiper() if not args.is_holistic else HolisticPiper()

def process_video_frames(letter: str, id: str):
    vc = cv2.VideoCapture('video.avi')
    i = 0
    if vc.isOpened():
        rval , frame = vc.read()
    else:
        rval = False
    
    #TODO: here?
    path_frames = f"./dynamic_signs/frames/"
    path_sign = f"{path_frames}{letter}"
    if not os.path.exists(path_frames):
        os.makedirs(path_frames)
    if not os.path.exists(path_sign):
        os.makedirs(path_sign)
        
    while rval:
        rval, frame = vc.read()
        if frame is None or frame.size == 0:
            continue
        cv2.imwrite(f"{path_sign}/{id}_{i}.png", frame)
        i = i + 1
    vc.release()
    mediapiper.write_dynamic_gestures_from_folder_to_csv(path_frames, args.out, id)

    shutil.rmtree(path_frames)
    
regex = r".*\/*(.+)\/(.+)\.avi"
with ZipFile(target_path, 'r') as myzip:
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
    
import argparse
import os
from pathlib import Path
import re
from zipfile import ZipFile
import cv2
from sign.training.landmark_extraction.MediaPiper import MediaPiper
from sign.training.landmark_extraction.HolisticPiper import HolisticPiper
import shutil


class DynamicLandmarkExtractor:
    def __init__(self, is_holistic=False, out_path="out.csv", target_path="videos.zip") -> None:
        self.target_path = target_path
        self.out_path = out_path
        if is_holistic:
            os.makedirs(out_path, exist_ok=True)
            self.mediapiper = HolisticPiper(out_dest=Path(out_path))
        else:
            self.mediapiper = MediaPiper()
        self.regex = r".*\/*(.+)\/(.+)\.avi"
        pass

    def process_video_frames(self, label: str, video_id: str, base_path="./dynamic_signs/frames/", video_path="./video.avi"):
        vc = cv2.VideoCapture(video_path)
        i = 0
        if vc.isOpened():
            rval , frame = vc.read()
        else:
            rval = False
            
        path = f"{base_path}{label}"
        if not os.path.exists(path):
            os.makedirs(path)
            
        while rval:
            rval, frame = vc.read()
            if frame is None or frame.size == 0:
                continue
            cv2.imwrite(f"{path}/{video_id}#{i}.png", frame)
            i = i + 1
        vc.release()
        res = self.mediapiper.write_dynamic_gestures_from_folder_to_csv(base_path, self.out_path, id=video_id)
        shutil.rmtree(path)
    
    def process_video_dataset(self):
        with ZipFile(str(Path.cwd().absolute().joinpath(target_path)), 'r') as myzip:
            try:
                for file in myzip.filelist:
                    match = re.match(self.regex, file.filename)
                    if match is not None:
                        letter = match.group(1)
                        id = match.group(2)
                        video = myzip.open(file.filename).read()
                        with open("video.avi", "wb") as video_file:
                            video_file.write(video)
                        self.process_video_frames(letter, id)
            finally:
                os.remove("video.avi")  # Clean up after ourselves

if __name__ == "__main__":
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

    extractor = DynamicLandmarkExtractor(is_holistic=args.is_holistic, out_path=args.out, target_path=args.zip_file)
    extractor.process_video_dataset()
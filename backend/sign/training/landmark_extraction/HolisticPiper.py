from typing import Any, NamedTuple
import mediapipe.python.solutions.holistic as mp_holistic
import cv2 as cv
import csv
from pathlib import Path
from sign.training.landmark_extraction.utils import ImageSequence, get_image_sequences_from_dir
from sign.training.landmark_extraction.DynamicPiper import DynamicPiper

class HolisticPiper(DynamicPiper):
    holistic: mp_holistic.Holistic
    out_dest: Path

    def __init__(self, out_dest:Path = Path.cwd().absolute().joinpath("csvs"),
                 complexity = 1, verbose = False):
        self.holistic = mp_holistic.Holistic(
            static_image_mode=True,
            model_complexity=complexity,
        )
        self.out_dest = out_dest
        self.verbose = verbose
    
    @staticmethod
    def __get_attributes_as_dict(obj : NamedTuple) -> dict[str, Any]:
        return {field : getattr(obj, field) for field in obj._fields}

    def write_processed_sequence_to_csv(self, label:str, id: str, 
                                        mp_process_results: list[NamedTuple]):
        with open(self.out_dest.joinpath(f"{label}_out.csv"), 'a', newline="") as f:        
            writer = csv.writer(f)
            for res in mp_process_results:
                res_as_dict = self.__get_attributes_as_dict(res)
                #Sort to get:
                # face_landmarks, left_hand_landmarks, pose_landmarks, pose_world_landmarks, right_hand_landmarks, segmentation_mask
                for body_part, landmarks in sorted(res_as_dict.items(), key = lambda key_value : key_value[0]):
                    toWrite = []
                    which = body_part.removesuffix("_landmarks")
                    if landmarks is not None: 
                        toWrite = list(sum([ (mrk.x, mrk.y, mrk.z) for mrk in landmarks.landmark], ()))
                    else:
                        if self.verbose:
                            print(f"No landmarks for {which}")
                    writer.writerow([which, id, *toWrite])
            
            
    def write_to_csv(self, label_files_dict: dict[str, list[ImageSequence]], verbose = False):
        for label, img_sequences in label_files_dict.items():
            for sequence in img_sequences:
                results = [ self.holistic.process(cv.imread(img_path)) for img_path in sequence.filepaths] 
                if verbose:
                    print(f"MediaPipe Holistic for {label}-{sequence.id} has {len(results)} many elements")
                self.write_processed_sequence_to_csv(label, sequence.id, results)

    def write_dynamic_gestures_from_folder_to_csv(self, parent_directory: str, out:str, id: str):
        label_files_dict = get_image_sequences_from_dir(parent_directory)
        self.write_to_csv(label_files_dict)



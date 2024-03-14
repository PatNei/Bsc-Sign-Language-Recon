import mediapipe.python.solutions.hands as mp_hands
import cv2 as cv

import csv
import os
from sign.landmarks import calc_landmark_list, pre_process_landmark
from sign.CONST import DATA_BASE_PATH, TRAIN_PATH

from sign.training.landmark_extraction.MediapipeTypes import MediapipeLandmark, MediapipeResult, MediapipeClassification
from dataclasses import dataclass
from natsort import natsorted

GestureSequence = list[MediapipeResult]

@dataclass
class DynamicGesture:
    """Fields:
    
            label -> name of the gesture

            results -> a 2D list, each list in is a sequence of images of the gesture.
    """
    label: str
    results: list[GestureSequence]

class MediaPiper:
    """
        MediaPiper, a home made interface for interacting with the mediapipe hands library.
        The class is used to create training data.
    """
    def __init__(self, num_hands = 1, gesture_sequence_sep = "_") -> None:
        # TODO: How kwargs?
        use_static_image_mode = True
        min_detection_confidence = 0.7
        min_tracking_confidence = 0.5

        hands  = mp_hands.Hands(
            static_image_mode=use_static_image_mode,
            max_num_hands=num_hands,
            min_detection_confidence=min_detection_confidence, 
            min_tracking_confidence=min_tracking_confidence,
        )
        self.__hands = hands
        self.__seq_sep = gesture_sequence_sep

    def process_image(self, img: cv.typing.MatLike) -> MediapipeResult:
        """Process a single image using mediapipe hands library

        Returns:
            A NamedTuple object, that should mimic actual mediapipe.python.solution_base.SolutionOutputs
        """
        res = self.__hands.process(img)
        # This is cursed, avoid the ignored pylance error that type NamedTuple
        #   doesn't have fields, multi_hand_landmarks etc.
        # [multi_hand_landmarks, multi_hand_world_landmarks, multi_handedness]
        cursed = [getattr(res, field) for field in res._fields]
        
        if cursed[0] is not None and cursed[2] is not None:
            # TODO: Does this cause any trouble handling more than a single hand?
            # Converts the multi_hand_landmarks which has the form: 
            #   'mediapipe.framework.formats.landmark_pb2.NormalizedLandmark'
            # into a simple python list of MediapipeTypes.MediapipeLandmark
            cursed[0] = [MediapipeLandmark(l.x, l.y, l.z) 
                         for _, l in enumerate(cursed[0][0].landmark)]
            
            cursed[2] = [MediapipeClassification(c.index, c.score, c.label) 
                         for _, c in enumerate(cursed[2][0].classification)]

        return MediapipeResult(
            multi_hand_landmarks=cursed[0],
            multi_hand_world_landmarks=cursed[1],
            multi_handedness=cursed[2],
        )

    def process_image_from_path(self, file_path: str) -> MediapipeResult:
        """Process a single image using mediapipe hands library from a file
        
        Returns:
            A NamedTuple object, that should mimic actual mediapipe.python.solution_base.SolutionOutputs
        """
        img = cv.imread(file_path)  
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = cv.flip(img, 1)
        
        return self.process_image(img)

    def process_images_from_folder_to_csv(self, base_path, out_file = "out.csv", limit = 0) -> None:
        """Given a base_path to a directory with subdirectories containing images, the method
        creates training data from all images. IF Mediapipe is unable to find identify hands in an image
        the imaged is skipped, so there may be missing "lines" in the output csv file
        
        Side-effects:
            Creates/Writes to the specified csv file

        Returns:
            None
        """
        subfolders :list[str] = [ file for file in os.listdir(base_path) 
                                  if os.path.isdir(base_path + file) ]

        for folder in subfolders:
            folder_path = base_path + os.sep + folder
            def gen_img_path(image:str):
                return folder_path + os.sep + image
            image_paths:list[str] = [ gen_img_path(image) for image in os.listdir(folder_path)
                                      if os.path.isfile(gen_img_path(image))]
            if limit != 0:
                image_paths = image_paths[:limit]

            for image in image_paths:
                img = cv.imread(image)  
                img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                img = cv.flip(img, 1)
                mp_result = self.process_image(img)

                if mp_result.multi_hand_landmarks is not None:
                    image_width, image_height = img.shape[1], img.shape[0]

                    # TODO: This used to be inside of a loop, does this pose any challenges when doing more than a single hand?
                    landmark_list = calc_landmark_list(mp_result.multi_hand_landmarks,
                                                       image_width=image_width, 
                                                       image_height=image_height)
                    pre_processed_landmark_list = pre_process_landmark(landmark_list)

                    with open(out_file, 'a', newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([folder, *pre_processed_landmark_list])
        return None

    def process_dynamic_gestures_from_folder(self, base_path:str) -> list[DynamicGesture]:
        """Given a folder of dynamic gestures (represented a folder of image sequences),
        the function will produce landmarks for all dynamic gestures.

        Expects a directory structured like: base_path/[gestures]/[image_sequences]

            [gestures] -> directory names will be used as labels
            
            [image_sequnces] -> sequences of images, a sequence is marked as the first part of the file name,
              2_23.png is then the 23rd image in sequence 2.

        Returns:
            A list of dynamic gestures, with a label field, and a 2D list of Mediapiperesults.
            Each list in the DynamicGesture.results represents a sequence of images.
        """
        labels = [folder for folder in os.listdir(base_path)
                  if os.path.isdir(base_path + os.sep + folder)]
        res: list[DynamicGesture] = []
        for label in labels:
            folder_path = base_path + os.sep + label
            files = natsorted([file for file in os.listdir(folder_path)
                               if os.path.isfile(folder_path + os.sep + file)])
            
            folder_path += os.sep

            cur: GestureSequence = []
            labelRes: list[GestureSequence] = [cur]
            prev_prefix = self.__extract_prefix(files[0])
            for image in files:
                prefix = self.__extract_prefix(image)
                if not (prefix == prev_prefix):
                    cur = []
                    labelRes.append(cur)
                
                imageRes = self.process_image_from_path(folder_path + image)
                # TODO: Do we really want to throw away pictures that couldn't
                #       be recognized by mediapipe?
                if(imageRes.multi_hand_landmarks is not None):
                    cur.append(imageRes)
                prev_prefix = prefix
            res.append(DynamicGesture(label=label, results=labelRes))

        return res

    def __extract_prefix(self, file_name:str) -> str:
        """Extract the prefix of images belonging to a sequence of a dynamic gesture.
        So, for 2_13.png returns 2
        """
        return file_name.split(self.__seq_sep)[0]

import numpy as np
if __name__ == "__main__":
    mpr = MediaPiper()

    out_file = "out.csv"
    #data_path = "data/archive/asl_alphabet_train/"
    data_path = "data/archive/dynamic_gestures/"

    print(f"Processing images from ({data_path})...")
    #mpr.process_images_from_folder_to_csv(data_path, out_file=out_file, limit=10)
    res = mpr.process_dynamic_gestures_from_folder(data_path)
    #print(f"Output result to {out_file}")


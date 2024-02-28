import mediapipe.python.solutions.hands as mp_hands
import cv2 as cv

import csv
import os
from sign.landmarks import calc_landmark_list, pre_process_landmark
from sign.CONST import DATA_BASE_PATH, TRAIN_PATH

from MediapipeTypes import *


class MediaPiper:
    """
        MediaPiper, a home made interface for interacting with the mediapipe hands library.
        The class is used to create training data.
    """
    def __init__(self, num_hands = 1) -> None:
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
        
        if cursed[0] is not None:
            # Converts the multi_hand_landmarks which has the form: 
            #   'mediapipe.framework.formats.landmark_pb2.NormalizedLandmark'
            # into a simple python list of MediapipeTypes.MediapipeLandmark
            cursed[0] = [MediapipeLandmark(l.x, l.y, l.z) for _, l in enumerate(cursed[0][0].landmark)]

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

if __name__ == "__main__":
    mpr = MediaPiper()

    out_file = "out.csv"
    data_path = "data/archive/asl_alphabet_train/"

    print(f"Processing images from ({data_path})...")
    mpr.process_images_from_folder_to_csv(data_path, out_file=out_file, limit=10)
    print(f"Output result to {out_file}")
        
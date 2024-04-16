from turtle import right
import mediapipe.python.solutions.hands as mp_hands
import cv2 as cv

import csv
import os
from sign.landmarks import calc_landmark_list, pre_process_landmark
from sign.CONST import MEDIAPIPER_VERSION_2

from sign.training.landmark_extraction.DynamicPiper import DynamicPiper
from sign.training.landmark_extraction.utils import get_image_sequences_from_dir
from sign.training.landmark_extraction.MediapipeTypes import MediapipeLandmark, MediapipeResult, MediapipeClassification
from dataclasses import dataclass

GestureSequence = list[MediapipeResult]

@dataclass
class DynamicGesture:
    """Fields:
    
            label -> name of the gesture

            results -> a 2D list, each list in is a sequence of images of the gesture.
    """
    label: str
    results: list[GestureSequence]

class MediaPiper(DynamicPiper):
    """
        MediaPiper, a home made interface for interacting with the mediapipe hands library.
        The class is used to create training data.
    """
    def __init__(self, num_hands = 1, gesture_sequence_sep = "#") -> None:
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
        self.__num_hands = num_hands
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
        if cursed[0] and cursed[1] and cursed[2]:
            # TODO: Does this cause any trouble handling more than a single hand?
            # Converts the multi_hand_landmarks which has the form: 
            #   'mediapipe.framework.formats.landmark_pb2.NormalizedLandmark'
            # into a simple python list of MediapipeTypes.MediapipeLandmark
            cursed[0] = [ MediapipeLandmark(l.x, l.y, l.z) 
                          for hand in cursed[0] 
                          for _,l in enumerate(hand.landmark) ]
            cursed[1] = [ MediapipeLandmark(l.x, l.y, l.z) 
                          for hand in cursed[1] 
                          for _,l in enumerate(hand.landmark)]
            cursed[2] = [ MediapipeClassification(c.index, c.score, c.label) 
                          for handed in cursed[2] 
                          for _,c in enumerate(handed.classification) ]

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

    def process_images_from_folder_to_csv(self, base_path, out_file = "out.csv", limit = 0, handedness = False) -> None:
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
            if limit > 0:
                image_paths = image_paths[:limit]

            for image in image_paths:
                img = cv.imread(image)  
                img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                img_versions = [img] if not handedness else [img, cv.flip(img, 1)]
                for img in img_versions:
                    #TODO: For static images, we just always get the result for the first hand
                    mp_result = self.process_image(img).get_hand_result(0)
                        
                    if mp_result.multi_hand_landmarks is not None:
                        if mp_result.multi_handedness is None:
                            err_msg = f"!!Image: {image} had hand_landmarks, but no handedness!!"
                            print(err_msg)
                            raise Exception(err_msg)
                        
                        image_width, image_height = img.shape[1], img.shape[0]

                        # TODO: This used to be inside of a loop, does this pose any challenges when doing more than a single hand?
                        landmark_list = calc_landmark_list(mp_result.multi_hand_landmarks,
                                                        image_width=image_width, 
                                                        image_height=image_height)
                        pre_processed_landmark_list = pre_process_landmark(landmark_list)

                        with open(out_file, 'a', newline="") as f:
                            writer = csv.writer(f)
                            if handedness:
                                writer.writerow([folder, mp_result.multi_handedness[0].label.lower(), *pre_processed_landmark_list])
                            else:
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
        labels_image_dict = get_image_sequences_from_dir(base_path, separator=self.__seq_sep)
        res: list[DynamicGesture] = []
        for label, sequences in labels_image_dict.items():
            label_res = []
            for seq in sequences:
                seq_results = [self.process_image_from_path(img) for img in seq.filepaths]
                seq_results = list(filter(lambda mp_res: bool(mp_res.multi_hand_landmarks), seq_results))
                label_res.append(seq_results)
            res.append(DynamicGesture(label, label_res))
        return res
    
    def write_dynamic_gestures_from_folder_to_csv(self, path_frames:str, out:str, id:str = ""):
        """Extract landmarks from a folder of folders of image sequences: like folder[folder[img_sequence]]
        NOTE: The provided id will be used for ALL the sequences if provided.

        :param: id (string) - if provided all entries written to CSV will have this ID, this functionality
        is primarily used for the landmark_extractor.py. IF left empty, sequences will receive arbitrary numeric ids. 
        """
        res = self.process_dynamic_gestures_from_folder(path_frames)
        with open(out, 'a', newline="") as f:
            writer = csv.writer(f)
            # writer.writerow([MEDIAPIPER_VERSION_2])
            for dynamic_gesture in res:
                for sequence_id, gesture_sequence in enumerate(dynamic_gesture.results):
                    seq_id = id if id else sequence_id
                    for mp_result in gesture_sequence:
                        if mp_result.number_of_hands() == 1:
                            x = mp_result.multi_hand_landmarks
                            if x and mp_result.multi_handedness:
                                landmarks = [[landmark.x, landmark.y, landmark.z] for landmark in x]
                                hand_id = mp_result.multi_handedness[0].index
                                writer.writerow([dynamic_gesture.label, seq_id, hand_id, *landmarks])
                        else:
                            if mp_result.multi_handedness and mp_result.multi_hand_landmarks:
                                if len(mp_result.multi_handedness) > (len(mp_result.multi_hand_landmarks) / 2):
                                    raise Exception(f"Mediapipe found landmarks for {len(mp_result.multi_hand_landmarks)} hands, but reported handedness for {len(mp_result.multi_handedness)} hands")
                                row_out:list = [dynamic_gesture.label, seq_id]
                                for idx, hand_id in enumerate(map(lambda x: x.index ,mp_result.multi_handedness)):
                                    if idx in (0,1):
                                        landmarks_hand_for_id = mp_result.multi_hand_landmarks_by_hand(idx)
                                        
                                        if landmarks_hand_for_id:
                                            landmarks = [[landmark.x, landmark.y, landmark.z] for landmark in landmarks_hand_for_id]
                                            row_out.append(hand_id)
                                            row_out.extend(landmarks)
                                        else:
                                            raise Exception(f"Something is wrong here {mp_result}")
                                    else: 
                                        raise Exception(f"Working with unkown handedness-index: {hand_id}")
                                writer.writerow(row_out)   

if __name__ == "__main__":
    mpr = MediaPiper(num_hands=2, gesture_sequence_sep="_")

    out_file = "bing_bong_out.csv"
    #data_path = "data/archive/asl_alphabet_train/"
    data_path = "data/archive/dynamic_gestures"

    print(f"Processing images from ({data_path})...")
    #res = mpr.process_image_from_path("data/test.png")
    #res = mpr.process_image_from_path("data/archive/asl_alphabet_train/A/A1.jpg")
    #print(f"handedness: --{res.multi_handedness}--")
    #print(len(res.multi_hand_landmarks if res.multi_hand_landmarks else []))
    
    #mpr.process_images_from_folder_to_csv(data_path, out_file=out_file, handedness=True)
    #res = mpr.process_dynamic_gestures_from_folder(data_path)
    
    ##Make MediaPiper spit out a csv from a folder of folders
    mpr.write_dynamic_gestures_from_folder_to_csv(data_path, out_file)
    print(f"Output result to {out_file}")

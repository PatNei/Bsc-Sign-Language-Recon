from pathlib import Path

import numpy as np
from sign.CONST import CLASSIFIER_PATH
from sign.keypoint_classifier import KeyPointClassifier, NormalizedLandmarks
from sign.dynamic_classifier import DynamicClassifier
import csv

from sign.landmarks import NormalizedLandmark, NormalizedLandmarksSequenceDTO

class Recogniser:
    def __init__(self) -> None:
        self.keypoint_classifier = KeyPointClassifier()
        self.dynamic_classifier = DynamicClassifier()

    def get_annotation(self, landmarks : NormalizedLandmarks) -> str:

        return self.keypoint_classifier(landmarks)
    
    def get_dynamic_annotation(self, landmarksDTO: NormalizedLandmarksSequenceDTO) -> str:
        # target_length = 24
    
        landmarks_sequence: list[NormalizedLandmarks] = []
        for image_landmarks in landmarksDTO.data:
            image_normalized_landmarks = [NormalizedLandmark(lnd_mrk) for lnd_mrk in image_landmarks.data]        
            mrks = NormalizedLandmarks(data = image_normalized_landmarks)
            landmarks_sequence.append(mrks)
        
        # frames_list : list = []


        # if len(frames_list) < target_length:
        #     frames = bob.pad_sequences_of_landmarks(frames_list)
        # else: 
        #     frames = bob.extract_keyframes_sample(frames_list)
        
        # image_normalized_landmarks = []
        # landmarks_sequence = []
        # for i in range(0, len(frames), 3):
        #     landmark = NormalizedLandmark()
        #     landmark.x = np.float32(frames[i])
        #     landmark.y = np.float32(frames[i+1])
        #     landmark.z = np.float32(frames[i+2])
        #     image_normalized_landmarks.append(landmark)
        # mrks = NormalizedLandmarks(data = image_normalized_landmarks)
        
        # print(f"\n\n\n\n\n\n\n-------{len(landmarks_sequence)}-------\n\n\n\n\n\n")
        return self.dynamic_classifier(landmarks_sequence)
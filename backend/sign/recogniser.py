from pathlib import Path
from typing import Tuple

import numpy as np
from sign.CONST import CLASSIFIER_PATH
from sign.keypoint_classifier import KeyPointClassifier, NormalizedLandmarks
from sign.dynamic_classifier import DynamicClassifier
import csv

from sign.landmarks import NormalizedLandmark, NormalizedLandmarksSequencesDTO

class Recogniser:
    def __init__(self) -> None:
        self.keypoint_classifier = KeyPointClassifier()
        self.dynamic_classifier = DynamicClassifier()

    def get_annotation(self, landmarks : NormalizedLandmarks) -> str:
        return self.keypoint_classifier(landmarks)
    
    def get_dynamic_annotation(self, landmarkSequencesDTO: NormalizedLandmarksSequencesDTO) -> str:
        # target_length = 24
        landmarks_sequence: list[NormalizedLandmarks] = []
        for landmarksDTO in landmarkSequencesDTO.data:
            for image_landmarks in landmarksDTO.data:
                image_normalized_landmarks = [NormalizedLandmark(lnd_mrk) for lnd_mrk in image_landmarks.data]        
                mrks = NormalizedLandmarks(data = image_normalized_landmarks, handedness=image_landmarks.handedness)
                landmarks_sequence.append(mrks)
        return self.dynamic_classifier(landmarks_sequence)
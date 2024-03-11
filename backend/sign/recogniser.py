from pathlib import Path
from sign.CONST import CLASSIFIER_PATH
from sign.keypoint_classifier import KeyPointClassifier, NormalizedLandmarks
from sign.dynamic_classifier import DynamicClassifier
import csv

class Recogniser:
    def __init__(self) -> None:
        self.keypoint_classifier = KeyPointClassifier()
        self.dynamic_classifier = DynamicClassifier()

    def get_annotation(self, landmarks : NormalizedLandmarks) -> str:

        return self.keypoint_classifier(landmarks)
    
    def get_dynamic_annotation(self, landmarks_sequence: list[NormalizedLandmarks]) -> str:

        return self.dynamic_classifier(landmarks_sequence)
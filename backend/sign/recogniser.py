from pathlib import Path
from sign.CONST import CLASSIFIER_PATH
from sign.keypoint_classifier import KeyPointClassifier, NormalizedLandmarks
import csv

class Recogniser:
    def __init__(self) -> None:
        self.keypoint_classifier = KeyPointClassifier()
        self.keypoint_classifier_labels = []

        # Read labels ###########################################################
        with open(str(Path.cwd().absolute().joinpath(CLASSIFIER_PATH)), encoding='utf-8-sig') as f:
            self.keypoint_classifier_labels = csv.reader(f)
            self.keypoint_classifier_labels = [row[0] for row in self.keypoint_classifier_labels]

    def get_annotation(self, landmarks : NormalizedLandmarks) -> str:

        return self.keypoint_classifier(landmarks)
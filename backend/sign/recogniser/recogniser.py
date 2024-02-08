from pydantic import BaseModel
from sign.model import KeyPointClassifier
import csv

from sign.model.keypoint_classifier.keypoint_classifier import NormalizedLandmarks



class Recogniser:
    def __init__(self) -> None:
        self.keypoint_classifier = KeyPointClassifier()
        self.keypoint_classifier_labels = []

        # Read labels ###########################################################
        with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            keypoint_classifier_labels = csv.reader(f)
            keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels]

    def get_annotation(self, landmarks : NormalizedLandmarks) -> str:
        # Hand sign classification
        hand_sign_id = self.keypoint_classifier(landmarks)

        return self.keypoint_classifier_labels[hand_sign_id]
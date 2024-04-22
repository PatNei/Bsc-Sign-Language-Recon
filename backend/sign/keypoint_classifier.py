#!/usr/bin/env python
# -*- coding: utf-8 -*-
from joblib import load
import numpy as np
from pathlib import Path
from sign.CONST import STATIC_MODEL_PATH
from sign.landmarks import NormalizedLandmarks, calc_landmark_list, pre_process_landmark
from sign.model import SignClassifier

class KeyPointClassifier(object):
    def __init__(
        self,
        model_path = STATIC_MODEL_PATH,
        num_threads=1,
    ):    
        self.classifier: SignClassifier = SignClassifier(model_path)

    def __call__(self, landmark_list: NormalizedLandmarks) -> np.str_:
        # landmarks = np.array(list(itertools.chain.from_iterable([data.x, data.y] for data in landmark_list.data)), dtype=np.float32)
        handedness = landmark_list.handedness
        landmarks = calc_landmark_list(landmark_list.data)
        # Conversion to relative coordinates / normalized coordinates
        landmarks = pre_process_landmark(landmarks)
        
        numpy_landmarks = np.array([landmarks], dtype=np.float32)
        predictions = self.classifier.predict(numpy_landmarks)

        return predictions[0]

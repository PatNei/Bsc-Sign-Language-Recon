#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from sign.CONST import STATIC_MODEL_PATH, STATIC_MODEL_USES_HANDEDNESS
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
        handedness = landmark_list.handedness
        # landmarks = np.array(list(itertools.chain.from_iterable([data.x, data.y] for data in landmark_list.data)), dtype=np.float32)
        landmarks = calc_landmark_list(landmark_list.data)
        # Conversion to relative coordinates / normalized coordinates
        landmarks = pre_process_landmark(landmarks)
        
        if STATIC_MODEL_USES_HANDEDNESS:
            #M6 model expects the input to have it's handedness appeneded at the end.
            landmarks.append(1 if handedness == "right" else 0)

        numpy_landmarks = np.array([landmarks], dtype=np.float32)
        
        predictions = self.classifier.predict(numpy_landmarks)


        return predictions[0]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from joblib import load
import numpy as np
from pathlib import Path
from sign.CONST import MODEL_PATH
from sign.landmarks import NormalizedLandmarks, calc_landmark_list, pre_process_landmark
from sign.model import SignClassifier

class KeyPointClassifier(object):
    def __init__(
        self,
        model_path=str(Path.cwd().absolute().joinpath(MODEL_PATH)),
        num_threads=1,
    ):
        
        self.classifier: SignClassifier = load(model_path)
        
        # self.interpreter = tf.lite.Interpreter(model_path=model_path, num_threads=num_threads)
        
        # self.interpreter.allocate_tensors()
        # self.input_details = self.interpreter.get_input_details()
        # self.output_details = self.interpreter.get_output_details()

    def __call__(self, landmark_list: NormalizedLandmarks) -> np.str_:
        # landmarks = np.array(list(itertools.chain.from_iterable([data.x, data.y] for data in landmark_list.data)), dtype=np.float32)
        landmarks = calc_landmark_list(landmark_list.data)

        # Conversion to relative coordinates / normalized coordinates
        landmarks = pre_process_landmark(landmarks)
        
        landmarks = np.array([landmarks], dtype=np.float32)    
        predictions = self.classifier.predict(landmarks)

        return predictions[0]

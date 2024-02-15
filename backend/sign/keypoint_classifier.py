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
        landmarks = calc_landmark_list(landmark_list)

        # Conversion to relative coordinates / normalized coordinates
        landmarks = pre_process_landmark(landmarks)
        
        
        # This is going to change
        landmarks = np.array([landmarks], dtype=np.float32)
        
        # App.py <- here
        predictions = self.classifier.predict(landmarks)
        
        
        # input_details_tensor_index = self.input_details[0]['index']
        # self.interpreter.set_tensor(input_details_tensor_index, landmarks)
        # self.interpreter.invoke()

        # output_details_tensor_index = self.output_details[0]['index']

        # result = self.interpreter.get_tensor(output_details_tensor_index)

        # result_index = np.argmax(np.squeeze(result))

        return predictions[0]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import itertools
from joblib import load
import numpy as np
from pydantic import BaseModel
from pathlib import Path
from sign.CONST import MODEL_PATH

from sign.model import SignClassifier

class NormalizedLandmarkDTO(BaseModel):
    x: str
    y: str
    z: str

    
class NormalizedLandmarksDTO(BaseModel):
    data: list[NormalizedLandmarkDTO]


class NormalizedLandmark():
    x: np.float32
    y: np.float32
    z: np.float32
    
    def __init__(self, dto : NormalizedLandmarkDTO):
        self.x = np.float32(dto.x)
        self.y = np.float32(dto.y)
        self.z = np.float32(dto.z)
    
class NormalizedLandmarks():
    data: list[NormalizedLandmark]
    
    def __init__(self, landmarks : list[NormalizedLandmark]):
        self.data = landmarks


def calc_landmark_list(landmarks : NormalizedLandmarks):
    image_width, image_height = 1280, 720

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.data):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point

def pre_process_landmark(landmark_list) -> list[float]:
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list

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
        predictions = self.classifier.predict([landmarks])
        
        
        # input_details_tensor_index = self.input_details[0]['index']
        # self.interpreter.set_tensor(input_details_tensor_index, landmarks)
        # self.interpreter.invoke()

        # output_details_tensor_index = self.output_details[0]['index']

        # result = self.interpreter.get_tensor(output_details_tensor_index)

        # result_index = np.argmax(np.squeeze(result))

        return predictions[0]

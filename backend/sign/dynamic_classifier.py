
from typing import Any
from fastapi import HTTPException
import numpy as np
from sign.CONST import DYNAMIC_MODEL_PATH
from sign.landmarks import NormalizedLandmarks
from sign.model import SignClassifier
from sign.trajectory import TrajectoryBuilder

class DynamicClassifier():
    def __init__(self):
        self.classifier = SignClassifier(DYNAMIC_MODEL_PATH)
        self.bob = TrajectoryBuilder()
    
    def __call__(self, landmark_list: list[NormalizedLandmarks]) -> str:
        new_sequence: list[np.ndarray[Any, np.dtype[np.float32]]] = []
        for image_landmarks in landmark_list:
            if len(image_landmarks.data) < 1:
                 continue
            arr : np.ndarray[Any, np.dtype[np.float32]] = np.array([(mrk.x,mrk.y,mrk.z) for mrk in image_landmarks.data]).flatten()
            new_sequence.append(arr)

        keyframes = self.bob.extract_keyframes_sample(new_sequence)
        
        sequence_trajectory = self.bob.make_trajectory(keyframes)

        model_input = self.bob.make_trajectory_values(sequence_trajectory)
        
        predictions = self.classifier.predict(np.array([model_input]))

        return predictions[0]
    
        # try:
            # keyframes = self.bob.extract_keyframes(new_sequence)
            
            # sequence_trajectory = self.bob.make_trajectory(keyframes)

            # model_input = self.bob.make_trajectory_values(sequence_trajectory)
            
            # predictions = self.classifier.predict(np.array([model_input]))

            # return predictions[0]
        # except Exception as e:
        #     print(e)
        #     raise HTTPException(status_code=400, detail=str(e))
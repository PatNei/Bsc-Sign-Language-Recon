
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
        
        new_sequence = []
        for image_landmarks in landmark_list[:13]:
            if len(image_landmarks.data) < 1:
                 continue
            arr = np.array([(mrk.x,mrk.y,mrk.z) for mrk in image_landmarks.data]).flatten()
            new_sequence.append(arr)
        
        sequence_as_np_array = np.array(new_sequence)    
        sequence_trajectory = self.bob.make_trajectory(sequence_as_np_array)

        model_input = self.bob.make_trajectory_values(sequence_trajectory)
         
        predictions = self.classifier.predict(np.array([model_input]))

        return predictions[0]
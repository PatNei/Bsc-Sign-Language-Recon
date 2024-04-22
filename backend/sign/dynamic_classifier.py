from typing import Tuple
import numpy as np
import numpy.typing as npt
from sign.CONST import DYNAMIC_MODEL_PATH
from sign.landmarks import NormalizedLandmark, NormalizedLandmarkDTO, NormalizedLandmarks, pre_process_landmark, calc_landmark_list
from sign.model import SignClassifier
from sign.trajectory import TrajectoryBuilder

import random

class DynamicClassifier():
    def __init__(self):
        self.classifier = SignClassifier(DYNAMIC_MODEL_PATH)
        self.bob = TrajectoryBuilder(target_len=24)
    
    def __call__(self, landmark_list: list[Tuple[NormalizedLandmarks, str]]) -> str:
        new_landmark_list: list[np.ndarray] = []
        
        for landmarks in landmark_list:
            # landmarks.handedness # here is something you might want to use?
            # WE GOT HANDEDNESS HERE FOLKS
            new_landmark_list.append(np.array([(mrk.x,mrk.y,mrk.z) for mrk in landmarks.data]).flatten())
        new_frames = self.bob.enforce_target_length(new_landmark_list)
        res = self._preprocess_mediapipe_landmarks(new_frames)
        hand_landmarks_raw = [ hand_landmark for hand_landmark, _ in res ]
            
        flatmarks = [ flatmark for _, flatmark in res ] #without Z values
        sequence_trajectory = self.bob.make_trajectory(np.array(hand_landmarks_raw))
        model_input = sequence_trajectory.to_numpy_array()
        for flat_landmark in flatmarks:
            model_input = np.append(model_input, flat_landmark)
        # Model now expects input to be of the form:
        # <simple-trajectory-as-xyz-values><42-xy-values-from-yt-algo><42-xy-values-from-yt-algo>...
        predictions = self.classifier.predict(np.array([model_input]))

        return predictions[0]
    
    def _preprocess_mediapipe_landmarks(self, ldnmrks:list[np.ndarray]) -> list[Tuple[npt.NDArray[np.float32], list[float]]]:
        """Converts mediapipe landmarks to a list of tuples.
        Tuples consist of the "raw" mediapipe multi_hand_landmarks, and the 
        preprocessed landmarks (that we also use for static models)
        """
        converted_lndmrks: list[Tuple[npt.NDArray[np.float32], list[float]]] = []

        for image_landmarks in ldnmrks:
            if len(image_landmarks.data) < 1:
                 continue
            arr: list[NormalizedLandmark] = []
            for i in range(0, len(image_landmarks), 3):
                landmark = NormalizedLandmark(NormalizedLandmarkDTO(x=str(image_landmarks[i]), y=str(image_landmarks[i+1]), z=str(image_landmarks[i+2])))
                arr.append(landmark)
            lndmrk_list = calc_landmark_list(arr)
            preprocessed = pre_process_landmark(lndmrk_list)
            converted_lndmrks.append( (image_landmarks.flatten(), preprocessed) )
        return converted_lndmrks

    #TODO: Should probably be part of trajectory builder
    def _extract_keyframes_sample_keep_preprocessed_landmarks(self,
              landmark_list: list[Tuple[npt.NDArray[np.float32], list[float]]]) -> Tuple[npt.NDArray[np.float32], list[list[float]] ]:
            """Extract keyframs using the sample method.
            But it keeps the raw mediapipe landmarks and
            the landmarks "pre-processed" together in a single tuple.
            """
            random.seed(42)
            res = [landmark_list[0]]
            res.extend(random.sample(landmark_list[1:-1], self.bob.target_len - 2))
            res.append(landmark_list[-1])

            keyframes = [raw_mp_landmarks for raw_mp_landmarks,_ in res]
            pre_processed_landmarks = [preprossed for _,preprossed in res]

            return np.array(keyframes), pre_processed_landmarks
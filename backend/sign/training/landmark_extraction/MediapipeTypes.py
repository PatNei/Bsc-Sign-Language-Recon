from typing import NamedTuple, Union
import numpy as np

class MediapipeLandmark(NamedTuple):
    """ A raw landmark directly from Mediapipe hands
    """
    x: np.float32
    y: np.float32
    z: np.float32

class MediapipeClassification(NamedTuple):
    """ A raw classification of handedness from Mediapipe
    """
    index: np.int32
    score: np.float32
    label: np.str_

class MediapipeResult(NamedTuple):
    """ A Mediapipe hands result.
    It could be the result of calling hands.process(img)

    TODO: world_landmarks and handedness are not actually sweet python lists,
    there are instead scary Mediapipe protobuf classes
    """
    multi_hand_landmarks: Union[list[MediapipeLandmark], None]
    multi_hand_world_landmarks: Union[list[MediapipeLandmark], None]
    multi_handedness: Union[list[MediapipeClassification], None]
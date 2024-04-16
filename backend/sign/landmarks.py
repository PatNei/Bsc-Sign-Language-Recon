
import copy
from dataclasses import dataclass
import itertools
from pydantic import BaseModel
import numpy as np

from typing import Union, Tuple
from sign.training.landmark_extraction.MediapipeTypes import MediapipeLandmark

class NormalizedLandmarkDTO(BaseModel):
    x: str
    y: str
    z: str

    
class NormalizedLandmarksDTO(BaseModel):
    data: list[NormalizedLandmarkDTO]
    handedness: str

class NormalizedLandmarksSequenceDTO(BaseModel):
    data: list[NormalizedLandmarkDTO]

class NormalizedLandmark():
    x: np.float32
    y: np.float32
    z: np.float32
    
    def __init__(self, dto: NormalizedLandmarkDTO | None = None):
        if dto is not None:
            self.x = np.float32(dto.x)
            self.y = np.float32(dto.y)
            self.z = np.float32(dto.z)
        
@dataclass
class NormalizedLandmarks():
    data: list[NormalizedLandmark]
    handedness: str
    
@dataclass()
class NormalizedLandmarksSequence(): 
    seq = list[NormalizedLandmarks]

##------------------------------------------------------------------------------------##
##                                                                                    ##
##  SHOUTOUT TO OUR BOI                                                               ##
##  https://github.com/kinivi/hand-gesture-recognition-mediapipe                      ##
##                                                                                    ##
##                                                                                    ##
##------------------------------------------------------------------------------------##

def calc_landmark_list(landmarks : Union[list[MediapipeLandmark], list[NormalizedLandmark]], handedness: str,
                       image_width = 1280, 
                       image_height = 720) -> Tuple[list[Tuple[int, int]], str]:
    """ Turns a list of MediapipeLandmarks into a list of screen coordinates

        Returns: 
            The list of landmarks turned into screen coordinates, [x,y]
    """

    landmark_point = []

    # Keypoint
    for landmark in landmarks:
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point.append([landmark_x, landmark_y])

    return (landmark_point, handedness)

def pre_process_landmark(landmark_list: list[Tuple[int, int]], handedness: str) -> Tuple[list[float], str]:
    """ Takes a list of landmarks that have been converted using calc_landmark_list
        and performs the final preprocessing step. That is normalizing all the landmarks
        according to the max absolut value 

        Returns: 
            A list of processed landmarks
    """
    res = []
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]
        
        x = landmark_point[0] - base_x
        y = landmark_point[1] - base_y
        
        res.append(x)
        res.append(y)
   
    # Normalization
    max_value = max(list(map(abs, res)))
    def normalize_(n : int) -> float:
        return n / max_value

    res = list(map(normalize_, res))

    return (res, handedness)

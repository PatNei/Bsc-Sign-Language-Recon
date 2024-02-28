import numpy as np
import numpy.typing as npt

from typing import Tuple, Union
from MediapipeTypes import *
from sign.landmarks import NormalizedLandmark

##-----------------------##
##                       ##
##  SHOUTOUT TO OUR BOI  ##
##                       ##
##-----------------------##

def pre_process_landmark(landmark_list: list[Tuple[int, int]]) -> list[float]:
    """ Takes a list of landmarks that have been converted using calc_landmark_list
        and performs the final preprocessing step. That is normalizing all the landmarks
        according to the max absolut value 

        Returns: a list of processed landmarks
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
    def normalize_(n):
        return n / max_value

    res = list(map(normalize_, res))

    return res

def calc_landmark_list(landmarks: Union[list[MediapipeLandmark], list[NormalizedLandmark]], image_width: int, image_height:int) -> list[Tuple[int, int]]:
    """ Turns a list of MediapipeLandmarks into a list of screen coordinates

        Returns: The list of landmarks turned into screen coordinates, [x,y]
    """

    landmark_point : list[Tuple[int,int]] = []

    # Keypoint
    for landmark in landmarks:
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append((landmark_x, landmark_y))

    return landmark_point
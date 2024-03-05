from enum import IntEnum, Enum
from typing import List
import numpy as np
from numpy import dtype, type
from sign.landmarks import NormalizedLandmark, NormalizedLandmarks, NormalizedLandmarksSequence
from dataclasses import dataclass

DIMENSIONS = 3  # x, y, and z (always 3 for consistency)
LANDMARK_POINTS = 21
LANDMARK_AMOUNT = DIMENSIONS * LANDMARK_POINTS
ZERO_PRECISION = 0.1
SCALED_PRECISION = True # if True, the zero precision is scaled by the maximal displacement over an axis, but remains at least equal to self.zero_precision. This mitigates the problem of the zero precision being too small for fast movements.
HANDEDNESS = 2

class HAND(IntEnum):
    LEFT=0
    RIGHT=1

class direction(Enum):
    UP = 1
    RIGHT = UP
    INTO = UP
    STATIONARY = 0
    DOWN = -1
    LEFT = DOWN
    AWAY = DOWN


@dataclass
class trajectory:
    x: int
    y: int
    z: int
    
def hands_spatial_position(landmarks:NormalizedLandmarks,hand=HAND):
    """
    Should take the mean value of the landmarks and apply it where it makes sense.
    """
    handType = 0 if hand.LEFT else 1
    
    return landmarks.data[handType]

def convert_landmark_to_npArray(landmark:NormalizedLandmark):
    return np.array((landmark.x,landmark.y,landmark.z))
    

def make_step_directions(_previous:NormalizedLandmark,_current:NormalizedLandmark):
    previous = np.array(_previous,np.dtype(NormalizedLandmark))
    current = _current
    
    # TODO: Maybe check if dimensions are correct
    
    if SCALED_PRECISION: 
        
    
    
    return

def generate_trajectories(landmarks_seq: NormalizedLandmarksSequence, hand=HAND):
    ## Do the thing
    
    trajectories = []
    previous = hands_spatial_position(landmarks_seq[0],hand)
    for landmark in landmarks_seq[1:]:
        current = hands_spatial_position(landmark,hand)
        directions = make_step_directions(previous,current)
        trajectories.append(directions)
        previous = current
    return trajectories

if "__name__" == "__main__":
    make_step_directions()
    
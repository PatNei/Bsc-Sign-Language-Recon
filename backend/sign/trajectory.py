import array
from enum import IntEnum, Enum
from typing import List, Union
import numpy as np
from numpy import typing as npt
from pytz import ZERO
from sign.landmarks import NormalizedLandmark, NormalizedLandmarks
from dataclasses import dataclass

NormalizedLandmarksSequence = list[NormalizedLandmarks]

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

@dataclass
class trajectory_element:
    x: direction = direction.STATIONARY
    y: direction = direction.STATIONARY
    z: direction = direction.STATIONARY
    
@dataclass
class trajectory2:
    directions: list[trajectory_element]

def landmarks_to_single_mean(landmarks: np.ndarray) -> np.ndarray:
    reshaped = landmarks.reshape((-1,21,3))
    return np.mean(reshaped, axis=1).flatten()

def is_within_boundaries(prev_mean:Union[float, np.float32], 
                         cur_mean:Union[float, np.float32],
                         boundary = 0.01, bertram_mode = False
                         ) -> Union[bool, np.bool_]:
    boundary = boundary / 2
    if bertram_mode:
        diff = abs(prev_mean - cur_mean)
        return diff <= boundary
    else:
        upper = prev_mean + boundary
        lower = prev_mean - boundary

        return lower <= cur_mean <= upper

def create_trajectory_element(prev:np.ndarray, cur:np.ndarray) -> trajectory_element:
    directions: list[direction] = []

    for dim in range(DIMENSIONS):
        mean_p_dim:np.float32 = prev[dim]
        mean_c_dim:np.float32 = cur[dim]

        if dim == 1:
            print(f"prev_mean_y: {mean_p_dim}, cur_mean_y: {mean_c_dim}")

        if is_within_boundaries(mean_p_dim, mean_c_dim):
            directions.append(direction.STATIONARY)
        else:
            directions.append(direction.UP if mean_p_dim > mean_p_dim else direction.DOWN)

    return trajectory_element(*directions)

def make_trajectory(image_landmark_sequence: np.ndarray) -> trajectory2:
    res: list[trajectory_element] = []

    previous = image_landmark_sequence[0]
    for current in image_landmark_sequence[1:]:
        mean_prev = landmarks_to_single_mean(previous)
        mean_cur = landmarks_to_single_mean(current)
        
        next_elm_of_trajectory = create_trajectory_element(mean_prev, mean_cur)
        res.append(next_elm_of_trajectory)
        previous = current

    return trajectory2(res)


def hands_spatial_position(landmarks:NormalizedLandmarks,hand=HAND):
    """
    Should take the mean value of the landmarks and apply it where it makes sense.
    """
    handType = 0 if hand.LEFT else 1
    
    return landmarks.data[handType]

def convert_landmark_to_npArray(landmark:NormalizedLandmark):
    return np.array((landmark.x,landmark.y,landmark.z))
    

def make_step_directions(_previous:NormalizedLandmark,_current:NormalizedLandmark,zero_precision:float):
    """
    """
    # TODO: Refactor these types, they are not transparent
    previous = np.array(_previous,np.object_)
    current = np.array(_current,np.object_)
    
    # TODO: Maybe check if dimensions are correct
    if SCALED_PRECISION: # increases precision for the zero precision if the movement is too low.
        zero_precision = find_best_precision(previous,current,zero_precision)        
    
    
    return

def find_best_precision(_previous:npt.NDArray,_current:npt.NDArray, zero_precision:float) -> float:
    max_displacement = np.max(np.abs(_current - _previous))
    if max_displacement > zero_precision * 2:
        zero_precision = max_displacement / 2
    return zero_precision

def generate_trajectories(landmarks_seq: NormalizedLandmarksSequence,zero_precision:float,hand=HAND):
    ## Do the thing
    
    trajectories = []
    previous = hands_spatial_position(landmarks_seq[0],hand)
    for landmark in landmarks_seq[1:]:
        current = hands_spatial_position(landmark,hand)
        directions = make_step_directions(previous,current,zero_precision)
        trajectories.append(directions)
        previous = current
    return trajectories



if __name__ == "__main__":
    fist_down_seq = np.load("./dynamic_signs/fist_down_seq_npyarray.npy")
    
    landmarks = fist_down_seq
    #reshaped = landmarks.reshape((-1, 21, 3))
    #print(landmarks)
    #print(np.mean(reshaped, axis=1))
    #mean = np.mean(reshaped, axis = 1)

    #print("mean HERE: ", mean.flatten())

    traj = make_trajectory(fist_down_seq)
    print(traj)
    for elm in traj.directions:
        print(f"x:{elm.x}, y: {elm.y}, z: {elm.z}")

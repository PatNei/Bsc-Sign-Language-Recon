from enum import IntEnum, Enum
import random
from typing import Any, Tuple, TypeVar, Union
import numpy as np
from numpy import typing as npt
from sign.landmarks import NormalizedLandmark, NormalizedLandmarks
from dataclasses import dataclass
from typing import cast

NormalizedLandmarksSequence = list[NormalizedLandmarks]


DIMENSIONS = 3  # x, y, and z (always 3 for consistency)
LANDMARK_POINTS = 21
LANDMARK_AMOUNT = DIMENSIONS * LANDMARK_POINTS
ZERO_PRECISION = 0.1
SCALED_PRECISION = True # if True, the zero precision is scaled by the maximal displacement over an axis, but remains at least equal to self.zero_precision. This mitigates the problem of the zero precision being too small for fast movements.
HANDEDNESS = 2
T = TypeVar("T")

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
class trajectory_element:
    x: direction = direction.STATIONARY
    y: direction = direction.STATIONARY
    z: direction = direction.STATIONARY
    
@dataclass
class trajectory:
    directions: list[trajectory_element]

    def to_numpy_array(self) -> np.ndarray:
        return np.array([(te.x.value, te.y.value, te.z.value) for te in self.directions]).flatten()

    def to_float_list(self) -> list[float]:
        asd = list(sum([(float(te.x.value), float(te.y.value), float(te.z.value)) for te in self.directions], ()))
        return asd

class TrajectoryBuilder:
    def __init__(self, bertram_mode = True, boundary = 0.01, target_len = 3):
        self.target_len = target_len
        self.bertram_mode = bertram_mode
        self.boundary = boundary
        if bertram_mode: 
            print("🔥🔥 TrajectoryBuilder is now running in BERTRAM_MODE 🔥🔥")

    def enforce_target_length(self, seq:list[T]) -> list[T]:
        if len(seq) < self.target_len:
            return self.pad_sequences_of_landmarks(seq)
        else: 
            return self.extract_keyframes_sample(seq)
    
    def landmark_list_to_trajectories(self,landmarks:list[list[float]],num_landmarks=21,dimensions=3):
        """Creates a trajectory(representing a gesture ) from a sequence of landmarks.

            :param image_landmark_sequence: list of pictures, that have been reduced to landmarks
                np.array(np.array(landmarks)), where each landmark has 3 float coordinates (x,y,z).
                
            :return: A trajectory object.
        """
        res: list[trajectory_element] = []
        
        if len(landmarks) < 3:
           raise ValueError(f"landmark list is shorter than 3 elements and can't be processed")
        
        for previous,current in zip(landmarks[0:],landmarks[1:]):
            mean_prev = self.frame_to_single_mean(previous,num_landmarks=num_landmarks,dimensions=dimensions)
            mean_cur = self.frame_to_single_mean(current,num_landmarks=num_landmarks,dimensions=dimensions)
            if len(mean_prev) < 1 or len(mean_cur) < 1:
                continue
            try:
                next_elm_of_trajectory = self.create_trajectory_element(mean_prev, mean_cur)
            except Exception as e:
                print(e)
                continue
            res.append(next_elm_of_trajectory)

        return trajectory(res)            
    
    # Just the length of 3D vector difference, don't worry bout it
    def _distance(self, pos1, pos2) -> float:
        return float(np.linalg.norm(pos1 - pos2))

    def remove_outliers(self, seq: list[T]) -> list[T]:
        positions = []
        seq_new = cast(np.ndarray,seq)
        for i in range(len(seq)):
            positions.append(self.landmarks_to_single_mean(seq_new[i]))

        non_outliers = [seq[0]]
        for i in range(1, len(seq) - 1):
            if min(self._distance(positions[i-1], positions[i]), self._distance(positions[i], positions[i+1])) > \
                    self._distance(positions[i-1], positions[i+1]):
                # outlier
                print("REMOVING OUTLIER")
                continue
            non_outliers.append(seq[i])

        non_outliers.append(seq[-1])
        return non_outliers
    
    def pad_sequences_of_landmarks(self,seq:list[T]) -> list[T] :
        """
        TODO: Better way to do this?
        
        This functions loops the sequence until it reaches the target length.
        
        """
        seq_length = len(seq)
        new_seq = []
        if (self.target_len <= 2):
            raise Exception("stop it")
        i = 0
        while True:
            if len(new_seq) == self.target_len:
                break
            new_seq.append(seq[i % seq_length])
            i += 1
        return new_seq
    
    def extract_keyframes_sample(self, seq: list[T]) -> list[T]:
        """
        TODO: Do something with the seq type (which was list[np.ndarray[Any, np.dtype[np.float32]]])
        
        Extracts keyframes from a sequence of landmarks to get target_len frames to send to the model.
        Why random.sample? This results in extracting keyframes that are more evenly distributed across the sequence.
        We don't take the physical distance of the hand between frames into account.
        We simply want a fixed number of frames to send to the model.
        """
        
        if (self.target_len <= 2):
            raise Exception("stop it")
        seq_new = self.remove_outliers(seq)
        if len(seq_new) < self.target_len:
            seq_new = self.pad_sequences_of_landmarks(seq_new)
        print(len(seq_new))
        random.seed(42)
        res = [seq_new[0]]
        idxs = sorted(random.sample(range(1,len(seq_new)-1), k=self.target_len-2))
        for index in idxs:
            res.append(seq_new[index])
        res.append(seq_new[-1])
        return res
    
    def extract_keyframes(self, seq: list[np.ndarray[Any, np.dtype[np.float32]]]) -> np.ndarray:
        if self.target_len > len(seq): 
            raise ValueError(f"Tried creating {self.target_len} keyframes for a sequence of {len(seq)}")
        if len(seq) / self.target_len < 2:
            return np.array(random.sample(seq, self.target_len))
        seq = self.remove_outliers(seq)
        print("SEQ LENGTH ", len(seq))
        # compute displacements between neighboring frames
        displacements: list[float] = [0]
        last_pos = self.landmarks_to_single_mean(seq[0])

        for i in range(1, len(seq)):
            pos = self.landmarks_to_single_mean(seq[i])
            displacements.append(self._distance(last_pos, pos))
            last_pos = pos

        total = sum(displacements)
        # this is how often a key frame should be placed
        interval = total / (self.target_len - 1)
        print("INTERVAL: ", interval)
        running_sum = 0
        toReturn = [seq[0]]
        for i in range(1, len(seq)):
            running_sum += displacements[i]
            print("running_sum ", running_sum)
            print("displacements[i] ", displacements[i])
            if running_sum >= interval:
                # the total displacement up to this point is enough to consider this frame key
                toReturn.append(seq[i])
                print("SEQ[I] ", seq[i])
                running_sum = 0
        print("TORETURN LENGTH: ", len(toReturn))
        if len(toReturn) < self.target_len:
            toReturn.append(seq[len(seq)-1])
            
        if len(toReturn) < self.target_len:
            raise Exception(f"expected {self.target_len} but got {len(toReturn)}.. not enough keyframes >:(")
                
        return np.array(toReturn)
    def frame_to_single_mean(self,frame:list[float],num_landmarks=21,dimensions=3):
        np_landmarks = np.array([coord for coord in frame])
        return self.landmarks_to_single_mean(np_landmarks,num_landmarks,dimensions)

    def landmarks_to_single_mean(self, landmarks: np.ndarray,num_landmarks=21,dimensions=3):
        reshaped = landmarks.reshape((-1,num_landmarks,dimensions))
        mean = np.mean(reshaped, axis=1).flatten()
        return mean

    def is_within_boundaries(self, 
                             prev_mean:Union[float, np.float32], cur_mean:Union[float, np.float32]
                             ) -> Union[bool, np.bool_]:
        boundary = self.boundary / 2
        if self.bertram_mode:
            diff = abs(prev_mean - cur_mean)
            return diff <= boundary
        else:
            upper = prev_mean + boundary
            lower = prev_mean - boundary

            return lower <= cur_mean <= upper

    def create_trajectory_element(self, prev:Tuple[float,float,float], cur:Tuple[float,float,float],dimensions=DIMENSIONS) -> trajectory_element:
        directions: list[direction] = []
        if (len(prev) < dimensions) or (len(cur) < dimensions):
            raise ValueError("You provided a list with less than 3 elements \n prev: {prev}\n curr: {cur}")
        
        for dim in range(dimensions):
            mean_p_dim = prev[dim]
            mean_c_dim = cur[dim]

            if self.is_within_boundaries(mean_p_dim, mean_c_dim):
                directions.append(direction.STATIONARY)
            else:
                directions.append(direction.UP if mean_c_dim > mean_p_dim else direction.DOWN)

        return trajectory_element(*directions)

    def make_trajectory(self,image_landmark_sequence: np.ndarray) -> trajectory:
        """Creates a trajectory(representing a gesture ) from a sequence of landmarks.

            :param image_landmark_sequence: list of pictures, that have been reduced to landmarks
                np.array(np.array(landmarks)), where each landmark has 3 float coordinates (x,y,z).
                
            :return: A trajectory object.
        """
        res: list[trajectory_element] = []

        previous = image_landmark_sequence[0]
        for current in image_landmark_sequence[1:]:
            mean_prev = self.landmarks_to_single_mean(previous)
            mean_cur = self.landmarks_to_single_mean(current)
            
            next_elm_of_trajectory = self.create_trajectory_element(mean_prev, mean_cur)
            res.append(next_elm_of_trajectory)
            previous = current

        return trajectory(res)

    def make_trajectory_values(self, trj: trajectory) -> np.ndarray:
        return np.array([(te.x.value, te.y.value, te.z.value) for te in trj.directions]).flatten()

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
    
    #landmarks = fist_down_seq
    #reshaped = landmarks.reshape((-1, 21, 3))
    #print(landmarks)
    #print(np.mean(reshaped, axis=1))
    #mean = np.mean(reshaped, axis = 1)

    #print("mean HERE: ", mean.flatten())
    gen = TrajectoryBuilder()
    traj = gen.make_trajectory(fist_down_seq)
    print(traj)
    for elm in traj.directions:
        print(f"x:{elm.x}, y: {elm.y}, z: {elm.z}")


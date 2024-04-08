
from ast import Pass, Raise
from dataclasses import dataclass
from turtle import position
from typing import Set, Tuple
import numpy as np
from sympy import false
from sign.training.load_data.HolisticCsvReader import HolisticFrame as hf, HoslisticCsvReader, holistic_keys as hk
from pathlib import Path

FRAME_AMOUNT = 12 # How many frames do we want? Depends on the precision we want?

@dataclass
class MeanFrame(hf):
    pass


def can_detect_a_hand(frame:hf):
    """
    Given a HolisticFrame checks if it can detect either a left or a right hand.
    
    """
    left_hand = frame[hk.LEFT_HAND]
    right_hand = frame[hk.RIGHT_HAND]
    if len(left_hand) < 0 and len(right_hand) < 0:
        return False
    return True
    

def landmarks_to_single_mean(float_landmarks:list[float]) -> Tuple[float,float,float]:
    """
    Reduces all values on an axis to a single mean value.
    Returns a tuple of mean(x,y,z)
    
    """
    landmarks = np.array(float_landmarks,dtype=np.float32)
    reshaped = landmarks.reshape((-1,len(float_landmarks),3))
    np_array:np.ndarray =  np.mean(reshaped, axis=1).flatten() 
    return (np_array[0],np_array[1],np_array[2])

def raw_frame_to_mean_values(frame:hf):
    """
    Given a HolisticFrame finds all mean values for all body parts.
    
    Returns MeanFrame. Why is it so mean???
    
    """
    mean_body_landmarks = landmarks_to_single_mean(frame.data[hk.POSE])
    mean_right_hand_landmarks = landmarks_to_single_mean(frame.data[hk.RIGHT_HAND])
    mean_left_hand_landmarks = landmarks_to_single_mean(frame.data[hk.LEFT_HAND])

    return MeanFrame(
        frame.id,{
        hk.POSE: [*mean_body_landmarks],
        hk.RIGHT_HAND: [*mean_right_hand_landmarks],
        hk.LEFT_HAND: [*mean_left_hand_landmarks]
    })

def can_detect_body(frame:hf):
    """
    Checks if a frame contains a body also called HolisticKeys.POSE. 
    """
    pose = frame[hk.POSE]
    if len(pose) < 0:
        return False
    return True

def mean_frame_distance(_from:MeanFrame,_to:MeanFrame,key:hk):
    """
    calculate the frame distance between a body part.
    
    """
    from_body_part = _from[key]
    to_body_part = _to[key]
    if len(from_body_part) < 1 or len(to_body_part) < 1:
        return None #TODO: FIX THIS This is wrong!
    return float(np.linalg.norm(np.array(from_body_part) - np.array(to_body_part)))


def check_minimum_dist(prev_frame:MeanFrame,current_frame:MeanFrame,next_frame:MeanFrame):
    """
    Given 3 frames, prev,current,next. 
    We check if the current frame is an outlier.
    We do this for 3 body parts (HolisticKeys.POSE,HolisticKeys.LEFT_HAND,HolisticKeys.RIGHT_HAND)
    If any body part is an outlier we discard the frame.
    TODO: This might be too extreme. We are also too strict on right and left hands as we often won't have both hands and this is fine.
    
    """
    min_body = min(mean_frame_distance(prev_frame, current_frame,hk.POSE), mean_frame_distance(current_frame, next_frame,hk.POSE)) > mean_frame_distance(prev_frame, next_frame,hk.POSE)
    
    min_left_hand = min(mean_frame_distance(prev_frame, current_frame,hk.LEFT_HAND), mean_frame_distance(current_frame, next_frame,hk.LEFT_HAND)) > mean_frame_distance(prev_frame, next_frame,hk.LEFT_HAND)
    
    min_right_hand = min(mean_frame_distance(prev_frame, current_frame,hk.RIGHT_HAND), mean_frame_distance(current_frame, next_frame,hk.RIGHT_HAND)) > mean_frame_distance(prev_frame, next_frame,hk.RIGHT_HAND)
    return min_body or min_left_hand or min_right_hand
                    

def extract_indices_for_outliers(video: list[hf], old_indices: list[int]):
    """
    TODO: Might be good to make a trajectory here and then pass it with the indices.
    
    Throws an error if there are more indices than frames.
    
    Finds all outliers for a list of HolisticFrames and a set of indices.
    
    Returns a new list of indices with outliers removed.
    
    """
    if len(video) < len(old_indices):
        raise ValueError("Length of indices are larger than length of frames.")
    
    
    mean_frames:list[MeanFrame] = []
    for i in old_indices:
        mean_frames.append(raw_frame_to_mean_values(video[i]))
        
    # non_outlier_frames = [mean_frames[0]] # If we decide that we also want to make trajectories
    new_indices:list[int] = [old_indices[0]]
    for i in range(1, len(mean_frames) - 1):
        if check_minimum_dist(mean_frames[i-1],mean_frames[i],mean_frames[i+1]):
            # outlier
            print("REMOVING OUTLIER")
            continue
        new_indices[i]
        # non_outlier_frames.append(mean_frames[i]) # If we decide that we also want to make trajectories

    # non_outlier_frames.append(mean_frames[-1]) # If we decide that we also want to make trajectories
    new_indices.append(old_indices[-1])
    return new_indices

def extract_indices_for_frames_with_body_and_hands(video:list[hf]):
    """
    Given a list of HolisticFrames 
    Returns a list of indices List[int] where each index match all frames where both a HolisticKeys.LEFT_HAND or HolisticKeys.RIGHT_HAND and a HolisticKeys.Pose is found.
    
    """
    extracted_indices:list[int] = []
    for idx,frame in enumerate(video):
        if not can_detect_a_hand(frame) and not can_detect_body(frame):
            continue
        extracted_indices.append(idx)
    return extracted_indices

def frame_mask(video: list[hf],indices:list[int]):
    """
    Bit mask for a list of HolisticFrames that given an array of indices, will return all frames that matches the indices specified in the list.
    
    Throws an error if there are more indices than frames.
    
    Returns an list of HolisticFrames.
    """
    if len(video) < len(indices):
        raise ValueError("Length of indices are larger than length of frames.")
    
    extracted_frames: list[hf] = []
    for index in indices:
        extracted_frames.append(video[index])
    return extracted_frames

def process_video(video: list[hf]):
    """
    Processes a list of holisticframes 
    (in another words a list of frames with landmarks from 
    the holistic model from media pipe.)
    
    Returns whether it succeded or not.
    """
    body_hands_indices = extract_indices_for_frames_with_body_and_hands(video)
    if len(body_hands_indices) < 1:
        return False
    good_indices = extract_indices_for_outliers(video,body_hands_indices)
    good_frames = frame_mask(video,good_indices)
    if not is_frames_evenly_spaces(frame):
        continue # discard_frame(frame)
    amount_of_frames = count_frames_with_hands_and_body(frame)
        
    if amount_of_frames < FRAME_AMOUNT:
        pad_frames(frame)
    else if amount_of_frames > FRAME_AMOUNT:
        extract_keyframes(frame)
        
    save_to_csv()
    return True
            
        
    


if __name__ == "__main__":
    # PARSE COMMAND LINE ARGS
    # SHOULD HAVE CSV PATH
    path = Path("")
    _HolisticCsvReader = HoslisticCsvReader()
    
    frame_generator = _HolisticCsvReader.frame_generator(path)
    for frame in frame_generator:
        previous_id = 0
        frames_for_video: list[hf] = []
        while frame.id == previous_id:
            frames_for_video.append(frame)
        process_video(frames_for_video)
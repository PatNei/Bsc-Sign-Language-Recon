
import argparse
import csv
from dataclasses import dataclass
from datetime import date
import datetime
from enum import StrEnum
import os
import random
from typing import Generator, Tuple
import numpy as np
from dynamic_signs.csv_reader import MultiHandStaticFrame
from sign.skewness_algorithm import is_it_evenly_distributed
from sign.training.landmark_extraction.HolisticPiper import HolisticPiper
from sign.training.load_data.HolisticCsvReader import HolisticFrame as hf, HoslisticCsvReader, holistic_keys as hk
from pathlib import Path
import logging

from sign.trajectory import TrajectoryBuilder, direction, trajectory_element
# Setup Logging
LOG_PATH = Path().cwd().joinpath("logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
logging.basicConfig(filename=LOG_PATH.joinpath(f"{current_time}.log"),level=logging.INFO)

FRAME_AMOUNT = 12 # How many frames do we want? Depends on the precision we want?

@dataclass
class MeanFrame(hf):
    pass

class coordinate(StrEnum):
    x = "x"
    y = "y"
    z = "z"

def can_detect_body_part(frame:MeanFrame,key: hk):
    body_part = frame[key]
    return len(body_part) > 0

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
    
    TODO: Verify that this is actually correct (especially in the reshape function, I.E should it be divided by three).
    
    
    """
    length_landmarks = len(float_landmarks)
    if length_landmarks < 3:
        raise ValueError("Length of landmark list is less than 3, we can't reshape")
    landmarks = np.array(float_landmarks,dtype=np.float32)
    reshaped = landmarks.reshape((-1,int(len(float_landmarks)/3),3))
    np_array:np.ndarray =  np.mean(reshaped, axis=1).flatten() 
    return (np_array[0],np_array[1],np_array[2])

def raw_frame_to_mean_values(frame:hf):
    """
    Given a HolisticFrame finds all mean values for all body parts.
    
    Returns MeanFrame. Why is it so mean???
    
    TODO: Is exceptions the best way to handle this ?
    TODO: Do we really want to use the mean for arms ? (pose / body)
    TODO: We take all values for the pose (even the ones media pipe predicts)
    
    """
    mean_body_landmarks:Tuple[float,float,float] | None = None
    mean_right_hand_landmarks:Tuple[float,float,float] | None = None
    mean_left_hand_landmarks:Tuple[float,float,float] | None = None
    try:
        mean_body_landmarks = landmarks_to_single_mean(frame.data[hk.POSE])
    except:
        pass
    try:
        mean_right_hand_landmarks = landmarks_to_single_mean(frame.data[hk.RIGHT_HAND])
    except:
        pass
    try: 
        mean_left_hand_landmarks = landmarks_to_single_mean(frame.data[hk.LEFT_HAND])
    except:
        pass 

    return MeanFrame(
        frame.id,{
        hk.POSE: [*mean_body_landmarks] if mean_body_landmarks is not None else [],
        hk.RIGHT_HAND: [*mean_right_hand_landmarks] if mean_right_hand_landmarks is not None else [],
        hk.LEFT_HAND: [*mean_left_hand_landmarks] if mean_left_hand_landmarks is not None else []
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
    if not can_detect_body_part(_from,key) or not can_detect_body_part(_to,key):
        raise ValueError("Can't detect body part")
    from_body_part = _from[key]
    to_body_part = _to[key]
    return float(np.linalg.norm(np.array(from_body_part) - np.array(to_body_part)))

def is_it_an_outlier(prev_frame:MeanFrame,current_frame:MeanFrame,next_frame:MeanFrame,key:hk):
    try:
        return min(mean_frame_distance(prev_frame, current_frame,key), mean_frame_distance(current_frame, next_frame,key)) > mean_frame_distance(prev_frame, next_frame,key)
    except:
        return None
        


def check_for_outlier(prev_frame:MeanFrame,current_frame:MeanFrame,next_frame:MeanFrame):
    """
    Given 3 frames, prev,current,next. 
    We check if the current frame is an outlier.
    We do this for 3 body parts (HolisticKeys.POSE,HolisticKeys.LEFT_HAND,HolisticKeys.RIGHT_HAND)
    If any body part is an outlier we discard the frame.
    
    """
    # min_body = is_it_an_outlier(prev_frame,current_frame,next_frame,hk.POSE)
    min_left_hand = is_it_an_outlier(prev_frame,current_frame,next_frame,hk.LEFT_HAND)
    min_right_hand = is_it_an_outlier(prev_frame,current_frame,next_frame,hk.RIGHT_HAND)
        
    if min_left_hand is None and min_right_hand is None: 
        # If both hands are not present then it is an outlier
        return True
    
    #if min_body: 
        # If the dist is wrong for the body then it is an outlier
    #    return True 
    
    if min_left_hand is not None and min_left_hand: 
        # If the left hand is detected but the dist is wrong then it is an outlier
        return True 
    
    if min_right_hand is not None and min_right_hand: 
        # If the right hand is detected but the dist is wrong then it is an outlier
        return True
    
    return False # if it passes all checks then it is not an outlier.
        
                    

def extract_indices_without_outliers(video: list[hf]):
    """
    Throws an error if there are more indices than frames.
    
    Finds all outliers for a list of HolisticFrames and a set of indices.
    
    Returns a new list of indices with outliers removed.
    
    TODO: Might be good to make a trajectory here and then pass it with the indices.
    TODO: Tobias wants to make an algorithm that checks if the first or last index is an outlier.
    """
    mean_frames:list[MeanFrame] = []
    for frame in video:
        mean_frames.append(raw_frame_to_mean_values(frame))
        
    # non_outlier_frames = [mean_frames[0]] # If we decide that we also want to make trajectories
    new_indices:list[int] = [0]
    for i in range(1, len(mean_frames) - 1):
        if check_for_outlier(mean_frames[i-1],mean_frames[i],mean_frames[i+1]):
            # outlier
            continue
        new_indices.append(i)
        # non_outlier_frames.append(mean_frames[i]) # If we decide that we also want to make trajectories

    # non_outlier_frames.append(mean_frames[-1]) # If we decide that we also want to make trajectories
    new_indices.append(len(mean_frames)-1)
    return new_indices

def extract_indices_for_frames_with_body_and_hands(video:list[hf]):
    """
    Given a list of HolisticFrames 
    Returns a list of indices List[int] where each index match all frames where both a HolisticKeys.LEFT_HAND or HolisticKeys.RIGHT_HAND and a HolisticKeys.Pose is found.
    """
    
    extracted_indices:list[int] = []
    for idx,frame in enumerate(video):
        if not can_detect_a_hand(frame) and not can_detect_body(frame): # Strictness parameter
            logging.info("discarded because there are not enough frames")
            continue
        extracted_indices.append(idx)
    return extracted_indices

def frame_mask(video: list[hf],indices:list[int]):
    """
    Bit mask for a list of HolisticFrames that given an array of indices, will return all frames that matches the indices specified in the list.
    
    Throws an error if there are more indices than frames.
    
    Returns a list of HolisticFrames.
    """
    if len(video) < len(indices):
        raise ValueError("Length of indices are larger than length of frames.")
    
    extracted_frames: list[hf] = []
    for index in indices:
        extracted_frames.append(video[index])
    return extracted_frames

def extract_keyframes(video:list[hf]):
    if (len(video) <= 2 or FRAME_AMOUNT <= 2):
        raise Exception("stop it")
    random.seed(42)
    res = [video[0]]
    idxs = sorted(random.sample(range(1,len(video)-1), k=FRAME_AMOUNT-2))
    for index in idxs:
        res.append(video[index])
    res.append(video[-1])
    return res

def pad_frames():
    pass

def calculate_trajectories(hand_landmarks:list[list[float]]):
    """
    Given a list of a list of floats (a video or a list of frames), extract landmarks and convert them to a trajectory.
    
    """
    if len(hand_landmarks) < 3:
        raise ValueError("You parsed a list which was less than 3 frames long")
    
    bob = TrajectoryBuilder()
    hand_trajectories: list[trajectory_element] = []
    for frame in hand_landmarks:
        prev_frame = frame[:3] # has the form x,y,z
        for index in range(3,len(frame)-3,3):
            current_frame = frame[index:index+3] # has the form x,y,z
            trajectory = bob.create_trajectory_element(np.array(prev_frame),np.array(current_frame))
            hand_trajectories.append(trajectory)
            prev_frame = current_frame
        last_frame = frame[len(frame)-3:] # has the form x,y,z
        trajectory = bob.create_trajectory_element(np.array(prev_frame),np.array(last_frame))
        hand_trajectories.append(trajectory)
    return hand_trajectories
    

def calculate_movement_score(trajectories:list[trajectory_element]):
    """
    Calculates the movement for a trajectory
    it works by taking the direction of movement for x,y,z and accumulates the amount of occurences that are not equal to direction.STATIONARY.
    Finally it returns the sum of x,y,z scores.
    
    """
    x_score = 0
    y_score = 0
    z_score = 0
    for trajectory in trajectories:
        if trajectory.x != direction.STATIONARY:
            x_score += 1
        if trajectory.y != direction.STATIONARY:
            y_score += 1
        if trajectory.z != direction.STATIONARY:
            z_score += 1
    return x_score + y_score + z_score



def which_hand_has_most_movement(video:list[MultiHandStaticFrame]):
    """
    Takes a list of MultiHandStaticFrames, finds their trajectory and tries to predict which hand has most movement. 
    It defaults to the left hand in case of both hands have equal movement.
    
    """
    
    left_hand_trajectories: list[trajectory_element] = []
    right_hand_trajectories: list[trajectory_element] = []
    
    left_hand_landmarks:list[list[float]] = []
    right_hand_landmarks:list[list[float]] = []
    
    for frame in video:
        _left_hand_landmarks,_right_hand_landmarks = frame.get_landmarks() 
        if _left_hand_landmarks: left_hand_landmarks.append(_left_hand_landmarks)
        if _right_hand_landmarks: right_hand_landmarks.append(_right_hand_landmarks)
    
    if left_hand_landmarks:
        left_hand_trajectories = calculate_trajectories(left_hand_landmarks)
    if right_hand_landmarks:
        right_hand_trajectories = calculate_trajectories(right_hand_landmarks)

    left_hand_score = calculate_movement_score(left_hand_trajectories)
    right_hand_score = calculate_movement_score(right_hand_trajectories)
    
    if left_hand_score < right_hand_score:
        return hk.RIGHT_HAND
    
    return hk.LEFT_HAND

def process_video(video: list[hf]):
    """
    Processes a list of holisticframes (in another words a list of frames with landmarks from 
    the holistic model from media pipe.)
    
    Returns a list of frames (a video) and None if it fails.
    TODO: We might actually have to pad otherwise we loose to much data.
    """
    
    indices_no_outliers = extract_indices_without_outliers(video) # Filter frames that contain outliers
    number_of_outliers = len(video)-len(indices_no_outliers)
    #print("We removed",len(indices_no_outliers),"out of",len(video),"frames")
    if (number_of_outliers / len(video) > 0.40):
        logging.info(f"Video with id {video[0].id} has more than 40 % outliers {number_of_outliers} out of {len(video)}")
    filtered_body_hands_outliers_indices = extract_indices_for_frames_with_body_and_hands([video[index] for index in indices_no_outliers])
    if len(filtered_body_hands_outliers_indices) < 1:
        return None
    
    if not is_it_evenly_distributed(video,filtered_body_hands_outliers_indices):
        return None # discard video
    
    final_frames = frame_mask(video,filtered_body_hands_outliers_indices)
    if len(filtered_body_hands_outliers_indices) < FRAME_AMOUNT:
        logging.info(f"video with id: {video[0].id} discarded because there are not enough frames")
        return None # Discard video
        # final_frames = pad_frames(frame) 
    elif len(filtered_body_hands_outliers_indices) > FRAME_AMOUNT:
        final_frames = extract_keyframes(final_frames)
    return final_frames


def save_list_of_HolisticVideos_to_csv(path:Path, videos:list[list[hf]]):
    """
    The new name of the file name will become f"proccessed_{filename}"
    and it will be saved in a folder called "processed" relative to the current path.
    
    """
    file_name = Path(f"proccessed_{path.name}")
    file_path = path.parent.absolute()
    file_path = file_path.joinpath("./processed")
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    processed_file_path = Path.joinpath(file_path,file_name)
    if not os.path.exists(processed_file_path):
        with open(processed_file_path, 'w'): pass
        
    with open(processed_file_path,"w") as csvfile:
        _writer = csv.writer(csvfile,delimiter=',')
        for video in videos:
            for frame in video:
                for body_part in hk:
                    frame_coordinates = frame[body_part] # we do this because python linting is actually stupid
                    coordinates = frame_coordinates if frame_coordinates is not None else []
                    _writer.writerow([body_part,frame.id,*coordinates])
                
def convert_list_of_frames_to_list_of_videos(frame_generator:Generator[hf, None, None]):
    videos:list[list[hf]] = []
    previous_id = None
    frames_for_single_video: list[hf] = []
    for frame in frame_generator:
        if previous_id is None:
            frames_for_single_video.append(frame)
            previous_id = frame.id
            continue
        if frame.id == previous_id:
            frames_for_single_video.append(frame)
            continue        
        previous_id = frame.id
        videos.append(frames_for_single_video)
        frames_for_single_video = []
    videos.append(frames_for_single_video)
    return videos
        

def filter_holistic_csv(path:Path):
    """
    Runs our pipeine (process_video()) for a given csv and returns a filtered list of videoes
    
    """
    processed_videos:list[list[hf]]  = []
    _HolisticCsvReader = HoslisticCsvReader()
    frame_generator = _HolisticCsvReader.frame_generator(path)
    list_of_videos = convert_list_of_frames_to_list_of_videos(frame_generator)
    discard_videos = 0
    good_videos = 0
    for video in list_of_videos:
        processed_video = process_video(video)
        # print(len(video)/len(processed_video))
        if processed_video is None:
            discard_videos += 1
            continue
        good_videos += 1
        processed_videos.append(processed_video)
    logging.info(f"Discarded Videos: {discard_videos} Good Videoes: {good_videos} Total videos: {len(list_of_videos)}")
    return processed_videos
    
    
def process_csv():
    parser = argparse.ArgumentParser(
                    prog='ProcessHolisticCSV',
                    description='This program processes a csv of holistic frames',
                    epilog='Good Luck 🤡🤡🤡🤡🤡🤡🤡🤡')
    parser.add_argument("filename",help="Filename for the csv")
    _args = parser.parse_args()
    path = Path(_args.filename)
    if not path.exists():
        exit(1)
    if path.is_dir(): # Processes all .csv in a directory
        for file in os.listdir(path):
            file_path = path.joinpath(file)
            if not file_path.is_file():
                continue
            if not file_path.suffix == ".csv":
                continue
            processed_videos = filter_holistic_csv(file_path)
            save_list_of_HolisticVideos_to_csv(file_path,processed_videos)
        exit()
    
    if not path.is_file():
        exit(1)
    if not path.suffix == ".csv":
        exit(1)
    processed_videos = filter_holistic_csv(path) # process a single file
    save_list_of_HolisticVideos_to_csv(path,processed_videos)
    exit()

if __name__ == "__main__":
    process_csv()
    
    

        
        
        
        
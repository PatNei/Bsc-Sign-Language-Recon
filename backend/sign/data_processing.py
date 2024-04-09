
import argparse
import csv
from dataclasses import dataclass
import os
import random
from typing import Generator, Tuple
import numpy as np
from sign.skewness_algorithm import is_it_evenly_distributed
from sign.training.landmark_extraction.HolisticPiper import HolisticPiper
from sign.training.load_data.HolisticCsvReader import HolisticFrame as hf, HoslisticCsvReader, holistic_keys as hk
from pathlib import Path

FRAME_AMOUNT = 12 # How many frames do we want? Depends on the precision we want?

@dataclass
class MeanFrame(hf):
    pass

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
    if not can_detect_body_part(_from,key) or not can_detect_body_part(_to,key):
        raise ValueError("Can't detect body part")
    from_body_part = _from[key]
    to_body_part = _to[key]
    return float(np.linalg.norm(np.array(from_body_part) - np.array(to_body_part)))

def outlier_calculation(prev_frame:MeanFrame,current_frame:MeanFrame,next_frame:MeanFrame,key:hk):
    return min(mean_frame_distance(prev_frame, current_frame,key), mean_frame_distance(current_frame, next_frame,key)) > mean_frame_distance(prev_frame, next_frame,key)


def check_for_outlier(prev_frame:MeanFrame,current_frame:MeanFrame,next_frame:MeanFrame):
    """
    Given 3 frames, prev,current,next. 
    We check if the current frame is an outlier.
    We do this for 3 body parts (HolisticKeys.POSE,HolisticKeys.LEFT_HAND,HolisticKeys.RIGHT_HAND)
    If any body part is an outlier we discard the frame.
    
    """
    min_body = outlier_calculation(prev_frame,current_frame,next_frame,hk.POSE)
    
    min_left_hand = None
    try: 
         min_left_hand = outlier_calculation(prev_frame,current_frame,next_frame,hk.LEFT_HAND)
    except:
        min_left_hand = None

    min_right_hand = None
    try:
        min_right_hand = outlier_calculation(prev_frame,current_frame,next_frame,hk.RIGHT_HAND)
    except:
        min_right_hand = None
        
    if min_left_hand is None and min_right_hand is None: 
        # If both hands are not present then it is an outlier
        return True
    
    if min_body: 
        # If the dist is wrong for the body then it is an outlier
        return True 
    
    if min_left_hand is not None and min_left_hand: 
        # If the left hand is detected but the dist is wrong then it is an outlier
        return True 
    
    if min_right_hand is not None and min_right_hand: 
        # If the right hand is detected but the dist is wrong then it is an outlier
        return True
    
    return False # if it passes all checks then it is not an outlier.
        
                    

def extract_indices_without_outliers(video: list[hf], old_indices: list[int]):
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
        if check_for_outlier(mean_frames[i-1],mean_frames[i],mean_frames[i+1]):
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

def calculate_trajectories(video:list[hf]):
    " oh no"
    pass

def process_video(video: list[hf]):
    """
    Processes a list of holisticframes (in another words a list of frames with landmarks from 
    the holistic model from media pipe.)
    
    Returns a list of frames (a video) and None if it fails.
    """
    body_hands_indices = extract_indices_for_frames_with_body_and_hands(video)

    if len(body_hands_indices) < 1:
        return None
    indices_no_outliers = extract_indices_without_outliers(video,body_hands_indices)
    if not is_it_evenly_distributed(video,indices_no_outliers):
        return None # discard video
    
    final_frames = frame_mask(video,indices_no_outliers)
    if len(indices_no_outliers) < FRAME_AMOUNT:
        return None
        # final_frames = pad_frames(frame) 
    elif len(indices_no_outliers) > FRAME_AMOUNT:
        final_frames = extract_keyframes(final_frames)
    return final_frames


def save_list_of_HolisticVideos_to_csv(path:Path, videos:list[list[hf]]):
    """
    The new name of the file name will become f"proccessed_{filename}"
    
    """
    file_name = Path(f"proccessed_{path.name}")
    file_path = path.parent.absolute()
    full_path = Path.joinpath(file_path,file_name)
    if not os.path.exists(full_path):
        with open(full_path, 'w'): pass
        
    with open(full_path) as csvfile:
        _writer = csv.writer(csvfile,delimiter=',')
        for video in videos:
            for frame in video:
                _writer.writerow([hk.FACE,frame.id,frame[hk.FACE]])
                _writer.writerow([hk.LEFT_HAND,frame.id,frame[hk.LEFT_HAND]])
                _writer.writerow([hk.POSE,frame.id,frame[hk.POSE]])
                _writer.writerow([hk.POSE_WORLD,frame.id])
                _writer.writerow([hk.RIGHT_HAND,frame.id,frame[hk.RIGHT_HAND]])
                _writer.writerow([hk.SEGMENTATION_MASK,frame.id])
                
def convert_list_of_frames_to_list_of_videos(frame_generator:Generator[hf, None, None]):
    videos:list[list[hf]] = []
    previous_id = 0
    frames_for_single_video: list[hf] = []
    for frame in frame_generator:
        if frame.id == previous_id:
            frames_for_single_video.append(frame)
            continue        
        previous_id = frame.id
        videos.append(frames_for_single_video)
        frames_for_single_video = []
    return videos
        

def filter_holistic_csv(path:Path):
    """
    Runs our pipeine (process_video()) for a given csv and returns a filtered list of videoes
    
    """
    processed_videos:list[list[hf]]  = []
    _HolisticCsvReader = HoslisticCsvReader()
    frame_generator = _HolisticCsvReader.frame_generator(path)
    list_of_videos = convert_list_of_frames_to_list_of_videos(frame_generator)
    
    for video in list_of_videos:
        processed_video = process_video(video)
        if processed_video is None:
            continue
        processed_videos.append(processed_video)
    return processed_videos
    
    
def process_csv():
    parser = argparse.ArgumentParser(
                    prog='ProcessHolisticCSV',
                    description='This program processes a csv of holistic frames',
                    epilog='Good Luck 🤡🤡🤡🤡🤡🤡🤡🤡')
    parser.add_argument("filename",help="Filename for the csv")
    _args = parser.parse_args()
    path = Path(_args.filename)
    if not path.is_file():
        exit(1)
    if not path.suffix == ".csv":
        exit(1)
    processed_videos = filter_holistic_csv(path)
    save_list_of_HolisticVideos_to_csv(path,processed_videos)
    exit()

if __name__ == "__main__":
    process_csv()
    
    

        
        
        
        
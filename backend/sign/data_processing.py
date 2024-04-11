
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
    TODO: Might be good to make a trajectory here and then pass it with the indices.
    x
    Throws an error if there are more indices than frames.
    
    Finds all outliers for a list of HolisticFrames and a set of indices.
    
    Returns a new list of indices with outliers removed.
    
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
            print("discarded because there are not enough frames")
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
    TODO: We might actually have to pad otherwise we loose to much data.
    """
    
    indices_no_outliers = extract_indices_without_outliers(video) # Filter frames that contain outliers
    #print("We removed",len(indices_no_outliers),"out of",len(video),"frames")
    if (len(indices_no_outliers) / len(video) > 0.40):
        print("Video with id",video[0].id,"has more than 40 % outliers" , len(video)-len(indices_no_outliers),"out of",len(video))
    filtered_body_hands_outliers_indices = extract_indices_for_frames_with_body_and_hands([video[index] for index in indices_no_outliers])
    if len(filtered_body_hands_outliers_indices) < 1:
        return None
    
    if not is_it_evenly_distributed(video,filtered_body_hands_outliers_indices):
        return None # discard video
    
    final_frames = frame_mask(video,filtered_body_hands_outliers_indices)
    if len(filtered_body_hands_outliers_indices) < FRAME_AMOUNT:
        print("discarded because there are not enough frames")
        return None # Discard video
        # final_frames = pad_frames(frame) 
    elif len(filtered_body_hands_outliers_indices) > FRAME_AMOUNT:
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
        
    with open(full_path,"w") as csvfile:
        _writer = csv.writer(csvfile,delimiter=',')
        for video in videos:
            for frame in video:
                for body_part in hk:
                    _writer.writerow([body_part,frame.id,frame[body_part]])
                
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
    print(discard_videos,good_videos)
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
    
    

        
        
        
        
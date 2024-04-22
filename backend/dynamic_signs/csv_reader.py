import csv
from dataclasses import dataclass
from typing import Literal, Tuple
from sign.CONST import MEDIAPIPER_VERSION_2

import numpy as np

LENGTH_LANDMARKS = 21
LENGTH_HANDID_AND_LANDMARKS = 1 + LENGTH_LANDMARKS #1 for hand_id, 21 for the amount of tuple
EMPTY_ID = "___empty-id___"
EMPTY_LABEL = "___empty-label___"

@dataclass
class MultiHandStaticFrame:
    """Keeps all the landmarks as a single list.
    IMPORTANT: The list will always be ordered as 63 landmarks for hand_0,
    then 63 landmarks for hand_1, IFF. there are landmarks for both hands.
    Otherwise the list will only contain the 63 landmarks
    """
    present_hands: Literal[0] | Literal[1] | Tuple[Literal[0], Literal[1]]
    landmarks: list[float]

    def get_landmarks(self) -> Tuple[list[float] | None, list[float] | None]:
        if isinstance(self.present_hands, tuple):
            return self.landmarks[:LENGTH_LANDMARKS * 3], self.landmarks[LENGTH_LANDMARKS*3:]
        elif self.present_hands == 0:
            return self.landmarks, None
        elif self.present_hands == 1:
            return None, self.landmarks
        return None,None

class csv_reader:
    def __init__(self):
        pass
    
    def extract_landmarks(self,path:str) -> dict[str, dict[int, list[float]]]:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            landmarks: dict[str, dict[int, list[float]]] = {}
            id = None
            new_video = False
            parsed_landmarks: list[float] = []
            for row in reader:
                new_video = int(row[1]) != id
                id = int(row[1])
                label = row[0]
                for landmark in row[2:-1]:
                    coords = np.fromstring(landmark.strip(",").strip("[").strip("]"), dtype=np.float32, sep=",")
                    for coord in coords:
                        parsed_landmarks.append(coord)
                if new_video:
                    existing = landmarks.get(label)
                    if existing is not None:
                        existing[id] = parsed_landmarks
                    else:
                        landmarks[label] = {id:parsed_landmarks}
                else:
                    existing = landmarks.get(label)
                    if existing is not None:
                        existing[id].extend(parsed_landmarks)
                    else:
                        landmarks[label] = {id:parsed_landmarks}
                parsed_landmarks = []
            return landmarks
        
    def extract_two_handed_landmarks(self, 
                                     path:str, 
                                     id_counter_marker = "~") -> dict[str, dict[str, list[MultiHandStaticFrame]]]:
        """
        Like extract_landmarks, it extracts all the data from a CSV.
        
        Returns
        -------
        A dictionary from label -> dictionary of sequence_id -> list[MultiHandStaticFrame]
            The MultiHandStaticFrame class remembers which hands were present in the data. Useful for data cleanup later?
        """
        def parse_tuple_list_of_xyz(row) -> np.ndarray:
            return np.fromstring(row.strip(",").strip("[").strip("]"), dtype=np.float32, sep=",")

        def extract_hand_id_and_landmarks(row:list[str], i:int) -> Tuple[int,list[float]]:
            xyz_tuples = [x for x in row[i*LENGTH_HANDID_AND_LANDMARKS+1:(i+1)*LENGTH_HANDID_AND_LANDMARKS]]
            xyz_parsed_and_flattened = sum([list(parse_tuple_list_of_xyz(xyz_tuple)) for xyz_tuple in xyz_tuples], []) 
            hand_id = int(row[i * LENGTH_HANDID_AND_LANDMARKS])
            return hand_id, xyz_parsed_and_flattened

        counter = 0
        with open(path, 'r') as f:
            reader = csv.reader(f)
            res: dict[str, dict[str, list[MultiHandStaticFrame]]] = {}

            prev_id = EMPTY_ID
            label = EMPTY_LABEL
            
            cur_sequence: list[MultiHandStaticFrame] = []
            for line, row in enumerate(reader):
                prev_label = label
                label = row[0]
                if label not in res:
                    res[label] = {}
                
                next_id = row[1]
                is_new_video = (prev_id != next_id) or (prev_label != label)
                if is_new_video and prev_id != EMPTY_ID:
                    if res[prev_label].get(prev_id) is not None:
                        #Youtube videoes may have the same id multiple times for the same label :)
                        modified_id = prev_id + f"{id_counter_marker}{counter}"
                        counter = counter + 1
                        res[prev_label][modified_id] = cur_sequence
                    else: 
                        res[prev_label][prev_id] = cur_sequence
                    cur_sequence = []

                prev_id = next_id
                rest_row = row[2:]
                
                rest_length = len(rest_row)
                if rest_length == LENGTH_HANDID_AND_LANDMARKS :
                    #There's only a single hand in here
                    hand_id = int(rest_row[0])
                    if hand_id not in (0,1):
                        raise ValueError(f"Invalid hand_id at line {line+1} for file {path}")
                    parsed_landmarks = sum([list(parse_tuple_list_of_xyz(landmark_tuple)) for landmark_tuple in rest_row[1:]], [])
                    cur_sequence.append(MultiHandStaticFrame(hand_id, parsed_landmarks))
                elif rest_length == 2 * LENGTH_HANDID_AND_LANDMARKS:
                    #There should be two hands in this line
                    
                    hands = [
                        (extract_hand_id_and_landmarks(rest_row,i)) 
                        for i in range(2)
                    ]
                    hands.sort(key = lambda x: x[0]) #sort by the hand_id
                    to_append = MultiHandStaticFrame((0,1), list(sum(map(lambda x: x[1], hands),[])))
                    cur_sequence.append(to_append)
                else:
                    raise ValueError(f"More than two hands for line {line+1}")
            #The loop above is not complete, so we'll add on the last curr
            if len(cur_sequence) > 0:
                res[label][prev_id] = cur_sequence
            return res
        
if __name__ == "__main__":
    from dynamic_signs.csv_reader import csv_reader
    from dynamic_signs.csv_reader import MultiHandStaticFrame
    from sign.training.landmark_extraction.MediapipeTypes import MediapipeHandIndex
    from pathlib import Path

    out_file = str(Path().cwd().joinpath("data", "dynamic_train", "dyn_j_z_test.csv").absolute())
    reader = csv_reader()
    res = reader.extract_two_handed_landmarks(out_file)
    
    ##look at the handedness of the read csv
    for label, sequences in res.items():
        for video_id, frames in sequences.items():
            mapped_frames = list(map(lambda frame : MediapipeHandIndex[frame.present_hands], frames))
            right_handed_frames = list(filter(lambda x: x == "right",mapped_frames))
            left_handed_frames = list(filter(lambda x: x == "left",mapped_frames))
            both_handed_frames = list(filter(lambda x: x == "both",mapped_frames))
            print(f"Video {label}-{video_id} has {len(frames)} frames, which hands are in use? \n\tboth: {len(both_handed_frames)} frames\n\tleft: {len(left_handed_frames)} frames\n\tright: {len(right_handed_frames)} frames")

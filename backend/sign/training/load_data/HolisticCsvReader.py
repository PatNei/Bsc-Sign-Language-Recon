from enum import StrEnum
from typing import Generator
import os
from pathlib import Path
import csv
from dataclasses import dataclass

class holistic_keys(StrEnum):
    FACE = "face"
    LEFT_HAND = "left_hand"
    RIGHT_HAND = "right_hand"
    POSE = "pose"    
    SEGMENTATION_MASK = "segmentation_mask"
    POSE_WORLD = "pose_world"


@dataclass
class HolisticFrame:
    id: int
    
    data: dict[holistic_keys, list[float]]
    def __getitem__(self, key:holistic_keys):
        if key not in self.data:
            return None
        return self.data[key]

HolisticSequence = dict[holistic_keys, list[float]]

class HoslisticCsvReader:
    @staticmethod
    def spawn_sequence() -> dict[holistic_keys, list[float]]:
        return {holistic_keys.FACE: [],
                holistic_keys.LEFT_HAND: [],
                holistic_keys.POSE : [],
                holistic_keys.RIGHT_HAND : [],
                }

    def __init__(self, sequence_spawner = spawn_sequence):
        self.new_holistic_sequence = sequence_spawner

    def _avoid(self, row_val: holistic_keys):
        return row_val == holistic_keys.SEGMENTATION_MASK or row_val == holistic_keys.POSE_WORLD
    
    def _remove_file_suffix(self, file_name: str):
        return file_name.removesuffix("_out.csv")
    
    def frame_generator(self, path:Path) -> Generator[HolisticFrame, None, None]:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            prev_id = -1
            sequence_start_marker = ""

            cur_entry = self.new_holistic_sequence()
            for idx, row in enumerate(reader):
                row_key = holistic_keys(row[0])
                if idx == 0:
                    sequence_start_marker = row_key
                if self._avoid(row_key):
                    continue

                new_id = int(row[1])
                if sequence_start_marker == row_key and prev_id != -1:
                    to_yield = HolisticFrame(prev_id, cur_entry)
                    cur_entry = self.new_holistic_sequence()
                    yield to_yield

                prev_id = new_id
                if len(row) > 2:
                    landmarks = row[2:]
                    row_marks = list(map(lambda elm : float(elm), landmarks))
                    if row_key not in cur_entry:
                        raise ValueError(f"Holistic Sequence only allows keys: {[k for k in self.new_holistic_sequence().keys()]}.\n\tEither update \"spawn_sequence\" function or check if csv is broken")
                    cur_entry[row_key] = row_marks
            yield HolisticFrame(prev_id, cur_entry)
        

    def extract_holistic_landmarks(self, path:Path) -> dict[int, HolisticSequence]:
        """Extracts holistic landmarks from a single csv-file
        The file should only include landmarks of the same label.

        returns:
            A dictionary from an int (the sequence id) to a list of concatenated landmarks.
            That is, if any frame is missing a left_hand, the final HolisticSequence will be
            that frame shorter. So, for 5 frame where one is without a left_hand, the final
            length would be (5*21*3) - (1 * 21 * 3).
            TODO: Currently no way of recombining the fields of HolisticSequence into the
            original CSV data. We don't know which frames were missing D:
        """
        res :dict[int, HolisticSequence] = {}
        with open(path, 'r') as f:
            reader = csv.reader(f)
            prev_id = -1

            cur_entry: HolisticSequence = self.new_holistic_sequence()
            for row in reader:
                row_key = holistic_keys(row[0])
                if self._avoid(row_key):
                    continue

                new_id = int(row[1])
                is_new_video = new_id != prev_id
                if is_new_video and prev_id != -1:
                    res[prev_id] = cur_entry
                    cur_entry = self.new_holistic_sequence()
                    
                prev_id = new_id
                if len(row) > 2:
                    landmarks = row[2:]
                    row_marks = list(map(lambda elm : float(elm), landmarks))
                    if row_key not in cur_entry:
                        raise ValueError(f"Holistic Sequence only allows keys: {[k for k in self.new_holistic_sequence().keys()]}.\n\tEither update \"spawn_sequence\" function or check if csv is broken")
                    cur_entry[row_key].extend(row_marks)
            if len(list(cur_entry.values())[0]) > 0:
                res[prev_id] = cur_entry
        return res
    
    def extract_holistic_landmarks_from_folder(self, path: str) -> dict[str, dict[int, HolisticSequence]]:
        """
            Returns a dictionary from LABEL of the sign to a dictionary of sequence_ID to a HolisticSequence.
                
                HolisticSequence:
                    A dictionary of keys: ["face", "right_hand", "left_hand", "pose"]. 
                    Keys map to a list of the floats corresponding to xyz of landmarks of all frames in the sequnce.
        """
        res = {}
        for csv_file in [path+os.sep+file for file in os.listdir(path) if file.endswith(".csv")]:
            path_to_file = Path(csv_file)
            label = self._remove_file_suffix(path_to_file.name)
            res[label] = self.extract_holistic_landmarks(path_to_file.absolute())
        return res
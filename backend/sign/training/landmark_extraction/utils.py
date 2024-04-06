import os
from natsort import natsorted
from dataclasses import dataclass

@dataclass
class ImageSequence:
    id: int
    filepaths: list[str]


def __extract_prefix(filename:str, separator:str = "_"):
    return filename.split(separator)[0]

def get_image_sequences_from_dir(dir:str) -> dict[str, list[ImageSequence]]:
    """
        :params: dir -> the parent directory containing all the folders of individual labels.
                dir:
                    J-label-directory -> n-many sequences of J
                    
                    Z-label-directory -> m-many sequecne of Z
        returns:
            a dictionary from label to a list of sequneces. A sequence consists of all the filenames
            sorted by their sequence number (placement in sequence).
    """
    labels = [folder for folder in os.listdir(dir)
                  if os.path.isdir(dir + os.sep + folder)]
    res_dict = {}
    for label in labels:
        folder_path = dir + os.sep + label + os.sep
        files = natsorted([file for file in os.listdir(folder_path)
                               if os.path.isfile(folder_path + file)])

        prev_prefix = __extract_prefix(files[0])
        cur_sequence = []
        label_sequences: list[ImageSequence] = [ImageSequence(int(prev_prefix), cur_sequence)]
        for image in files:
            prefix = __extract_prefix(image)
            if not (prefix == prev_prefix):
                cur_sequence = []
                label_sequences.append(ImageSequence(int(prefix), cur_sequence))
            cur_sequence.append(folder_path + image)
            prev_prefix = prefix
        res_dict[label] = label_sequences
    return res_dict
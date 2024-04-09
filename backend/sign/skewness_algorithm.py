
import numpy as np

CUTOFF = 0.79 # CUTOFF is %

def calculate_slice_amount(length_of_list:int):
    if length_of_list < 24:
        return 3
    if length_of_list < 50:
        return 5
    return 7

def is_it_evenly_distributed(original_list:list,filtered_list:list,cutoff=CUTOFF):
    if len(filtered_list) > len(original_list):
        raise ValueError("filtered list is bigger than the original list")
    
    filtered_set = set(filtered_list)
    SLICE_AMOUNT = calculate_slice_amount(len(original_list))
    
    evenly_distributed_list = np.array_split(original_list,SLICE_AMOUNT)
    for chunk in evenly_distributed_list:
        leaf = set(chunk)
        common_indices = leaf.intersection(filtered_set)
        if len(common_indices) / len(leaf) > cutoff:
            continue
        return False
    return True
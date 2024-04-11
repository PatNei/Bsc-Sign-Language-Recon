
import numpy as np

CUTOFF = 0.20 # CUTOFF is %
SLICE_LESS_THAN_24 = 3
SLICE_LESS_THAN_50 = 3
SLICE_MORE_THAN_50 = 3

def calculate_slice_amount(length_of_list:int):
    if length_of_list < 24:
        return SLICE_LESS_THAN_24
    if length_of_list < 50:
        return SLICE_LESS_THAN_50
    return SLICE_MORE_THAN_50

def is_it_evenly_distributed(unfiltered_list:list,filtered_list:list,cutoff=CUTOFF):
    """
    TODO: THIS NEEDS TO BE REVISITED AS WE CAN'T USE SETS
    """
    if len(filtered_list) > len(unfiltered_list):
        raise ValueError("filtered list is larger than the original list")
    
    SLICE_AMOUNT = calculate_slice_amount(len(unfiltered_list))
    
    evenly_distributed_list = np.array_split(range(len(unfiltered_list)),SLICE_AMOUNT)
    
    for chunk in evenly_distributed_list:
        common_indices = [i for i in chunk if i in filtered_list] # Bootleg intersection using list
        if len(common_indices) / len(chunk) > cutoff:
            continue
        return False
    return True
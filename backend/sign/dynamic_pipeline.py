from collections import Counter
from typing import Literal, Tuple, Union
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sign.training.load_data.dynamic_loader import DynamicLoader
import numpy as np
import numpy.typing as npt


'''
Split 24 frames into 6 (maybe experiment with having traj in models or not)



'''
INTERMEDIATES = 3
INTERMEDIATE_FRAMES = 8
TARGET_LENGTH = INTERMEDIATES * INTERMEDIATE_FRAMES
REAL_TRAJECTORIES:list[dict[str, npt.NDArray[np.float32]]] = [{} for _ in range(INTERMEDIATES)]
MODELS = []

loader = DynamicLoader(target_len=TARGET_LENGTH)
data = loader.prepare_training_data("../backend/new_youtube.csv")
xs = data.xs
print(len(xs))
ys = data.ys

# <trajector> = <xyz_direction>_0... <xyz_direction>_TARGET_LENGTH-1
# x = [<trajectory>, <42xyz>_0...<42xyz>_20]
def split_data_into_pipeline_trainin_samples():
    landmarks_for_steps:list[Tuple] = []
    trajectories_for_steps:list[Tuple] = []
    for x in xs:
        trajector_end = (TARGET_LENGTH-1) * 3
        #x_trj = np.split(x[:trajector_end], INTERMEDIATES)
        
        #Pad the trajectory with an all stationary trajectory element at the begining.
        x_trj = np.split(np.concatenate((np.array([0,0,0]), x[:trajector_end])), INTERMEDIATES)
        x_lndmrks = np.split(x[trajector_end:], INTERMEDIATES)
        landmarks_for_steps.append(tuple(x_lndmrks))
        trajectories_for_steps.append(tuple(x_trj))
    return landmarks_for_steps, trajectories_for_steps 

lndmarks, trajects = split_data_into_pipeline_trainin_samples()

def train_pipeline():
    #remember most common trajectories?
    label_step_dict: dict[str, dict[int, list[npt.NDArray[np.float32]]]] = { label: {} for label in ys}
    zipped = zip(np.array(list(map(np.array,trajects))), ys)
    for numpied, label in zipped:
        for step in range(INTERMEDIATES):
            trajectory = numpied[step]
            if label_step_dict[label].get(step) is None:
                label_step_dict[label][step] = [trajectory]
            else:
                label_step_dict[label][step].append(trajectory)

    for label, steps in label_step_dict.items():
        for step, trajectories in steps.items():
            #trajectories_as_strs = list(map(lambda x: ))
            uniques, counts = np.unique(trajectories, return_counts=True, axis=0)
            most_unique = max(zip(uniques, counts), key = lambda uniq_cnt_tuple: uniq_cnt_tuple[1])[0]
            try:
                REAL_TRAJECTORIES[step][label] = most_unique
            except:
                raise Exception("You've stepped outside the bounds, brotherman")
    
    #lndmarks = [(xs_m1, xs_m2, xs_m3), (xs_m1)] -> [[xs_m1, xs_m1], [xs_m2, xs_m2], [xs_m3, xs_m3]]
    step_xs = [[] for _ in range(INTERMEDIATES)]
    for step_landmarks_tuple in lndmarks:
        for i in range(INTERMEDIATES):
            step_xs[i].append(step_landmarks_tuple[i])


    for idx, training_samples in enumerate(step_xs):
        #print(f"Training model for step {idx} - shape:{np.array(training_samples).shape}")     
        clf = LogisticRegression()
        clf.fit(training_samples, ys)
        MODELS.append(clf)
    


def predict_pipeline(x) -> Union[str, bool]:
    '''
    TODO: En god fortælling om hvad der foregår her :D
    '''
    lndmarks, trajectories = split_data_into_pipeline_trainin_samples()
    predictions = []
    for i in range(INTERMEDIATES):
        predictions.append(predict_step(lndmarks[i], i))
    for i in range(INTERMEDIATES):
        if(i > 0):
            if(predictions[i] != predictions[i - 1]):
                return False

        if not(REAL_TRAJECTORIES[i][predictions[i]] == trajectories[i]):
            return False
    return predictions[0]


def predict_step(data, modelnumber):
    return MODELS[modelnumber].predict(data)


    
    

from collections import Counter
from typing import Literal, Tuple, Union
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from joblib import dump
from sklearn.linear_model import LogisticRegression
from sign.training.load_data.dynamic_loader import DynamicLoader
import numpy as np
import numpy.typing as npt


class DynamicClassifierPipeline():
    """ A simple DynamicPipeline class that tries to fulfill the subset of API functions needed to use
    Sklearn cross_validate functions.
    """

    def __init__(self,
                 intermediates = 3,
                 intermediate_frames = 8,
                 verbose:Literal[0,1,2] = 0,
                 model_failed:str = "__MODEL_FAILED__",
                 trajectory_failed:str = "__TRAJECTORY_FAILED__",
                 out_name = "DynamicPipeline"):
        self.intermediates = intermediates
        self.intermediate_frames = intermediate_frames
        self.real_trajectories:list[dict[str, npt.NDArray[np.float32]]] = [{} for _ in range(intermediates)]
        self.__target_length = self.intermediates * self.intermediate_frames
        self.models = []
        self.__verbose = verbose
        self.__model_failed = model_failed
        self.__trajectory_failed = trajectory_failed
        self.__out_name = out_name
        self.is_fitted = False
    
    def dump(self):
        if not self.is_fitted:
            raise Exception("Pipeline hasn't been fitted!")
        dump(self, self.__out_name)

    def __instantiate_model(self, step:int):
        clf = LogisticRegression(max_iter=10_000, verbose=2 if self.__verbose else 0)
        if self.__verbose:
            print(f"Step{step} -> Uses model of type:\n\t{type(clf)}")
        return clf


    def __split_training_instance(self, x:npt.NDArray[np.float32]) -> Tuple[list[npt.NDArray[np.float32]], list[npt.NDArray[np.float32]]]:
        """
            Splits a instance training instance. The instance has to be of the form:
            
            Params:
            ---------
            x = [<trajectory>, <42xyz>_0...<42xyz>_20]
                - Where: <trajectory> = <xyz_direction>_0... <xyz_direction>_TARGET_LENGTH-1
                - And:   <42xyz>_n is the 42 x-,y-,z-values for static sign recognition
        
        """
        trajector_end = (self.__target_length-1) * 3
        #Pad the trajectory with an all stationary trajectory element at the begining.
        padded_trajectory = np.concatenate((np.array([0,0,0]), x[:trajector_end]))
        x_trj = np.split(padded_trajectory, self.intermediates)
        x_lndmrks = np.split(x[trajector_end:], self.intermediates)
        return x_trj, x_lndmrks

    def split_data_into_pipeline_training_samples(self, xs: list[npt.NDArray[np.float32]]):
        """
        Tries reformat the training data from DynamicLoader into a format the pipeline finds useful.

        Params:
        -------
        - xs = [$<trajectory>, <42xyz>_0...<42xyz>_20$_0, $<trajectory>, <42xyz>_0...<42xyz>_20$_1,...]
            - Where: <trajectory> = <xyz_direction>_0... <xyz_direction>_TARGET_LENGTH-1
            - And:   <42xyz>_n is the 42 x-,y-,z-values for static sign recognition
        """
        #tuple(zip(*map(self.__split_training_instance, xs), ()))
        landmarks_for_steps:list[Tuple] = []
        trajectories_for_steps:list[Tuple] = []
        for x in xs:
            x_trj, x_lndmrks = self.__split_training_instance(x)
            landmarks_for_steps.append(tuple(x_lndmrks))
            trajectories_for_steps.append(tuple(x_trj))
        return landmarks_for_steps, trajectories_for_steps 
    
    def fit(self, xs, ys):
        """Fits this pipline and its underlying models.
        
        Params
        --------
            :xs: -> a list of instances used for training. MUST come in the same format as DynamicLoader.prepare_training_data() uses!
            
            :ys: -> a list of the true labels for the instances (xs), where indices match, that is label(xs[0]) == ys[0] 
        """

        lndmarks, trajects = self.split_data_into_pipeline_training_samples(xs)

        #remember most common trajectories?
        label_step_dict: dict[str, dict[int, list[npt.NDArray[np.float32]]]] = { label: {} for label in ys}
        zipped = zip(np.array(list(map(np.array,trajects))), ys)
        for numpyified, label in zipped:
            for step in range(self.intermediates):
                trajectory = numpyified[step]
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
                    self.real_trajectories[step][label] = most_unique
                except:
                    raise Exception("You've stepped outside the bounds, brotherman")
        
        #lndmarks = [(xs_m1, xs_m2, xs_m3), (xs_m1)] -> [[xs_m1, xs_m1], [xs_m2, xs_m2], [xs_m3, xs_m3]]
        step_xs = [[] for _ in range(self.intermediates)]
        for step_landmarks_tuple in lndmarks:
            for i in range(self.intermediates):
                step_xs[i].append(step_landmarks_tuple[i])
        for idx, training_samples in enumerate(step_xs):
            if self.__verbose:
                print(f"Training model for step {idx} - shape:{np.array(training_samples).shape}")     
            clf = self.__instantiate_model(idx)
            clf.fit(training_samples, ys)
            self.models.append(clf)
        self.is_fitted = True

    def predict_step(self, data, modelnumber) -> str:
        return self.models[modelnumber].predict(data)[0]
    
    
    def predict_single(self, x) -> str:
        """ Predicts the label of a single instance.
        """
        if not self.is_fitted:
            raise Exception("Model hasn't bene fit! Call fit()")
        step_to_trajectory, landmarks_for_steps = self.__split_training_instance(x)
        
        predictions:list[str] = []
        for i in range(self.intermediates):
            prediction = self.predict_step([landmarks_for_steps[i]], i)
            predictions.append(prediction)
            if self.__verbose:
                print(f"Step{i}: model predicted -> {prediction}")
        for i in range(self.intermediates):
            if(i > 0):
                if(predictions[i] != predictions[i - 1]):
                    return self.__model_failed

            prediction_at_step = predictions[i]
            real_trajectory = self.real_trajectories[i][prediction_at_step]
            if not np.array_equal(real_trajectory, step_to_trajectory[i]):
                if self.__verbose:
                    print(f"Step{i}: trajectory discard -> {prediction_at_step}")
                return self.__trajectory_failed
        return predictions[0]
    
    def predict(self, xs) -> list[str]:
        return list(map(self.predict_single, xs))


if __name__ == "__main__":
    '''
    Split 24 frames into 6 (maybe experiment with having traj in models or not)

    '''
    INTERMEDIATES = 3
    INTERMEDIATE_FRAMES = 8
    TARGET_LENGTH = INTERMEDIATES * INTERMEDIATE_FRAMES

    loader = DynamicLoader(target_len=TARGET_LENGTH)
    PATH = "../backend/new_youtube.csv"
    #PATH = "small_dyn.csv"
    print("Loading data...")
    data = loader.prepare_training_data(PATH)
    xs = data.xs
    ys = data.ys
    print("Loaded data...")
    
    print("...About to train 💪")
    pipe = DynamicClassifierPipeline(INTERMEDIATES, INTERMEDIATE_FRAMES, verbose=2)
    pipe.fit(xs, ys)
    print("Trained model")

    TARGET = (ys[4], xs[4])
    print(f"Trying to predict {TARGET}")
    predicted = pipe.predict_single(TARGET[1])
    print(f"Final prediction is: '{predicted}'")




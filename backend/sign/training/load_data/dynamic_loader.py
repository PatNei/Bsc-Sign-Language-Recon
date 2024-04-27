from pathlib import Path
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from typing import Literal
from dynamic_signs.csv_reader import csv_reader
from sign.training.landmark_extraction.MediapipeTypes import MediapipeLandmark
from sign.trajectory import TrajectoryBuilder
from sign.landmarks import pre_process_landmark, calc_landmark_list
from sklearn.model_selection import train_test_split
from typing import Tuple

@dataclass
class DynamicTrainingData:
    xs: list[npt.NDArray[np.float32]]
    ys: list[str]

    def spliterino(self, 
                   train_size = 0.8, 
                   random_state = 42) -> Tuple[Tuple[npt.NDArray[np.float32]], Tuple[str], Tuple[npt.NDArray[np.float32]], Tuple[str]]:
        """Performs the test-train-split and shuffles the data (keeping the label/instance ordering in tact)

        Params:
        --------
        :train_size: The desired size of the training set. between 0 and 1.
        :random_state: Used to control the Scikit train_test_split
        """
        zipped = list(zip(self.xs,self.ys))
        static_test_train, static_test_test = train_test_split(zipped, train_size=train_size, random_state=random_state)
        train = list(zip(*static_test_train))
        test = list(zip(*static_test_test))
        return train[0], train[1], test[0], test[1]     #landmarks, labels, landmarks, labels

class DynamicLoader():
    """
        Class for loading dynamic data used for training models.
    
        Example:
        --------
        >>> from sign.training.load_data.dynamic_loader import DynamicLoader
        >>> loader = DynamicLoader(target_len = 24)
        >>> somepath = "HERE GOES YOUR PATH"
        >>> trainig_data = loader.prepare_training_data(somepath)
        >>> xs_train, ys_train, xs_test, ys_test = trainig_data.spliterino(xs,ys)

    """
    reader: csv_reader
    bob: TrajectoryBuilder

    def __init__(self, target_len:int):
        self.reader = csv_reader()
        self.bob = TrajectoryBuilder(target_len=target_len)

    @staticmethod
    def __decide_target(left: list[list[float] | None], right: list[list[float] | None]) -> tuple[list[float], Literal["left", "right"] | None] :
        """
        Decides which hand to continue our preprocessing step for.
        
        That is, choosing the longest list when all 'None's are removed.
        """
        #left_landmarks = [elm for elm in left if elm is not None]
        #right_landmarks = [elm for elm in right if elm is not None]
        left_landmarks = sum([elm for elm in left if elm is not None],[])
        right_landmarks = sum([elm for elm in right if elm is not None],[])
        target = max((left_landmarks, "left"), 
                     (right_landmarks,"right"), 
                      key=lambda x : len(x[0]))
        if not target[0]: #both were full of "None" somehow??
            return [],None
        return target
    
    def prepare_training_data(self, path:str | Path) -> DynamicTrainingData:
        """Extracts and prepares training data directly from a csv.

        :path: must be a path (in str form) to a csv created using MediaPiper.
        """
        #xs : the list of instances used for training dynamic model
        xs = []
        #ys: the list of labels for the instances of xs. 
            #it should always match so that xs[n] has the corresponding label ys[n]
        ys:list[str] = []

        data = self.reader.extract_two_handed_landmarks(path)

        for label, id_video_frames in data.items():
            for id, video_frames in id_video_frames.items():
                left_frames, right_frames = zip(*[frame.get_landmarks() for frame in video_frames])
                video_xyz, hand = self.__decide_target(left_frames, right_frames)
                if hand is None:
                    print(f"WARNING: Both hands for label-id: '{label}'-'{id}' were empty - SKIPPING")
                    continue
                video_xyz = list(np.array(video_xyz).reshape((-1,21,3)))
                
                # a sequence of frames (XYZ landmarks) of target length by courtesy of bob
                enforced = np.array(self.bob.enforce_target_length(video_xyz))
                # ^can fail since bob removes outliers before sampling.
                
                def mapper_preprocess_landmarks(elm : np.ndarray):
                    landmarks = list(map(lambda y: MediapipeLandmark(y[0], y[1], y[2]), elm))
                    return pre_process_landmark(calc_landmark_list(landmarks))
                
                # the x,y normalized to mediapipe index.
                static_flatmarks_xy = sum(map(mapper_preprocess_landmarks, enforced.reshape((-1, 21, 3))), [])
                traj = self.bob.make_trajectory(enforced)

                #the final version of the data, ready for training.
                video_res = np.array(traj.to_float_list() + static_flatmarks_xy, dtype=np.float32)
                
                ys.append(label)
                xs.append(video_res)
        ys = list(map(lambda label: label.capitalize(), ys))
        return DynamicTrainingData(xs,ys)

if __name__ == "__main__":
    loader = DynamicLoader(target_len=24)
    #data = loader.prepare_training_data("data/dynamic_train/dyn_j_z_homemade.csv")
    path = Path("backend/sign/training/load_data/dyn_50_common_youtube_55p.csv")
    data = loader.prepare_training_data(path)


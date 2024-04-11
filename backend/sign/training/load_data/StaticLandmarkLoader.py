import numpy.typing as npt
import csv
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Tuple, NamedTuple, Union

LandmarksCSV = list[npt.NDArray[np.float32]]
NPFloat = npt.NDArray[np.float32]
NPStr = npt.NDArray[np.str_]

class TrainingData(NamedTuple):
    landmarks_train : NPFloat
    labels_train : NPStr
    landmarks_test : NPFloat
    labels_test : NPStr
    hands_train : Union[NPStr, None]
    hands_test : Union[NPStr, None]

class StaticLandmarkLoader(object):
    def __init__(self) -> None:
        pass

    def __load_csv_data(self, file_path: str, handedness = False) -> Tuple[LandmarksCSV, list[str], list[str]]:
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
        landmarks_start_index = 1 if not handedness else 2

        
        landmarks_list: LandmarksCSV = []
        labels_list:list[str] = []
        handedness_list: list[str] = []
        for entry in data:
            if handedness:
                handedness_list.append(entry[1])
            landmarks_list.append(np.array(entry[landmarks_start_index:], dtype=np.float32))
            labels_list.append(entry[0])
        return landmarks_list, labels_list, handedness_list

    def load_training_data(self, file_path: str) -> TrainingData:
        """Loads a csv prepared for static image training as train data. The method performs a 
        train test split, where 20% of the data will be put into a separate array for testing/validation.

        returns:
            A tuple of 4 elements:
            1) landmarks_train landmarks encoded as a np array for training. 
            2) labels_train matching the landmarks_train
            3) landmarks_test The 20% landmarks selected for testing. 
            4) labels_test labels matching the landmarks_test 
        """
        landmarks_list, labels_list,_ = self.__load_csv_data(file_path)
        return self.__train_test_split(landmarks_list, labels_list)
    
    def load_test_data(self, file_path: str) -> Tuple[LandmarksCSV, list[str]]:
        """Loads a csv prepared for static image training as test data, meaning no train test split
        
        returns:
            A tuple of landmarks encoded as np array and a list of matching labels.
        """
        return self.__load_csv_data(file_path)[:2]

    def load_handed_training_data(self, file_path:str) -> TrainingData:
        landmarks_list, labels_list, hands = self.__load_csv_data(file_path, handedness=True)
        return self.__train_test_split(landmarks_list, labels_list, hands)

    @staticmethod
    def __train_test_split(landmarks: LandmarksCSV, labels: list[str], hands: list[str] = []) -> TrainingData:
        if len(hands) < 1:
            zipped = list(zip(landmarks,labels))
            train_set, test_set = train_test_split(zipped, test_size=0.2, random_state=42)
            landmarks_train, labels_train = zip(*train_set)
            landmarks_test, labels_test = zip(*test_set)
            hands_train = None
            hands_test = None
        else:
            zipped = list(zip(landmarks, labels, hands))
            train_set, test_set = train_test_split(zipped, test_size=0.2, random_state=42)
            landmarks_train, labels_train, hands_train = zip(*train_set)
            landmarks_test, labels_test, hands_test = zip(*test_set)
            hands_train = np.array(hands_train, dtype=np.str_)
            hands_test = np.array(hands_test, dtype=np.str_)

        landmarks_train = np.array(landmarks_train)
        labels_train = np.array(labels_train)
        landmarks_test : npt.NDArray[np.float32] = np.array(landmarks_test)
        labels_test : npt.NDArray[np.str_] = np.array(labels_test)

        return TrainingData(landmarks_train, labels_train,
                            landmarks_test, labels_test,
                            hands_train, hands_test)
import numpy.typing as npt
import csv
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Tuple, NamedTuple

LandmarksCSV = list[npt.NDArray[np.float32]]
NPFloat = npt.NDArray[np.float32]
NPStr = npt.NDArray[np.str_]

class TrainingData(NamedTuple):
    landmarks_train : NPFloat
    labels_train : NPStr
    landmarks_test : NPFloat
    labels_test : NPStr


class StaticLandmarkLoader(object):
    def __init__(self) -> None:
        pass

    def load_training_data(self, file_path: str) -> TrainingData:
        """
        """
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)

        landmarks_list: LandmarksCSV = []
        labels_list:list[str] = []
        for entry in data:
            landmarks_list.append(np.array(entry[1:], dtype=np.float32))
            labels_list.append(entry[0])

        return self.__train_test_split(landmarks_list, labels_list)

    @staticmethod
    def __train_test_split(landmarks: LandmarksCSV, labels: list[str]) -> TrainingData:
        zipped: list[Tuple[NPFloat, str]] = list(zip(landmarks,labels))

        train_set, test_set = train_test_split(zipped, test_size=0.2, random_state=42)

        train_set_unpacked = [ [landmark for landmark, _ in train_set],
                                [label for _, label in train_set] ]
        landmarks_train = np.array(train_set_unpacked[0])
        labels_train = np.array(train_set_unpacked[1])
        test_set_unpacked  = [ [landmark for landmark, _ in test_set],
                               [label for _, label in test_set] ]
        landmarks_test : npt.NDArray[np.float32] = np.array(test_set_unpacked[0])
        labels_test : npt.NDArray[np.str_] = np.array(test_set_unpacked[1])

        return TrainingData(landmarks_train, labels_train,
                            landmarks_test, labels_test)
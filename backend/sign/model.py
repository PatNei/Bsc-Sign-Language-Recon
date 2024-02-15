import numpy.typing as npt
import csv
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from typing import Protocol, Self, Tuple, List

class TrainingData:
    landmarks_array : npt.NDArray[np.float32]
    labels_array : npt.NDArray[np.str_]
    landmarks_test : npt.NDArray[np.float32]
    labels_test : npt.NDArray[np.str_]
    
    def __init__(self, landmarks, labels):
        self.landmarks_array : npt.NDArray[np.float32] = np.array(landmarks)
        self.labels_array : npt.NDArray[np.str_] = np.array(labels)
        self.landmarks_test : npt.NDArray[np.float32] = np.array([], dtype=np.float32)
        self.labels_test : npt.NDArray[np.str_] = np.array([], dtype=np.str_)

    def train_test_split(self):
        #Zip landmarks and labels, then shuffle, then unzip
        zipped: List[Tuple[(np.float32,np.str_)]] = list(zip(self.landmarks_array, self.labels_array))

        #then shuffle
        train_set, test_set = train_test_split(zipped, test_size=0.2, random_state=42)


        train_set_unpacked = [ [landmark for landmark, _ in train_set],
                               [label for _, label in train_set] ]
        self.landmarks_train = np.array(train_set_unpacked[0])
        self.labels_train = np.array(train_set_unpacked[1])
        
        test_set_unpacked  = [ [landmark for landmark, _ in test_set],
                               [label for _, label in test_set] ]
        self.landmarks_test : npt.NDArray[np.float32] = np.array(test_set_unpacked[0])
        self.labels_test : npt.NDArray[np.str_] = np.array(test_set_unpacked[1])


def load_training_data(file_path) -> TrainingData:
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    landmarks_list = []
    labels_list = []
    for entry in data:
        landmarks_list.append(np.array(entry[1:], dtype=np.float32))
        labels_list.append(entry[0])

    return TrainingData(np.array(landmarks_list, dtype=np.float32), np.array(labels_list, dtype=np.str_))

class scikitModel(Protocol):
    def __init__(self):
        super().__init__()
    def __call__(self) -> Self: 
        return self
    def fit(self,X:npt.NDArray,y:npt.NDArray): ...
    def predict(self,target:npt.NDArray) -> npt.NDArray[np.str_]: ...



class SignClassifier:
    def __init__(self, model:scikitModel, X:npt.NDArray, y:npt.NDArray):
        sgd_clf = model()
        sgd_clf.fit(X, y)
        self.model = sgd_clf

    def predict(self, target:npt.NDArray[np.float32]) -> npt.NDArray[np.str_]:
        return self.model.predict(target)

if __name__ == '__main__':
    print("it works sir")
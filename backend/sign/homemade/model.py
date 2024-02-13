import csv
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from backend.sign.model.keypoint_classifier.keypoint_classifier import NormalizedLandmark

class TrainingData:
    def __init__(self, landmarks, labels):
        self.landmarks_array = np.array(landmarks)
        self.labels_array = np.array(labels)

    def train_test_split(self):
        #Zip landmarks and labels, then shuffle, then unzip
        zipped = list(zip(self.landmarks_array, self.labels_array))

        #then shuffle
        train_set, test_set = train_test_split(zipped, test_size=0.2, random_state=42)


        train_set_unpacked = [ [landmark for landmark, _ in train_set],
                               [label for _, label in train_set] ]
        self.landmarks_train = np.array(train_set_unpacked[0])
        self.labels_train = np.array(train_set_unpacked[1])
        
        test_set_unpacked  = [ [landmark for landmark, _ in test_set],
                               [label for _, label in test_set] ]
        self.landmarks_test = np.array(test_set_unpacked[0])
        self.labels_test = np.array(test_set_unpacked[1])


def load_training_data(file_path):
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    landmarks_list = []
    labels_list = []
    for entry in data:
        landmarks_list.append(np.array(entry[1:], dtype=np.float32))
        labels_list.append(entry[0])

    return TrainingData(landmarks_list, labels_list)

class SignClassifier:
    def __init__(self, model:SGDClassifier, X, y):
        sgd_clf = model(random_state=42)
        sgd_clf.fit(X, y)
        self.model: SGDClassifier = sgd_clf

    def predict(self, target:np.ndarray[NormalizedLandmark]) -> np.ndarray[np.str_]:
        return self.model.predict(target)


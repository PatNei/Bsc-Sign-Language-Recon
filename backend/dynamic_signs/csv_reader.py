import csv

import numpy as np

class csv_reader:
    def __init__(self):
        pass
    
    def extract_landmarks(self,path:str) -> dict[str, dict[int, list[float]]]:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            landmarks: dict[str, dict[int, list[float]]] = {}
            id = None
            new_video = False
            parsed_landmarks: list[float] = []
            for row in reader:
                new_video = int(row[1]) != id
                id = int(row[1])
                label = row[0]
                for landmark in row[2:-1]:
                    coords = np.fromstring(landmark.strip(",").strip("[").strip("]"), dtype=np.float32, sep=",")
                    for coord in coords:
                        parsed_landmarks.append(coord)
                if new_video:
                    existing = landmarks.get(label)
                    if existing is not None:
                        existing[id] = parsed_landmarks
                    else:
                        landmarks[label] = {id:parsed_landmarks}
                else:
                    existing = landmarks.get(label)
                    if existing is not None:
                        existing[id].extend(parsed_landmarks)
                    else:
                        landmarks[label] = {id:parsed_landmarks}
                parsed_landmarks = []
            return landmarks
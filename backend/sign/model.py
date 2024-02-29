import numpy.typing as npt
import numpy as np
from typing import Protocol, Self, Tuple, List

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
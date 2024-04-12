from typing import Literal, NamedTuple, Self, Union, Tuple
import numpy as np

MediapipeHandIndexLabel: dict[Literal["left", "right", "both"], Literal[0,1] | Tuple[Literal[0], Literal[1]]] = {
    "left": 0,
    "right" : 1,
    "both": (0,1)
}
MediapipeHandIndex: dict[Literal[0,1] | Tuple[Literal[0], Literal[1]], Literal["left", "right", "both"]] = {
    0: "left",
    1: "right",
    (0,1): "both"
}


class MediapipeLandmark(NamedTuple):
    """ A raw landmark directly from Mediapipe hands
    """
    x: np.float32
    y: np.float32
    z: np.float32

class MediapipeClassification(NamedTuple):
    """ A raw classification of handedness from Mediapipe
    """
    index: Literal[0,1]
    score: np.float32
    label: np.str_

class MediapipeResult(NamedTuple):
    """ A Mediapipe hands result.
    It could be the result of calling hands.process(img)

    TODO: world_landmarks and handedness are not actually sweet python lists,
    there are instead scary Mediapipe protobuf classes
    """
    multi_hand_landmarks: Union[list[MediapipeLandmark], None]
    multi_hand_world_landmarks: Union[list[MediapipeLandmark], None]
    multi_handedness: Union[list[MediapipeClassification], None]

    def number_of_hands(self) -> int:
        if not self.multi_hand_landmarks:
            return 0
        return int(len(self.multi_hand_landmarks) / 21)
    def __assert_hands(self, hand:int):
        if hand > self.number_of_hands():
            raise IndexError(f"MediapipeResult was instantiated with data for {self.number_of_hands()}, not {hand}")

    def multi_hand_landmarks_by_hand(self, hand:Literal[0,1]):
        self.__assert_hands(hand)
        if not self.multi_hand_landmarks:
            return None
        return self.multi_hand_landmarks[hand*21:(hand+1)*21]
    
    def multi_handedness_by_hand(self, hand:Literal[0,1]):
        self.__assert_hands(hand)
        if not self.multi_handedness:
            return None
        return self.multi_handedness[hand]

    def multi_hand_world_landmarks_by_hand(self, hand:Literal[0,1]):
        self.__assert_hands(hand)
        if not self.multi_hand_world_landmarks:
            return None
        return self.multi_hand_world_landmarks[hand*21:(hand+1)*21]
    
    def get_hand_result(self, hand:Literal[0,1]) -> Self:
        hand_landmarks = self.multi_hand_landmarks_by_hand(hand)
        hand_world_landmarks = self.multi_hand_world_landmarks_by_hand(hand)
        self_handedness = self.multi_handedness_by_hand(hand)
        if self_handedness:
            self_handedness = [self_handedness]
        return type(self)(hand_landmarks, hand_world_landmarks, self_handedness)
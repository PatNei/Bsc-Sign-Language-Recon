from abc import ABC, abstractmethod

class DynamicPiper(ABC):
    @abstractmethod
    def write_dynamic_gestures_from_folder_to_csv(self,path:str, out:str):
        pass


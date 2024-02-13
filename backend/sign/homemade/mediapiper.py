import backend.sign.homemade.imageloader as imageloader
import backend.sign.homemade.sussyproc as sussyproc
import mediapipe as mp
import csv

class ProcessedImage:
    def __init__(self, label, landmarks, raw_img):
        self.label = label
        self.landmarks = landmarks
        self.img = raw_img
    
    def __str__(self):
        return "<PI< " + self.label + ": " + str(self.landmarks) + ">PI>"
    
    def __iter__(self):
        return iter((self.label, self.landmarks, self.img))
    
class MediaPiper:
    def __init__(self, **kwargs):
        # TODO: How kwargs?
        use_static_image_mode = 'store_true'
        min_detection_confidence = 0.7
        min_tracking_confidence = 0.5

        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=use_static_image_mode,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.hands = hands

    def process_images_for_training_data(self, images: list[imageloader.LabelledImage]):
        results = []
        for li in images:
            for img in li.data:
                r = ProcessedImage( li.label, self.hands.process(img), img )
                results.append( r )
        return ProcessedImages(results)

    def process_image_for_prediction(self, image):
        raw_mp_landmarks = self.hands.process(image)
        return (sussyproc.normalize_landmarks(raw_mp_landmarks, image), raw_mp_landmarks)

class ProcessedImages:
    processed_images: list[ProcessedImage]

    def __init__(self, result) -> None:
        self.processed_images = result

    def save_processed_image_to_csv(self,file_path):
        save_processed_image_to_csv(file_path, self.processed_images)

def save_processed_image_to_csv(file_path, p_images: list[ProcessedImage]):
    for pi in p_images: 
        label, result, raw_img = pi
        if result.multi_hand_landmarks is not None:
            # Let's spit out the preprocessed landmarks to a CSV for training later.
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks,
                                                  result.multi_handedness):
                
                landmark_list = sussyproc.calc_landmark_list(raw_img, hand_landmarks)
                
                pre_processed_landmark_list = sussyproc.pre_process_landmark(landmark_list)
                with open(file_path, 'a', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([label, *pre_processed_landmark_list])
import copy
import itertools

##-----------------------##
##                       ##
##  SHOUTOUT TO OUR BOI  ##
##                       ##
##-----------------------##

def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point

def normalize_landmarks(mp_result, raw_img):
    res = []
    if mp_result.multi_hand_landmarks is not None:
    # Let's spit out the preprocessed landmarks to a CSV for training later.
        for hand_landmarks, handedness in zip(mp_result.multi_hand_landmarks,
                                                mp_result.multi_handedness):
            
            landmark_list = calc_landmark_list(raw_img, hand_landmarks)
            
            pre_processed_landmark_list = pre_process_landmark(landmark_list)
            res.append(pre_processed_landmark_list)

    return res


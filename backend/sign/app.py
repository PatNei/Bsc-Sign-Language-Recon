import backend.sign.homemade.imageloader as imageloader
import backend.sign.homemade.mediapiper as mediapiper
import backend.sign.homemade.drawer as drawer
import backend.sign.homemade.model as model
import backend.sign.homemade.sussyproc as sussyproc
import copy
import os
from joblib import dump, load
from sklearn.linear_model import SGDClassifier 
import cv2 as cv
import numpy.typing as npt

data_base_path = 'data/archive/asl_alphabet_train/'
train_path = 'sign/model/alphabet/train.csv'
model_path = 'sign/model/alphabet/softmax.joblib'
training_amount = 250

piper = mediapiper.MediaPiper()

if(not os.path.isfile(model_path)):
    print("Creating a model")
    
    l = imageloader.load_images_from_directory(data_base_path, amount = training_amount)
    processed = piper.process_images_for_training_data(l)
    processed.save_processed_image_to_csv(train_path)

    data = model.load_training_data(train_path)
    data.train_test_split()
    
    #labels_train_A = (data.labels_train == 'A')
    #a_or_not_a_classifier = model.SignClassifier( 
    #                                SGDClassifier,
    #                                data.landmarks_train, 
    #                                labels_train_A)
    #classifier = a_or_not_a_classifier
    #expected = data.labels_test[0] == 'A'

    mutli_classifier = model.SignClassifier(SGDClassifier,
                                            data.landmarks_train,
                                            data.labels_train,
                                            )
    classifier = mutli_classifier
    expected = data.labels_test[0]

    predicted = classifier.predict( [ data.landmarks_test[0] ] )
    print("Trained a model: ", "predicted: " + str(predicted), "should return " + str( [expected] ))
    dump(mutli_classifier, model_path)
    print("Dumped model to: " + model_path)
else:
    classifier = load(model_path)
    print("loaded model from: " + model_path)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 500)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 500)

while True:
    # Process Key (ESC: end) #################################################
    key = cv.waitKey(10)
    if key == 27:  # ESC
        break

    ret, image = cap.read()
    if not ret:
        break
    image = cv.flip(image, 1)  # Mirror display
    debug_image = copy.deepcopy(image)

    # Detection implementation #############################################################
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

    image.flags.writeable = False
    (landmarks, raw_landmarks) = piper.process_image_for_prediction(image)
    image.flags.writeable = True

    if landmarks is not None and len(landmarks) > 0:
        res = classifier.predict( landmarks )
        for raw_hand_landmark in raw_landmarks.multi_hand_landmarks:
            landmark_list = sussyproc.calc_landmark_list(debug_image, raw_hand_landmark) 
            
            brect = drawer.calc_bounding_rect(debug_image, raw_hand_landmark)
        
            debug_image = drawer.draw_bounding_rect(True, debug_image, brect)
            debug_image = drawer.draw_landmarks(debug_image, landmark_list)
            debug_image = drawer.draw_info_text(
                debug_image,
                brect,
                str(res),
            )

    cv.imshow('Hand Gesture Recognition', debug_image)


cap.release()
cv.destroyAllWindows()

import datetime
import logging
import os
import numpy as np
import matplotlib.pyplot
import random
from pathlib import Path
from time import time
from joblib import dump
from sklearn.calibration import cross_val_predict
from sklearn.discriminant_analysis import StandardScaler
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import RandomizedSearchCV, cross_validate
from dynamic_signs.setup_logging import setup_logging
from sign.training.load_data.StaticLandmarkLoader import StaticLandmarkLoader

STATIC_TRAIN_PATH = Path.cwd().joinpath("misc", "data", "static_train")

CURRENT_DATE = datetime.datetime.now()
CURRENT_DATE_date_str = datetime.datetime.now().strftime("%d-%m-%Y")
CURRENT_DATE_time_str = datetime.datetime.now().strftime("%d-%m-%Y(%H-%M-%S)")
RANDOM_STATE = 422
TRAINING_PATH = "trained_models"

if not os.path.exists(TRAINING_PATH):
    os.mkdir(TRAINING_PATH)

setup_logging(TRAINING_PATH,CURRENT_DATE)

BASE_PATH = TRAINING_PATH + "/" + CURRENT_DATE_date_str
if not os.path.exists(BASE_PATH):
    os.mkdir(BASE_PATH)

def combine_and_shuffle(X1, y1, X2, y2):
    X = np.concatenate((X1, X2))
    y = np.concatenate((y1, y2))
    zipped = list(zip(X,y))
    random.seed(RANDOM_STATE)
    random.shuffle(zipped)
    X_unzipped, y_unzipped = zip(*zipped)
    return np.array(X_unzipped), np.array(y_unzipped)

def filter_out_nothing_space_delete_j_z(X,y):
    filtered_indices = (y == "nothing") & (y == "space") & (y == "del") & (y == "J") & (y == "Z")
    return X[filtered_indices], y[filtered_indices]

def main():
    out_path_searcher = Path.cwd().joinpath(BASE_PATH, "static_searcher.joblib")
    out_path = Path.cwd().joinpath(BASE_PATH, "static_model.joblib")
    #Load data
    loader = StaticLandmarkLoader()
    files = {
        "homemade":STATIC_TRAIN_PATH.joinpath("A_Z_homemade.csv"), 
        "kaggle"  :STATIC_TRAIN_PATH.joinpath("handedness_keypoints_from_data.csv")
        }

    # data = loader.load_handed_training_data("./A_I_homemade.csv")
    # X, y, X_test, y_test, handedness_train, handedness_test = data
    data_kaggle = loader.load_handed_training_data(str(files["kaggle"].absolute()))
    k_x_train, k_y_train, k_x_test, k_y_test, k_h_train, k_h_test = data_kaggle

    data_homemade = loader.load_handed_training_data(str(files["homemade"].absolute()))
    hm_x_train, hm_y_train, hm_x_test, hm_y_test, hm_h_train, hm_h_test = data_homemade

    nt = '\n\t'
    logging.info(f"Loaded data from:\n\t{nt.join(map(str, files.values()))}")

    X, y = combine_and_shuffle(k_x_train, k_y_train, hm_x_train, hm_y_train)
    X_test, y_test = combine_and_shuffle(k_x_test, k_y_test, hm_x_test, hm_y_test)

    logging.info(f"Length kaggle: {len(k_x_train) + len(k_x_test)}, length homemade: {len(hm_x_train)+ len(hm_x_test)}")
    logging.info(f"Combined length train: {len(X)} & Combined length test: {len(X_test)}")
    logging.info(f"Length Kaggle_test: {len(k_x_test)}, length Homemade_test {len(hm_x_test)}")
    
    X, y = filter_out_nothing_space_delete_j_z(X,y)
    X_test, y_test = filter_out_nothing_space_delete_j_z(X_test, y_test)
    logging.info(f"Combined length train after filter: {len(X)}, length combined test after {len(X_test)}")
    #Train
    clf = make_pipeline(StandardScaler(), SVC(kernel="poly"))
    PARAMS_DICT = {
        "svc__C": [0.25, 0.5, 1, 25, 50],
        "svc__coef0": [0.25, 0.5, 1, 100, 250],
        "svc__degree": [3,4,5,6],
    }
    searcher = RandomizedSearchCV(estimator=clf, param_distributions=PARAMS_DICT, n_jobs=-1)    
    logging.info("Checking params")
    start = time()
    searcher.fit(X,y)
    end = time()
    logging.info(f"Finished checking params, took {end - start} seconds")
    logging.info(f"Dumping fit {type(searcher).__name__} to {out_path_searcher}")
    dump(searcher, out_path_searcher)
    logging.info(f"Dumping best estimator to {out_path}")

    _best = searcher.best_estimator_
    cv_result = cross_validate(_best, X, y, cv=3, scoring='accuracy')
    cr_cv_predictions = classification_report(y,cross_val_predict(_best,X,y))
    logging.info(f"Training set - Cross validation result:\n{cv_result}")
    logging.info(f"Training set - Classification report  :\n{cr_cv_predictions}")


    logging.info("---- Validating on Test set ----")
    y_test_pred = _best.predict(X_test) #type: ignore
    
    cr_test = classification_report(y_test,y_test_pred,digits=4)
    logging.info(f"Test set     - Classification Report:\n{cr_test}")

    cm = confusion_matrix(y_test,y_test_pred)
    display = ConfusionMatrixDisplay(cm,display_labels=_best.classes_) #type: ignore
    display.plot()
    matplotlib.pyplot.savefig(f"{BASE_PATH}/cm-{CURRENT_DATE_time_str}")
    


if __name__ == "__main__":
    main()

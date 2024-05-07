import argparse
import datetime
from enum import Enum
import logging
import os
from pathlib import Path
from typing import Dict, Literal
from sklearn.calibration import cross_val_predict
from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from scipy.sparse import spmatrix
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.model_selection import RandomizedSearchCV, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sign.training.load_data.dynamic_loader import DynamicLoader
from sign.CONST import AMOUNT_OF_KEYFRAMES
from collections import Counter
import matplotlib.pyplot

class EK(Enum):
    """Estimator keywords """
    LR = "lr"
    RF = "rf"
    SVC = "svc"
    SVM = "svm"
    VC = "vc"
    BCLR = "bclr"

# Setup Logging
CURRENT_DATE = datetime.datetime.now().strftime("%d-%m-%Y")
RANDOM_STATE = 422
TRAINING_PATH = "model_output"
if not os.path.exists(TRAINING_PATH):
    os.mkdir(TRAINING_PATH)
BASE_PATH = TRAINING_PATH + "/" +CURRENT_DATE
if not os.path.exists(BASE_PATH):
    os.mkdir(BASE_PATH)
LOG_PATH = Path().cwd().joinpath(f"{BASE_PATH}/logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
CURRENT_TIME = datetime.datetime.now().strftime("%d-%m-%Y(%H-%M-%S)")
logging.basicConfig(filename=LOG_PATH.joinpath(f"{CURRENT_TIME}.log"),level=logging.INFO)
    

def load_csv(CSV_PATH:Path,AMOUNT_OF_KEYFRAMES=AMOUNT_OF_KEYFRAMES,NUM_HANDS=2):
    logging.debug("Loading data")
    dyna_lod = DynamicLoader(AMOUNT_OF_KEYFRAMES)
    training_data = dyna_lod.prepare_training_data(CSV_PATH)
    _xs,ys,_xs_test,ys_test = training_data.spliterino(random_state=RANDOM_STATE)
    _xs,_xs_test = np.array(_xs),np.array(_xs_test)
    logging.debug("data loaded")
    return _xs,ys,_xs_test,ys_test

def get_parameters(name:EK):
    if name == EK.LR:
        return  {'C':range(10,1001,20)}
    if name == EK.SVC or name == EK.SVM:
        return {'C':[float(x) for x in range(100,501,20)],"gamma":[round(x * 0.1,3) for x in range(30,51,1)]}
    if name == EK.RF:
        return {"max_features":["sqrt","log2"],"n_estimators":range(100,5001,100),"max_depth":range(500,600,10)}
    if name == EK.BCLR:
        return {"n_estimators":range(100,5001,100)}
    if name == EK.VC:
        return {"voting":["hard","soft"]}
    
    
def get_base_estimators(name:EK,xs:np.ndarray,ys:tuple[str]) -> BaseEstimator:
    if name == EK.LR:
        return LogisticRegression(random_state=RANDOM_STATE,max_iter=10000)
    if name == EK.RF:
        return RandomForestClassifier()
    if name == EK.SVM or name == EK.SVC:
        return SVC(probability=name==EK.SVC) 
    if name == EK.BCLR:
        be = find_optimized_model(EK.LR,xs,ys)
        return BaggingClassifier(be)
    if name == EK.VC:
        lr = find_optimized_model(EK.LR,xs,ys)
        bclr = find_optimized_model(EK.BCLR,xs,ys)
        rf = find_optimized_model(EK.RF,xs,ys)
        return VotingClassifier( estimators=[ 
                                                ('lr', lr), 
                                                ('rf', rf), 
                                                ('bclr', bclr)
        ]) 

def find_optimized_model(estimator_name:EK,xs:np.ndarray,ys:tuple[str],n_jobs=-1):
    estimator = get_base_estimators(estimator_name,xs,ys)
    parameters = get_parameters(estimator_name)
    pre_clf = RandomizedSearchCV(estimator,parameters,n_jobs=n_jobs,verbose=2,random_state=RANDOM_STATE) # type: ignore
    logging.info("Searching for best hyper parameters")
    pre_clf.fit(xs,ys)
    return pre_clf


def evaluate_model(clf:BaseEstimator,xs:np.ndarray,ys:tuple[str],cv=3):
    cross_val_score(clf, xs, ys, cv=cv, scoring="accuracy")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", 
                        help="The .csv containing the input data.",
                        type=str)

    parser.add_argument("model",
                        choices=[x.value for x in EK],
                        help="The model that you wish to use",
                        type=str)
    parser.add_argument("--scale","-s",
                        help="Should the input be scaled ?",
                        dest="scale",
                        action='store_true')
    parser.add_argument("--jobs","-j",
                        help="How many cores should we use?",
                        dest="n_jobs",
                        type=int,
                        default=-1
                        )
    parser.add_argument("--out", 
                        help="name of the out file.",
                        required=False,
                        dest="out",
                        type=str)
    args = parser.parse_args()

    input_path = Path(args.input)
    model_type = EK(args.model)
    should_scale = args.scale
    out_path:Path
    if args.out == None:
        out_path = Path(f"{BASE_PATH}/dynamic-{model_type}-{CURRENT_TIME}.joblib")
    else: 
        out_path = Path(args.out)
        out_path = out_path.joinpath(".joblib") if out_path.suffix != '.joblib' else out_path

    if not input_path.exists() or input_path.suffix != '.csv':
        raise ValueError(f"Input file must be a .csv :thinking:")

    if not out_path.exists():
        logging.info(f"Couldn't find {out_path.name}, so created it.")
        out_path.touch()

    logging.info(f"About to process {input_path} outputting to {out_path}")
    
    xs,ys,xs_test,ys_test = load_csv(input_path)
    n_jobs = args.n_jobs
    logging.info(f"training set: { Counter(ys) }")
    logging.info(f"test set: { Counter(ys_test) }")
    if should_scale:
        if model_type == EK.RF:
            logging.warn("Random forrest doesn't benefit from scaling the data, it might be beneficial to remove the -s or --scale flag.")
        logging.info("Scaling the data")
        scaler = StandardScaler().fit(xs,np.array(ys))
        xs = scaler.transform(xs)
        xs_test = scaler.transform(xs_test)
        if isinstance(xs_test,spmatrix) or isinstance(xs,spmatrix):
            exit()
    
    best_clf = find_optimized_model(model_type,xs,ys,n_jobs)
    logging.info(f"Best Estimator: {best_clf.best_estimator_}")
    logging.info(f"Best Index: {best_clf.best_index_}")
    logging.info(f"Best Params: {best_clf.best_params_}")
    logging.info(f"Best Score: {best_clf.best_score_}")

    y_pred = best_clf.predict(xs_test)
    
    # logging.info(xs.shape)
    # logging.info(xs_test.shape)
    logging.info(f"Cross val score:\n{cross_val_score(best_clf, xs, ys, cv=3, scoring='accuracy')}")
    logging.info(f"Classification Report for training set:\n{classification_report(ys,cross_val_predict(best_clf,xs,ys))}")
    logging.info(f"Classification Report for test set:\n{classification_report(ys_test,y_pred,digits=4,zero_division=1)}")
    cm = confusion_matrix(ys_test,y_pred)
    display = ConfusionMatrixDisplay(cm,display_labels=best_clf.classes_)
    display.plot()
    matplotlib.pyplot.savefig(f"{LOG_PATH}/cm-{CURRENT_TIME}")
    #logging.info(f"Probabilities:\n{[(x,y) for (x,y) in zip(ys_test,best_clf.predict_proba(xs_test))]}")
    from joblib import dump
    dump(best_clf, out_path)

if __name__ == "__main__":
  main()

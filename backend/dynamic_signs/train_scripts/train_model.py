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
from dynamic_signs.setup_logging import setup_logging
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
    
    
def get_base_estimators(name:EK,xs:np.ndarray,ys:tuple[str],optimised=False) -> BaseEstimator:
    if name == EK.LR:
        return LogisticRegression(random_state=RANDOM_STATE,max_iter=10000)
    if name == EK.RF:
        return RandomForestClassifier()
    if name == EK.SVM or name == EK.SVC:
        return SVC(probability=name==EK.SVC) 
    if name == EK.BCLR:
        be = get_model(EK.LR,xs,ys,optimised)
        return BaggingClassifier(be)
    if name == EK.VC:
        lr = get_model(EK.LR,xs,ys,optimised)
        bclr = get_model(EK.BCLR,xs,ys,optimised)
        rf = get_model(EK.RF,xs,ys,optimised)
        return VotingClassifier( estimators=[ 
                                                ('lr', lr), 
                                                ('rf', rf), 
                                                ('bclr', bclr)
        ]) 

def get_model(estimator_name:EK,xs:np.ndarray,ys:tuple[str],optimised=False,n_jobs=-1):
    estimator = get_base_estimators(estimator_name,xs,ys,optimised)
    pre_clf:BaseEstimator
    if optimised:
        parameters = get_parameters(estimator_name)
        pre_clf = RandomizedSearchCV(estimator,parameters,n_jobs=n_jobs,verbose=2,random_state=RANDOM_STATE) # type: ignore
        logging.info(f"Returning {estimator_name.value} model with best hyper parameters")
    else:
        pre_clf = make_pipeline(estimator)
        logging.info(f"Returning {estimator_name.value} model with default parameters")
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
    parser.add_argument("--optimise","-o",
                        help="Should we find the most optimised?",
                        dest="optimise",
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
    should_scale:bool = args.scale
    optimise:bool = args.optimise
    out_path:Path
    if args.out == None:
        out_path = Path(f"{BASE_PATH}/dynamic-{model_type}-{CURRENT_DATE_time_str}.joblib")
    else: 
        out_path = Path(args.out)
        out_path = out_path.joinpath(".joblib") if out_path.suffix != '.joblib' else out_path

    if not input_path.exists() or input_path.suffix != '.csv':
        raise ValueError(f"Input file must be a .csv :thinking:")

    logging.info(f"About to process {input_path} outputting to {out_path}")
    
    xs,ys,xs_test,ys_test = load_csv(input_path)
    
    n_jobs:int = args.n_jobs
    logging.info(f"training set: { Counter(ys) }")
    logging.info(f"test set: { Counter(ys_test) }")
    
    if not should_scale and model_type == EK.SVC or model_type == EK.SVM:
        logging.warn(f"{model_type.value} benefit from scaling, it might be good to rerun with the -s or --scale flag")
        
    if should_scale:
        if model_type == EK.RF:
            logging.warn("Random forrest doesn't benefit from scaling the data, it might be beneficial to remove the -s or --scale flag.")
        logging.info("Scaling the data")
        scaler = StandardScaler().fit(xs,np.array(ys))
        xs = scaler.transform(xs)
        xs_test = scaler.transform(xs_test)
        if isinstance(xs_test,spmatrix) or isinstance(xs,spmatrix):
            exit()
    
    clf = get_model(model_type,xs,ys,optimise,n_jobs)
    
    if isinstance(clf,RandomizedSearchCV):
        logging.info("- Search resulted in -")
        logging.info(f"Best Estimator: {clf.best_estimator_}")
        logging.info(f"Best Index: {clf.best_index_}")
        logging.info(f"Best Params: {clf.best_params_}")
        logging.info(f"Best Score: {clf.best_score_}")

    y_pred = clf.predict(xs_test)
    
    logging.info(f"Cross val score:\n{cross_val_score(clf, xs, ys, cv=3, scoring='accuracy')}")
    logging.info(f"Classification Report for training set:\n{classification_report(ys,cross_val_predict(clf,xs,ys))}")
    logging.info(f"Classification Report for test set:\n{classification_report(ys_test,y_pred,digits=4,zero_division=1)}")
    logging.info(f"Probabilities:\n{[(x,y) for (x,y) in zip(ys_test,clf.predict_proba(xs_test))]}")
    
    cm = confusion_matrix(ys_test,y_pred)
    display = ConfusionMatrixDisplay(cm,display_labels=clf.classes_)
    display.plot()
    matplotlib.pyplot.savefig(f"{BASE_PATH}/cm-{CURRENT_DATE_time_str}")
    
    if not out_path.exists():
        logging.info(f"Couldn't find {out_path.name}, so created it.")
        out_path.touch()

    from joblib import dump
    dump(clf, out_path)

if __name__ == "__main__":
  main()

import argparse
import datetime
import logging
import os
from pathlib import Path
from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from scipy.sparse import spmatrix
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sign.training.load_data.dynamic_loader import DynamicLoader
from sign.CONST import AMOUNT_OF_KEYFRAMES
from collections import Counter

# Setup Logging
CURRENT_DATE = datetime.datetime.now().strftime("%d-%m-%Y")
RANDOM_STATE = 422
BASE_PATH = CURRENT_DATE
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

def find_hyper_parameters(estimator:BaseEstimator,parameters:dict,xs:np.ndarray,ys:tuple[str],n_jobs=-1):
    pre_clf = RandomizedSearchCV(estimator,parameters,n_jobs=n_jobs,verbose=2,random_state=RANDOM_STATE,pre_dispatch=2)
    logging.info("Searching for best hyper parameters")
    pre_clf.fit(xs,ys)
    return pre_clf


    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", 
                        help="The .csv containing the input data.",
                        type=str)

    parser.add_argument("model",
                        choices=["lr","rf","svc","svm","vc","bc"],
                        help="The model that you wish to use",
                        type=str)
    parser.add_argument("--scale","-s",
                        help="Should the input be scaled ?",
                        dest="scale",
                        action='store_true')
    parser.add_argument("--out", 
                        help="name of the out file.",
                        required=False,
                        dest="out",
                        type=str)
    args = parser.parse_args()

    input_path = Path(args.input)
    model_type = args.model
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
    
    clf:BaseEstimator
    parameters:dict
    xs,ys,xs_test,ys_test = load_csv(input_path)
    n_jobs = -1
    logging.info(f"training set: {Counter(ys)}")
    logging.info(f"test set: {Counter(ys_test)}")
    if should_scale:
        logging.info("Scaling the data")
        scaler = StandardScaler().fit(xs,np.array(ys))
        xs = scaler.transform(xs)
        xs_test = scaler.transform(xs_test)
        if isinstance(xs_test,spmatrix) or isinstance(xs,spmatrix):
            exit()
            
    if model_type == "lr":
        clf = LogisticRegression(random_state=RANDOM_STATE,max_iter=10000)
        parameters = {'C':range(10,1001,20)}
        
    if model_type == "svc" or model_type == "svm":
        clf = SVC(probability=model_type=="svc") #  Note that the same scaling must be applied to the test vector to obtain meaningful results. 
        parameters = {'C':[float(x) for x in range(100,501,20)],"gamma":[x * 0.1 for x in range(30,51,1)]}

    if model_type == "rf":
        clf = RandomForestClassifier()
        parameters = {"max_features":["sqrt","log2"],"n_estimators":range(100,1001,100)}
    
    if model_type == "vc":
        raise NotImplementedError
        lr = LogisticRegression(C=930.0,max_iter=10_000)
        rf = RandomForestClassifier(random_state=RANDOM_STATE,n_estimators=500,max_features="sqrt")
        svc = make_pipeline(StandardScaler(),SVC(random_state=RANDOM_STATE,probability=True,gamma=0.4,C=400.0)) # remember probability
        clf = VotingClassifier( estimators=[ 
                                                ('lr', lr), 
                                                ('rf', rf), 
                                                ('svc', svc)
        ]) 
        parameters = {"voting":["hard","soft"]}
    if model_type == "bc":
        raise NotImplementedError
    
    best_clf = find_hyper_parameters(clf,parameters,xs,ys)
    logging.info(f"Best Estimator: {best_clf.best_estimator_}")
    logging.info(f"Best Index: {best_clf.best_index_}")
    logging.info(f"Best Params: {best_clf.best_params_}")
    logging.info(f"Best Score: {best_clf.best_score_}")

    y_pred = best_clf.predict(xs_test)
    logging.info(xs.shape)
    logging.info(xs_test.shape)
    logging.info(Counter(y_pred))
    logging.info(Counter(ys_test))
    logging.info(f"Classification Report:\n{classification_report(ys_test,y_pred,digits=4)}")
    from joblib import dump
    
    dump(best_clf, out_path)

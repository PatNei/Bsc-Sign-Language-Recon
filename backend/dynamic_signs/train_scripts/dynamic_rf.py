import numpy as np
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV

from sign.CONST import AMOUNT_OF_KEYFRAMES

from sign.training.load_data.dynamic_loader import DynamicLoader

CSV_PATH = '../new_youtube.csv'
NUM_HANDS = 2
print("Loading data")
dyna_lod = DynamicLoader(AMOUNT_OF_KEYFRAMES)
training_data = dyna_lod.prepare_training_data(CSV_PATH)
_xs,ys,_xs_test,ys_test = training_data.spliterino(random_state=1)
_xs,_xs_test = np.array(_xs),np.array(_xs_test)
print("data laoded")


from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier

print("Scaling")
random_forest = RandomForestClassifier()
scaler = StandardScaler(copy=True).fit(_xs) 
xs = scaler.transform(_xs) # remember it might be best to do this for the training data and never for the test set 😈
xs_test = scaler.transform(_xs_test)
parameters = {"max_features":["sqrt","log2"],"n_estimators":range(100,1001,100)}
pre_clf = RandomizedSearchCV(random_forest,parameters,n_jobs=1,verbose=3)
print("Searching for best hyper parameters")
pre_clf.fit(xs,ys)
print(pre_clf.best_estimator_,pre_clf.best_index_,pre_clf.best_params_,pre_clf.best_score_)
print(classification_report(ys_test,pre_clf.predict(xs_test),digits=4)) # type: ignore

if True:
    from joblib import dump
    dump(pre_clf, 'dynamic_rf.joblib')


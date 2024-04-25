import numpy as np
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV

from sign.CONST import AMOUNT_OF_KEYFRAMES

from sign.training.load_data.dynamic_loader import DynamicLoader

CSV_PATH = '../youtube.csv'
NUM_HANDS = 2
print("Loading data")
dyna_lod = DynamicLoader(AMOUNT_OF_KEYFRAMES)
training_data = dyna_lod.prepare_training_data(CSV_PATH)
_xs,ys,_xs_test,ys_test = training_data.spliterino(random_state=1)
xs,xs_test = np.array(_xs),np.array(_xs_test)
print("data laoded")


from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
print("Scaling")
scaler = StandardScaler(copy=True).fit_transform(xs) # remember it might be best to do this for the training data and never for the test set 😈
parameters = {'C':[float(x) for x in range(100,501,20)],"gamma":[x * 0.1 for x in range(30,51,1)]}
pre_clf = RandomizedSearchCV(SVC(),parameters,n_jobs=-1,verbose=3)
print("Searching for best hyper parameters")
pre_clf.fit(xs,ys)
print(pre_clf.best_estimator_,pre_clf.best_index_,pre_clf.best_params_,pre_clf.best_score_)
print(classification_report(ys_test,pre_clf.predict(xs_test),digits=4))

if True:
    from joblib import dump
    dump(pre_clf, 'dynamic_svm.joblib')


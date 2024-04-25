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
_xs,xs_test = np.array(_xs),np.array(_xs_test)
print("data laoded")


from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline

logistic_reg = LogisticRegression(random_state=42,max_iter=10000)
parameters = {'C':range(10,1001,20)}
pre_clf = RandomizedSearchCV(logistic_reg,parameters,n_jobs=-1)
pre_clf.fit(np.array(xs),ys)
print(pre_clf.best_estimator_,pre_clf.best_index_,pre_clf.best_params_,pre_clf.best_score_)
print(classification_report(ys_test,pre_clf.predict(np.array(xs_test)),digits=4))

if True:
    from joblib import dump
    dump(pre_clf, 'dynamic_lr.joblib')

import numpy as np
import scipy.stats
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sign.CONST import AMOUNT_OF_KEYFRAMES
from sign.training.load_data.dynamic_loader import DynamicLoader
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

CSV_PATH = 'sign/data/dynamic_train/dyn_50_common_youtube_55p.csv'
NUM_HANDS = 2

dyna_lod = DynamicLoader(AMOUNT_OF_KEYFRAMES)
training_data = dyna_lod.prepare_training_data(CSV_PATH)
xs,ys,xs_test,ys_test = training_data.spliterino(random_state=1)


# Hvis gini scoren er for høj, kan det så betale sig at fjerne de cases hvor den går i stykker eller vil det bare få modellen til at overfitte?
#Jeg er her fra nano :)
     
#tree_clf = DecisionTreeClassifier(max_depth=2, random_state=148)
#tree_clf.fit(xs,ys)
#bob2 = [x.lower() for x in tree_clf.predict(xs_test)]
#bob3 = [x.lower() for x in ys_test]
#print(classification_report(bob3,bob2))
#hello = [i for (i,label) in enumerate(ys) if label == "To" ]
# [xs[index] for index in hello]

# logistic_far = LogisticRegression(random_state=42,max_iter=500,C=90)
# parameters = {'C':range(90,1000,20)}

# pre_clf = RandomizedSearchCV(logistic_far,parameters,n_jobs=-1)
# pre_clf.fit(np.array(xs),ys)

#clf = GridSearchCV(logistic_far, parameters,n_jobs=-1)
#clf.fit(np.array(xs), ys)

#logistic_far.fit(xs,ys)
#print(classification_report(ys_test,logistic_far.predict(xs_test)))
"""
voting_clf = VotingClassifier( estimators=[ 
                                           ('lr', ), 
                                           ('rf', RandomForestClassifier(random_state=42)), 
                                           ('svc', SVC(random_state=42,probability=True))
]) 
#voting_clf.fit(xs, ys)
"""


#logistic_far_2 = LogisticRegression(random_state=42,max_iter=500,C=90)
def main():
    svc_testo = RandomForestClassifier()
    parameters = {"max_features":["sqrt","log2"],"n_estimators":range(100,1001,100)}
    pre_clf = RandomizedSearchCV(svc_testo,parameters)
    pre_clf.fit(np.array(xs),ys)
    print(pre_clf.best_estimator_,pre_clf.best_index_,pre_clf.best_params_,pre_clf.best_score_)

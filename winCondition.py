from mongoManager import MongoManager
from matchAnalyzer import MatchAnalysis
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
import numpy as np
from collections import Counter
import pickle

class WinCondition:

    def __init__(self):
        self.loaded_model = pickle.load(open("winnerPredictorRF.pkl", 'rb'))

    def predict(self, match):
        iM = MatchAnalysis(match)
        print("Actually won",iM.winner)
        for partObj in iM.participants:
            partObj.setFeatures()

        X_test = [iM.getGlobalFeatures()]
        result = self.loaded_model.predict(X_test)
        print("prediction",int(result[0]))
        if int(result[0]) != int(iM.winner):
            print("OMG FAILLLLLL")
            
        return result

    def train_model(self):
        iM = MongoManager()
        matches = iM.getMatches()
        notUsable = 0
        usable = 0
        X = []
        y = []
        stdGlobalFeatureNames = None

        for match in matches:
            if match["gameDuration"] // 60 > 15:
                try:
                    iM = MatchAnalysis(match)
                    for partObj in iM.participants:
                        partObj.setFeatures()

                    gfv = iM.getGlobalFeatures()
                    if len(gfv) != 650:
                        print("Wrong feat length", len(gfv))
                        continue
                    else:
                        if not stdGlobalFeatureNames:
                            stdGlobalFeatureNames = iM.globalFeatureNames

                    X.append(gfv)
                    y.append(iM.winner)
                    usable+=1
                except:
                    notUsable+=1
                    continue

        print(X[0])
        print("usable",usable)
        print("not usable",notUsable)
        print(Counter(y))
        clf2 = RandomForestClassifier()
        #cv = KFold(n_splits=10)
        clf2.fit(X,y)
        #pipeline2 = Pipeline([('estimator', clf2)])
        #scores = cross_val_score(pipeline2, X, y, cv = cv)
        #print("Results",np.mean(scores))
        filename = 'winnerPredictorRF.pkl'
        pickle.dump(clf2, open(filename, 'wb'))
        
        '''
        # load the model from disk
        loaded_model = pickle.load(open(filename, 'rb'))
        result = loaded_model.score(X_test, Y_test)
        print(result)
        '''

if __name__ == "__main__":
    iW = WinCondition()
    #iW.train_model()
    
    iMO = MongoManager()
    matches = iMO.getMatches(100)
    for match in matches:
        iW.predict(match)

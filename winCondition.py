from mongoManager import MongoManager
from matchAnalyzer import MatchAnalysis
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
import numpy as np
from collections import Counter
class WinCondition:

    def __init__(self):
        iM = MongoManager()
        matches, timelines = iM.getAllMatchesAndTimelines()
        notUsable = 0
        usable = 0
        X = []
        y = []
        
        for match, timeline in zip(matches,timelines):    
            if match["gameDuration"] // 60 > 15:
                try:
                    iM = MatchAnalysis(match, timeline)
                    for partObj in iM.participants:
                        partObj.setFeatures()

                    gfv = iM.getGlobalFeatures()
                    if len(gfv) != 620:
                        print("Wrong feat length", len(gfv))
                        continue

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
        cv = KFold(n_splits=10)
        pipeline2 = Pipeline([('estimator', clf2)])
        scores = cross_val_score(pipeline2, X, y, cv = cv)
        print("Results",np.mean(scores))

if __name__ == "__main__":
    iW = WinCondition()
from mongoManager import MongoManager
from matchAnalyzer import MatchAnalysis
from pprint import pprint
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

class SmurfDetector:

    def __init__(self):
        pass

    def buildDataset(self):
        iM = MongoManager()
        matches = iM.getMatches()
        X = []
        y = []
        
        #TODO Save feature order mapping, so info gain is meaningful
        #TODO ENCODE y in numeric values and save mapping

        for match in matches:
            for participant in match["participantIdentities"]:
                idP = participant["participantId"]
                summonerId = participant["player"]["summonerId"]
                player = iM.findBySummonerId(summonerId)
                if player:
                    wr = player["wins"] / (player["wins"] + player["losses"])
                    label = "ABOVE_DIAMOND"
                    if "tier" in player:
                        label = player["tier"]+"_"+player["rank"]

                    iMA = MatchAnalysis(match)
                    partObj = iMA.participantsById[idP]
                    partObj.setRankInfo(label,wr)
                    partObj.setFeatures()
                    features = partObj.featureVector                  
                    X.append(features)
                    y.append(label)
                    #pprint(features)
                    #print(label)
                    #print("---------------------")

        clf = RandomForestClassifier()
        print("Training....")
        print(np.mean(cross_val_score(clf, X, y, cv=10)))
        

if __name__ == "__main__":
    iSD = SmurfDetector()
    iSD.buildDataset()
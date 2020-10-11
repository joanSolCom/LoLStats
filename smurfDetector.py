from mongoManager import MongoManager
from matchAnalyzer import MatchAnalysis
from pprint import pprint
import numpy as np
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from collections import Counter
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

acceptedRoles = ["NONE_JUNGLE","SOLO_TOP","DUO_CARRY_BOTTOM","SOLO_MIDDLE","DUO_SUPPORT_BOTTOM"]

class SmurfDetector:

    def __init__(self):
        pass

    def generateArff(self, role = None):
        arff = None
        iM = MongoManager()
        if not role:
            role = acceptedRoles

        matches = iM.getMatches()
        NInst = 0

        for match in matches:
            for participant in match["participantIdentities"]:
                idP = participant["participantId"]
                summonerId = participant["player"]["summonerId"]
                participantStats = match["participants"][idP-1]
                player = iM.findBySummonerId(summonerId)

                if player:
                    wr = player["wins"] / (player["wins"] + player["losses"])
                    label = "ABOVE_DIAMOND"
                    if "tier" in player:
                        label = player["tier"]#+"_"+player["rank"]

                    iMA = MatchAnalysis(match)
                    partObj = iMA.participantsById[idP]
                    if partObj.position in role:
                        partObj.setRankInfo(label,wr)
                        partObj.setFeatures()

                        if not arff:
                            fnames = partObj.featureNames
                            arff = "@relation league\n"
                            for feat in fnames:
                                arff+= "@attribute " + feat +" numeric\n"
                            arff+="@attribute class {IRON,SILVER,GOLD,BRONZE,PLATINUM,DIAMOND,ABOVE_DIAMOND}\n@data\n"

                        line=""
                        for feat in partObj.featureVector:
                            line+=str(feat) + ","
                        line+=label+"\n"
                        arff+=line
        return arff

    def train(self):
        iM = MongoManager()
        matches = iM.getMatches()
        X = []
        y = []
        NInst = 0

        for match in matches:
            for participant in match["participantIdentities"]:
                idP = participant["participantId"]
                summonerId = participant["player"]["summonerId"]
                participantStats = match["participants"][idP-1]
                player = iM.findBySummonerId(summonerId)

                if player:
                    wr = player["wins"] / (player["wins"] + player["losses"])
                    label = "ABOVE_DIAMOND"
                    if "tier" in player:
                        label = player["tier"]#+"_"+player["rank"]

                    iMA = MatchAnalysis(match)
                    partObj = iMA.participantsById[idP]
                    if partObj.position in acceptedRoles:
                        partObj.setRankInfo(label,wr)
                        partObj.setFeatures()
                        features = partObj.featureVector                  
                        X.append(features)
                        y.append(label)
                        NInst+=1

        clf = SVC(kernel="linear")
        clf2 = RandomForestClassifier()
        scalar = StandardScaler()
        cv = KFold(n_splits=10)

        print("Training....")
        print(NInst, "instances")
        
        pipeline = Pipeline([('transformer', scalar), ('estimator', clf)])
        pipeline2 = Pipeline([('estimator', clf2)])

        scores = cross_val_score(pipeline, X, y, cv = cv)
        print("Results SVM",np.mean(scores))
        
        scores2 = cross_val_score(pipeline2, X, y, cv = cv)
        print("Results Random Forests",np.mean(scores2))

    def trainPerRole(self):
        iM = MongoManager()
        matches = iM.getMatches()
        X_per_role = {}
        y_per_role = {}

        #TODO Save feature order mapping, so info gain is meaningful
        #TODO ENCODE y in numeric values and save mapping
        featNames = None
        for match in matches:
            for participant in match["participantIdentities"]:
                idP = participant["participantId"]
                summonerId = participant["player"]["summonerId"]
                participantStats = match["participants"][idP-1]
                role = participantStats["timeline"]["role"] + "_" + participantStats["timeline"]["lane"]
                player = iM.findBySummonerId(summonerId)

                if player:
                    if role not in X_per_role:
                        X_per_role[role] = []
                    if role not in y_per_role:
                        y_per_role[role] = []

                    wr = player["wins"] / (player["wins"] + player["losses"])

                    label = "ABOVE_DIAMOND"
                    if "tier" in player:
                        label = player["tier"]#+"_"+player["rank"]

                    iMA = MatchAnalysis(match)
                    partObj = iMA.participantsById[idP]
                    if partObj.position in acceptedRoles:
                        partObj.setRankInfo(label,wr)
                        partObj.setFeatures()
                        if not featNames:
                            featNames = partObj.featureNames

                        features = partObj.featureVector                  
                        X_per_role[role].append(features)
                        y_per_role[role].append(label)

        clf = SVC()
        clf2 = RandomForestClassifier()
        scalar = StandardScaler()
        cv = KFold(n_splits=10)
        
        for role in X_per_role.keys():
            NInst = len(X_per_role[role])
            if NInst < 10:
                continue

            print("Training....", role)
            print(featNames)
            print("Class distribution per role", Counter(y_per_role[role]))
            print(NInst, "instances for", role)
            #y_pred = cross_val_predict(clf, X_per_role[role], y_per_role[role], cv=10)
            #for yreal, ypred in zip(y_per_role[role], y_pred):
            #    print("real:",yreal,"predicted:",ypred)
            
            #print(confusion_matrix(y_per_role[role], y_pred))
            
            pipeline = Pipeline([('transformer', scalar), ('estimator', clf)])
            pipeline2 = Pipeline([('estimator', clf2)])

            scores = cross_val_score(pipeline, X_per_role[role], y_per_role[role], cv = cv)
            print("Results SVM",np.mean(scores))
            
            scores2 = cross_val_score(pipeline2, X_per_role[role], y_per_role[role], cv = cv)
            print("Results Random Forests",np.mean(scores2))

if __name__ == "__main__":
    iSD = SmurfDetector()
    arff = iSD.generateArff(["DUO_SUPPORT_BOTTOM"])
    fd = open("trainWekaSupport.arff","w")
    fd.write(arff)
    fd.close()
    exit()
    #iSD.trainPerRole()
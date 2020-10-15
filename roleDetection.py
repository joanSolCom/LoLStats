import roleml
from mongoManager import MongoManager
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
import numpy as np
import pickle
from pprint import pprint

class RoleDetection:

    def __init__(self):
        self.loaded_model = pickle.load(open("roleDetector.pkl", 'rb'))

    def predict(self, match):
        dictPositions = {}
        dictProbas = {}

        for participant in match["participants"]:
            idCurrent = participant["participantId"]
            teamCurrent = participant["teamId"]
            features = {}
            features["champ"] = participant["championId"]
            features["spell1"] = participant["spell1Id"]
            features["spell2"] = participant["spell2Id"]
            stats = participant["stats"]
            for i in range(0,7):
                features["item"+str(i)] = stats["item"+str(i)]
            
            teamMateCount = 1
            for participant in match["participants"]:
                if participant["participantId"] != idCurrent and participant["teamId"] == teamCurrent:
                    features["teammate"+str(teamMateCount)] = participant["championId"]
                    teamMateCount+=1
            
            features["totalDamageDealt"] = stats["totalDamageDealt"]
            features["visionScore"] = stats["visionScore"]
            features["goldEarned"] = stats["goldEarned"]
            features["wardsPlaced"] = stats["wardsPlaced"]
            features["wardsKilled"] = stats["wardsKilled"]
            features["neutralMinionsKilledTeamJungle"] = stats["neutralMinionsKilledTeamJungle"]
            features["neutralMinionsKilled"] = stats["neutralMinionsKilled"]
            features["neutralMinionsKilledEnemyJungle"] = stats["neutralMinionsKilledEnemyJungle"]
            features["totalMinionsKilled"] = stats["totalMinionsKilled"]
            
            features["totalHeal"] = stats["totalHeal"]
            features["totalDamageDealtToChampions"] = stats["totalDamageDealtToChampions"]
            features["damageSelfMitigated"] = stats["damageSelfMitigated"]
            features["damageDealtToTurrets"] = stats["damageDealtToTurrets"]

            order = sorted(features.keys())
            featVector = []
            for fname in order:
                featVector.append(features[fname])
            
            X = [featVector]

            result = self.loaded_model.predict(X)[0]
            probas = self.loaded_model.predict_proba(X)
            dictPositions[idCurrent] = result
            dictProbas[idCurrent] = probas

        return dictPositions , dictProbas

    def train_model(self):
        iM = MongoManager()
        fullmatches = iM.getAllMatchesAndTimelines(35000)
        X = []
        y = []

        for fm in fullmatches:
            match = fm["match"]
            timeline = fm["timeline"]
            if match["gameDuration"] // 60 > 15:
                realRoles = roleml.predict(match, timeline)
                rolesDetected = set(realRoles.values())
                if len(rolesDetected) < 5:
                    print("ERROOOOOOR", realRoles)
                else:
                    for participant in match["participants"]:
                        idCurrent = participant["participantId"]
                        teamCurrent = participant["teamId"]
                        
                        roleGold = realRoles[idCurrent]
                        features = {}
                        features["champ"] = participant["championId"]
                        features["spell1"] = participant["spell1Id"]
                        features["spell2"] = participant["spell2Id"]
                        stats = participant["stats"]
                        for i in range(0,7):
                            features["item"+str(i)] = stats["item"+str(i)]
                        
                        
                        teamMateCount = 1
                        for participant in match["participants"]:
                            if participant["participantId"] != idCurrent and participant["teamId"] == teamCurrent:
                                features["teammate"+str(teamMateCount)] = participant["championId"]
                                teamMateCount+=1
                        
                        features["totalDamageDealt"] = stats["totalDamageDealt"]
                        features["visionScore"] = stats["visionScore"]
                        features["goldEarned"] = stats["goldEarned"]
                        features["wardsPlaced"] = stats["wardsPlaced"]
                        features["wardsKilled"] = stats["wardsKilled"]
                        features["neutralMinionsKilledTeamJungle"] = stats["neutralMinionsKilledTeamJungle"]
                        features["neutralMinionsKilled"] = stats["neutralMinionsKilled"]
                        features["neutralMinionsKilledEnemyJungle"] = stats["neutralMinionsKilledEnemyJungle"]
                        features["totalMinionsKilled"] = stats["totalMinionsKilled"]
                        
                        features["totalHeal"] = stats["totalHeal"]
                        features["totalDamageDealtToChampions"] = stats["totalDamageDealtToChampions"]
                        features["damageSelfMitigated"] = stats["damageSelfMitigated"]
                        features["damageDealtToTurrets"] = stats["damageDealtToTurrets"]

                        order = sorted(features.keys())
                        featVector = []
                        for fname in order:
                            featVector.append(features[fname])
                        
                        X.append(featVector)
                        y.append(roleGold)

        clf2 = RandomForestClassifier()
        #clf2.fit(X,y)
        cv = KFold(n_splits=10)
        pipeline2 = Pipeline([('estimator', clf2)])
        scores = cross_val_score(pipeline2, X, y, cv = cv)
        print("Results",np.mean(scores))
        #filename = 'roleDetector.pkl'
        #pickle.dump(clf2, open(filename, 'wb'))
                    

if __name__ == "__main__":
    iR = RoleDetection()
    #iR.train_model()
    

    iMO = MongoManager()
    
    matches = iMO.getMatches()
    wrong = []

    for match in matches:
        positions, probas = iR.predict(match)
        if len(set(positions.values())) != 5:
            print(positions, probas)
            wrong.append(match["gameId"])
    
    print(wrong)
            
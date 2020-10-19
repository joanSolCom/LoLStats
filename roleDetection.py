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

api_roles = ["DUO_SUPPORT_BOTTOM", "DUO_CARRY_BOTTOM","SOLO_TOP", "NONE_JUNGLE","SOLO_MIDDLE"]
mappings = {}
mappings["DUO_SUPPORT_BOTTOM"] = "supp"
mappings["DUO_CARRY_BOTTOM"] = "bot"
mappings["SOLO_TOP"] = "top"
mappings["NONE_JUNGLE"] = "jungle"
mappings["SOLO_MIDDLE"] = "mid"

proba_positions = {}
proba_positions["bot"] = 0
proba_positions["jungle"] = 1
proba_positions["mid"] = 2
proba_positions["supp"] = 3
proba_positions["top"] = 4

roles_team = ["bot","supp","mid","jungle","top"]

class RoleDetection:

    def __init__(self):
        self.loaded_model = pickle.load(open("roleDetector_enriched.pkl", 'rb'))

    def getFeatures(self, participant, match):
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

        return featVector

    def rules_pre(self, match):
        dictPositions = {}
        dictProbas = {}

        team1roles = []
        team2roles = []

        #team 100
        for idx in range(0,5):
            role = match["participants"][idx]["timeline"]["role"] + "_" + match["participants"][idx]["timeline"]["lane"]
            if role in api_roles:
                team1roles.append(mappings[role])
            else:
                team1roles = None
                break
        
        if team1roles:
            if len(set(team1roles)) == 5:
                for idx in range(0,5):
                    dictPositions[str(idx+1)] = team1roles[idx]
                    dictProbas[str(idx+1)] = "api said so"

        #team 200
        for idx in range(5,10): 
            role = match["participants"][idx]["timeline"]["role"] + "_" + match["participants"][idx]["timeline"]["lane"]
            if role in api_roles:
                team2roles.append(mappings[role])
            else:
                team2roles = None
                break

        if team2roles:
            if len(set(team2roles)) == 5:
                for idx in range(5,10):
                    dictPositions[str(idx+1)] = team2roles[idx-5]
                    dictProbas[str(idx+1)] = "api said so"
        
        return dictPositions, dictProbas

    def rules_post(self, dictPositions, dictProbas, team, idTeam):
        roleIds = {}
        #print("BEFORE",dictPositions, dictProbas)

        for role in roles_team:
            roleIds[role] = []

        offset = 1
        if idTeam == 2:
            offset = 6

        for idMember, role in enumerate(team):
            roleIds[role].append(idMember + offset)

        toCover = []
        for role, memberList in roleIds.items():
            if len(memberList) == 0:
                #print("We need a", role)
                toCover.append(role)

        toAssign = []

        #we select the repeated role that has more probability of having the role and remove it from the pendings
        for role, memberList in roleIds.items():
            #we got repeated roles
            toDel = None
            if len(memberList) > 1:
                #print("We have several",role)
                maxProba = 0
                for i, member in enumerate(memberList):
                    proba = dictProbas[str(member)][0][proba_positions[role]]
                    if proba > maxProba:
                        chosenOne = member
                        maxProba = proba
                        toDel = i
                
                del memberList[toDel]
                #print("ChosenOne is", chosenOne, "with",maxProba)

                for member in memberList:
                    toAssign.append(member)
                
        #then the remaining roles are assigned to the remaining unassigned members        
        for roleToCover in toCover:
            for idx, member in enumerate(toAssign):
                maxProba = -1
                assignedMember = ""
                proba = dictProbas[str(member)][0][proba_positions[roleToCover]]
                if proba > maxProba:
                    maxProba = proba
                    assignedMember = member
                    toDel = idx

            #print("chosenOne for",roleToCover,"is",assignedMember,"with",maxProba)
            dictPositions[str(assignedMember)] = roleToCover
            #print("assigning",assignedMember, roleToCover)
            del toAssign[toDel]
              
        
        #print("AFTER",dictPositions)
        #print()
        return dictPositions


    def predict(self, match):
        #preprocess. If api gives what we want, we just use it
        dictPositions, dictProbas = self.rules_pre(match)

        for participant in match["participants"]:
            idCurrent = str(participant["participantId"])
            #if this guy was in a team that was not well tagged by the api, we use our ML model
            if idCurrent not in dictPositions:
                featVector = self.getFeatures(participant, match)
                X = [featVector]
                result = self.loaded_model.predict(X)[0]
                probas = self.loaded_model.predict_proba(X)
                dictPositions[idCurrent] = result
                dictProbas[idCurrent] = probas
        
        team1 = [dictPositions["1"],dictPositions["2"],dictPositions["3"],dictPositions["4"],dictPositions["5"]]
        team2 = [dictPositions["6"],dictPositions["7"],dictPositions["8"],dictPositions["9"],dictPositions["10"]]
        
        #if one of the team has repeated roles, we postprocess
        if len(set(team1)) != 5:
            #print("Team 1 needs postprocessing")
            self.rules_post(dictPositions, dictProbas, team1, 1)

        if len(set(team2)) != 5:
            #print("Team 2 needs postprocessing")
            self.rules_post(dictPositions, dictProbas, team2, 2)

        return dictPositions

    def train_model(self):
        iM = MongoManager()
        fd = open("toAddModel.txt","r")
        raw = fd.read()
        keyfullmatches = raw.split("\n")

        fullmatches = iM.getAllMatchesAndTimelines(35000)
        keyfullmatches = iM.getSpecificFullmatches(keyfullmatches)
        fullmatches.extend(keyfullmatches)
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
                        featVector = self.getFeatures(participant, match)
                        roleGold = realRoles[idCurrent]

                        X.append(featVector)
                        y.append(roleGold)

        clf2 = RandomForestClassifier()
        clf2.fit(X,y)
        #cv = KFold(n_splits=10)
        #pipeline2 = Pipeline([('estimator', clf2)])
        #scores = cross_val_score(pipeline2, X, y, cv = cv)
        #print("Results",np.mean(scores))
        filename = 'roleDetector_enriched.pkl'
        pickle.dump(clf2, open(filename, 'wb'))
                    

if __name__ == "__main__":
    iR = RoleDetection()
    #iR.train_model()
    iMO = MongoManager()
    
    matches = iMO.getMatches()
    wrong = []

    for match in matches:
        if match["gameDuration"] // 60 > 15:
            positions = iR.predict(match)
            team1 = [positions["1"],positions["2"],positions["3"],positions["4"],positions["5"]]
            team2 = [positions["6"],positions["7"],positions["8"],positions["9"],positions["10"]]
            if len(set(team1)) != 5 or len(set(team2))!= 5:
                print(match["gameId"])
                wrong.append(match["gameId"])
    
    print(len(wrong))
            
from mongoManager import MongoManager
from dataHelper import DataHelper
from matchAnalyzer import MatchAnalysis

class Score:
    
    def __init__(self, match, verbose=True):
        self.match = match
        self.weights = self.loadWeights()
        self.featureTotals = self.getFeatureTotals()
        self.scorePlayers(verbose)
    
    def loadWeights(self, path="scoringWeights.tsv"):
        fd = open(path, "r")
        raw = fd.read()
        lines = raw.split("\n")
        featureWeightsPerCategory = {}
        self.diffFeats = []

        for line in lines:
            featType, featName, weight = line.split()
            if featType == "diffFeats":
                self.diffFeats.append(featName)

            if featType not in featureWeightsPerCategory:
                featureWeightsPerCategory[featType] = []
            
            featureWeightsPerCategory[featType].append((featName,float(weight)))
        
        return featureWeightsPerCategory

    def getFeatureTotals(self):
        featureTotals = {}
        self.iM = MatchAnalysis(self.match)
        for partObj in self.iM.participants:
            partObj.setFeatures()

            for key, value in partObj.features.items():
                if key not in featureTotals and value != -1:
                    featureTotals[key] = 1.0

                if key in self.diffFeats:
                    if value > 0:
                        featureTotals[key]+=float(value)
                else:
                    if value != -1:
                        featureTotals[key]+=float(value)
        
        featureTotals["longestTimeSpentLiving"] = self.match["gameDuration"] // 60

        return featureTotals
    
    def scorePlayers(self, verbose=True):
        if verbose:
            print(self.iM.date)
            print("Winner",self.iM.winner, self.match["gameDuration"]//60, "minutes")
        
        for team in self.iM.teams:
            if verbose:
                print("TEAM: ", team.teamId)

            for partObj in team.participants:
                partObj.setFeatures()
                
                role = partObj.position
                champ = partObj.champion
                #print()
                #print(partObj.participantId, champ, role)
                #print(partObj.features["kills"], partObj.features["deaths"], partObj.features["assists"])
                
                feats = partObj.features
                score = 0

                for feat, weight in self.weights["notNorm"]:
                    score += feats[feat] * weight
                    #print(feat, feats[feat])

                for feat, weight in self.weights["all"]:
                    if feats[feat] != -1:
                        featScore = weight * (feats[feat] / self.featureTotals[feat])
                        score += featScore
                        #print(feat, featScore, feats[feat], self.featureTotals[feat])

                for feat, weight in self.weights["diffFeats"]:
                    if feats[feat] != -1:
                        featScore = weight * (feats[feat] / self.featureTotals[feat])
                        score += featScore
                        #print(feat, featScore, feats[feat], self.featureTotals[feat])

                for feat, weight in self.weights[role]:
                    if feats[feat] != -1:
                        featScore = weight * (feats[feat] / self.featureTotals[feat])
                        score += featScore
                        #print(feat, featScore, feats[feat], self.featureTotals[feat])

                partObj.score = score        
                if verbose:
                    print(partObj.participantId, partObj.summonerName ,champ, role, partObj.position, partObj.spell1, partObj.spell2, partObj.features["kills"], partObj.features["deaths"], partObj.features["assists"], "\t",score)
    
        if verbose:   
            print()
    
    def getScoreOfPlayer(self, summonerId):
        allScores = []
        playerScore = None
        for team in self.iM.teams:
            for partObj in team.participants:
                allScores.append(partObj.score)
                if partObj.summonerId == summonerId:
                    playerScore = partObj.score

        return playerScore, allScores


if __name__ == "__main__":
    iMo = MongoManager()
    matches = iMo.getMatches(150)
    for match in matches:    
        if match["gameDuration"] // 60 > 15: 
            iPS = Score(match)
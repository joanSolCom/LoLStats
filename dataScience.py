from mongoManager import MongoManager
import numpy as np
from matchAnalyzer import MatchAnalysis
from scipy.stats import mode
import json
from pprint import pprint

acceptedRoles = ["NONE_JUNGLE","SOLO_TOP","DUO_CARRY_BOTTOM","SOLO_MIDDLE","DUO_SUPPORT_BOTTOM"]

class DataScienceOMG:

    def __init__(self):
        pass

    def meanFeatureValuesPerRoleAndRank(self):
        iM = MongoManager()
        matches = iM.getMatches()
        dictResults = {}
        NInstances = 0

        for match in matches:
            for participant in match["participantIdentities"]:
                idP = participant["participantId"]
                summonerId = participant["player"]["summonerId"]
                participantStats = match["participants"][idP-1]
                role = participantStats["timeline"]["role"] + "_" + participantStats["timeline"]["lane"]
                player = iM.findBySummonerId(summonerId)

                if player:
                    
                    wr = player["wins"] / (player["wins"] + player["losses"])
                    rank = "ABOVE_DIAMOND"
                    if "tier" in player:
                        rank = player["tier"]#+"_"+player["rank"]
                    
                    iMA = MatchAnalysis(match)
                    partObj = iMA.participantsById[idP]
                    if partObj.position in acceptedRoles:
                        NInstances+=1
                        partObj.setRankInfo(rank,wr)
                        partObj.setFeatures()
                        feats = partObj.features

                        for featName, featValue in feats.items():
                            if featName not in dictResults:
                                dictResults[featName] = {}
                            
                            if role not in dictResults[featName]:
                                dictResults[featName][role] = {}

                            if rank not in dictResults[featName][role]:
                                dictResults[featName][role][rank] = []
                            
                            dictResults[featName][role][rank].append(featValue)

        print(NInstances, "usable instances")
        return dictResults

    def stats(self, resultObj):
        means = {}
        for featName, infoFeat in resultObj.items():
            means[featName] = {}
            for role, infoRole in infoFeat.items():
                means[featName][role] = {}
                for rank, listValues in infoRole.items():
                    means[featName][role][rank] = {}
                    means[featName][role][rank]["total_instances"] = len(listValues)
                    means[featName][role][rank]["mean"] = str(np.mean(listValues))
                    means[featName][role][rank]["median"] = str(np.median(listValues))
                    means[featName][role][rank]["max"] = str(np.max(listValues))
                    means[featName][role][rank]["min"] = str(np.min(listValues))
                    means[featName][role][rank]["variance"] = str(np.var(listValues))
                    means[featName][role][rank]["most_freq"] = str(mode(listValues)[0][0])
                    
        with open('dataScience.json', 'w') as outfile:
            json.dump(means, outfile, indent=4)

if __name__ == "__main__":
    iD = DataScienceOMG()
    results = iD.meanFeatureValuesPerRoleAndRank()
    iD.stats(results)
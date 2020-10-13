from mongoManager import MongoManager
from dataHelper import DataHelper
from matchAnalyzer import MatchAnalysis

iMo = MongoManager()
iDH = DataHelper()
matches, timelines = iMo.getAllMatchesAndTimelines(50)
featureTotals = {}

relevantFeaturesPerRole = {}

relevantFeaturesPerRole["notNorm"] = ["doubleKills","tripleKills","quadraKills","pentaKills"]
relevantFeaturesPerRole["all"] = ["kills","assists","longestTimeSpentLiving","xpPerMinDeltaEarlyGame","xpPerMinDeltaMidGame","xpPerMinDeltaLateGame","xpPerMinDeltaEndGame","goldPerMinDeltasEarlyGame","goldPerMinDeltasMidGame","goldPerMinDeltasLateGame","goldPerMinDeltasEndGame","turretKills","inhibitorKills","totalDamageDealt","totalDamageDealtToChampions","csDiffPerMinDeltasEarlyGame","csDiffPerMinDeltasMidGame","csDiffPerMinDeltasLateGame","csDiffPerMinDeltasEndGame","xpDiffPerMinDeltasEarlyGame","xpDiffPerMinDeltasMidGame","xpDiffPerMinDeltasLateGame","xpDiffPerMinDeltasEndGame"]
relevantFeaturesPerRole["jungle"] = ["damageDealtToObjectives","neutralMinionsKilled","neutralMinionsKilledTeamJungle","neutralMinionsKilledEnemyJungle","goldEarned"]
relevantFeaturesPerRole["top"] = ["creepsPerMinDeltaEarlyGame","creepsPerMinDeltaMidGame","creepsPerMinDeltaLateGame","creepsPerMinDeltaEndGame","totalMinionsKilled","goldEarned"]
relevantFeaturesPerRole["supp"] = ["visionScore","visionWardsBoughtInGame","wardsPlaced","wardsKilled"]
relevantFeaturesPerRole["bot"] = ["creepsPerMinDeltaEarlyGame","creepsPerMinDeltaMidGame","creepsPerMinDeltaLateGame","creepsPerMinDeltaEndGame","totalMinionsKilled","goldEarned"]
relevantFeaturesPerRole["mid"] = ["creepsPerMinDeltaEarlyGame","creepsPerMinDeltaMidGame","creepsPerMinDeltaLateGame","creepsPerMinDeltaEndGame","totalMinionsKilled","goldEarned"]
diffFeats = ['csDiffPerMinDeltasEarlyGame' 'csDiffPerMinDeltasMidGame', 'csDiffPerMinDeltasLateGame', 'csDiffPerMinDeltasEndGame', 'xpDiffPerMinDeltasEarlyGame', 'xpDiffPerMinDeltasMidGame', 'xpDiffPerMinDeltasLateGame', 'xpDiffPerMinDeltasEndGame','damageTakenDiffPerMinDeltasEarlyGame', 'damageTakenDiffPerMinDeltasMidGame', 'damageTakenDiffPerMinDeltasLateGame', 'damageTakenDiffPerMinDeltasEndGame']

def getScore(idGame, partObj):
    role = partObj.position
    champ = partObj.champion
    print()
    print(champ, role)
    print(partObj.features["kills"], partObj.features["deaths"], partObj.features["assists"])
    
    feats = partObj.features

    deaths = partObj.features["deaths"] / featureTotals[idGame]["deaths"]
    print("DeathScore", -3 * deaths, partObj.features["deaths"], featureTotals[idGame]["deaths"])
    score = -3 * deaths
    
    for feat in relevantFeaturesPerRole["notNorm"]:
        score += feats[feat]
        print(feat, feats[feat])

    for feat in relevantFeaturesPerRole["all"]:
        if feats[feat] != -1:
            score += feats[feat] / featureTotals[idGame][feat]
            print(feat, feats[feat] / featureTotals[idGame][feat], feats[feat], featureTotals[idGame][feat])

    for feat in relevantFeaturesPerRole[role]:
        if feats[feat] != -1:
            score += feats[feat] / featureTotals[idGame][feat]
            print(feat, feats[feat] / featureTotals[idGame][feat], feats[feat], featureTotals[idGame][feat])
    
    return score

for match, timeline in zip(matches,timelines):    
    if match["gameDuration"] // 60 > 15:
        gameId = match["gameId"]
        featureTotals[gameId] = {}
        iM = MatchAnalysis(match, timeline)

        for partObj in iM.participants:
            partObj.setFeatures()

            for key, value in partObj.features.items():
                if key not in featureTotals[gameId] and value != -1:
                    featureTotals[gameId][key] = 1.0

                if key in diffFeats:
                    if value > 0:
                        featureTotals[gameId][key]+=float(value)
                else:
                    if value != -1:
                        featureTotals[gameId][key]+=float(value)
        
        featureTotals[gameId]["longestTimeSpentLiving"] = match["gameDuration"] // 60
            
for match, timeline in zip(matches,timelines):    
    if match["gameDuration"] // 60 > 15:
        gameId = match["gameId"]
        print("------")
        print("Match Duration", match["gameDuration"] // 60)
        iM = MatchAnalysis(match, timeline)
        for team in iM.teams:
            print("TEAM: ", team.teamId)

            for partObj in team.participants:
                partObj.setFeatures()
                
                score = getScore(gameId, partObj)
                print("SCORE", score)
                print()
        

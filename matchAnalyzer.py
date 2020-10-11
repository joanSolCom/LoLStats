import json
from LoLStats import LolStats
from LoLStats import DataGatherer
from dataHelper import DataHelper

iDH = DataHelper()

class MatchAnalysis:

    def __init__(self, matchObj):
        self.matchDict = matchObj
        self.length = self.matchDict["gameDuration"] #in seconds
        self.date = self.matchDict["gameCreation"]
        self.server = self.matchDict["platformId"]
        self.dg = DataGatherer()
        self.teams = []
        self.teamsById = {}
        self.participants = []
        self.participantsById = {}
        self.winner = None

        for team in self.matchDict["teams"]:
            iT = Team(team)
            if iT.win == "Win":
                self.winner = iT.teamId

            self.teams.append(iT)
            self.teamsById[iT.teamId] = iT

        for pStats, pInfo in zip(self.matchDict["participants"], self.matchDict["participantIdentities"]):           
            iP = Participant(pStats, pInfo, self.length)
            self.participants.append(iP)
            self.participantsById[iP.participantId] = iP
            self.teamsById[iP.teamId].addParticipant(iP)

class Team:
    def __init__(self, teamDict):
        self.participants = []

        self.teamId = str(teamDict["teamId"])
        self.win = teamDict["win"]
        self.firstBlood = teamDict["firstBlood"]
        self.firstTower = teamDict["firstTower"]
        self.firstInhibitor = teamDict["firstInhibitor"]
        self.firstBaron = teamDict["firstBaron"]
        self.firstDragon = teamDict["firstDragon"]
        self.firstRiftHerald = teamDict["firstRiftHerald"]
        self.towerKills = teamDict["towerKills"]
        self.inhibitorKills = teamDict["inhibitorKills"]
        
        self.baronKills = teamDict["baronKills"]
        self.dragonKills = teamDict["dragonKills"]
        self.riftHeraldKills = teamDict["riftHeraldKills"]
        self.inhibitorKills = teamDict["inhibitorKills"]
        self.bans = []

        for banDict in teamDict["bans"]:
            chid = banDict["championId"]
            champ = "No Ban"
            if chid != -1:
                champ = iDH.getChampInfoById(chid).name
            self.bans.append(champ)

    def addParticipant(self, participant):
        self.participants.append(participant)


class Participant:

    def __init__(self, participantStats, participantInfo, gameLength):
        
        self.participantStats = participantStats
        self.gameLength = gameLength
        self.participantId = participantStats["participantId"]
        self.teamId = str(participantStats["teamId"])
        self.champion = iDH.getChampInfoById(participantStats["championId"]).name
        self.championId = participantStats["championId"]
        self.statsDict = participantStats["stats"]
        self.timelineDict = participantStats["timeline"]
        self.role = participantStats["timeline"]["role"]
        self.lane = participantStats["timeline"]["lane"]
        self.position = self.role + "_" + self.lane

        self.accountId = participantInfo["player"]["accountId"]
        self.summonerName = participantInfo["player"]["summonerName"]
        self.summonerId = participantInfo["player"]["summonerId"]

    def setRankInfo(self, rank, winrate):
        self.rank = rank
        self.winrate = winrate

    def setFeatures(self):
        length = self.gameLength // 60 #transform into minutes
        self.features = {}
        stats = self.participantStats["stats"]

        timeline = self.participantStats["timeline"]

        #metaFeatures
        #self.features["win"] = stats["win"]
        self.features["winrate"] = self.winrate
        #self.features["champ"] = self.championId
        
        #TODO ENCODE ROLE
        #self.features["role"] = self.role + "_" + self.lane

        #basic performance measures
        #self.features["kills"] = stats["kills"] #/ length
        self.features["deaths"] = stats["deaths"] #/ length
        #self.features["assists"] = stats["assists"] #/ length
        self.features["goldEarned"] = stats["goldEarned"] #/ length
        #self.features["totalDamageDealt"] = stats["totalDamageDealt"] #/ length
        #self.features["totalDamageDealtToChampions"] = stats["totalDamageDealtToChampions"] #/ length
        #self.features["longestTimeSpentLiving"] = (stats["longestTimeSpentLiving"] // 60) #/ length
        self.features["totalMinionsKilled"] = stats["totalMinionsKilled"] #/ length
        #self.features["champLevel"] = stats["champLevel"]
        self.features["visionScore"] = stats["visionScore"]
        self.features["visionWardsBoughtInGame"] = stats["visionWardsBoughtInGame"] #/ length
        self.features["wardsPlaced"] = stats["wardsPlaced"] #/ length
        self.features["wardsKilled"] = stats["wardsKilled"] #/ length
        self.features["totalDamageTaken"] = stats["totalDamageTaken"] #/ length

        self.features["creepsPerMinDeltaEarlyGame"] = -1
        self.features["creepsPerMinDeltaMidGame"] = -1
        self.features["creepsPerMinDeltaLateGame"] = -1
        self.features["creepsPerMinDeltaEndGame"] = -1

        if "creepsPerMinDeltas" in timeline:
            if "0-10" in timeline["creepsPerMinDeltas"]:
                self.features["creepsPerMinDeltaEarlyGame"] = timeline["creepsPerMinDeltas"]["0-10"]
            if "10-20" in timeline["creepsPerMinDeltas"]:
                self.features["creepsPerMinDeltaMidGame"] = timeline["creepsPerMinDeltas"]["10-20"]
            if "20-30" in timeline["creepsPerMinDeltas"]:
                self.features["creepsPerMinDeltaLateGame"] = timeline["creepsPerMinDeltas"]["20-30"]
            if "30-end" in timeline["creepsPerMinDeltas"]:
                self.features["creepsPerMinDeltaEndGame"] = timeline["creepsPerMinDeltas"]["30-end"]

        #EXP differences
        self.features["xpPerMinDeltaEarlyGame"] = -1
        self.features["xpPerMinDeltaMidGame"] = -1
        self.features["xpPerMinDeltaLateGame"] = -1
        self.features["xpPerMinDeltaEndGame"] = -1

        if "xpPerMinDeltas" in timeline:
            if "0-10" in timeline["xpPerMinDeltas"]:
                self.features["xpPerMinDeltaEarlyGame"] = timeline["xpPerMinDeltas"]["0-10"]
            if "10-20" in timeline["xpPerMinDeltas"]:
                self.features["xpPerMinDeltaMidGame"] = timeline["xpPerMinDeltas"]["10-20"]
            if "20-30" in timeline["xpPerMinDeltas"]:
                self.features["xpPerMinDeltaLateGame"] = timeline["xpPerMinDeltas"]["20-30"]
            if "30-end" in timeline["xpPerMinDeltas"]:
                self.features["xpPerMinDeltaEndGame"] = timeline["xpPerMinDeltas"]["30-end"]

        #GOLD DIFFERENCES
        self.features["goldPerMinDeltasEarlyGame"] = -1
        self.features["goldPerMinDeltasMidGame"] = -1
        self.features["goldPerMinDeltasLateGame"] = -1
        self.features["goldPerMinDeltasEndGame"] = -1

        if "goldPerMinDeltas" in timeline:
            if "0-10" in timeline["goldPerMinDeltas"]:
                self.features["goldPerMinDeltasEarlyGame"] = timeline["goldPerMinDeltas"]["0-10"]
            if "10-20" in timeline["goldPerMinDeltas"]:
                self.features["goldPerMinDeltasMidGame"] = timeline["goldPerMinDeltas"]["10-20"]
            if "20-30" in timeline["goldPerMinDeltas"]:
                self.features["goldPerMinDeltasLateGame"] = timeline["goldPerMinDeltas"]["20-30"]
            if "30-end" in timeline["goldPerMinDeltas"]:
                self.features["goldPerMinDeltasEndGame"] = timeline["goldPerMinDeltas"]["30-end"]

                
        #complementary stats
        '''
        self.features["largestKillingSpree"] = stats["largestKillingSpree"]
        self.features["largestMultiKill"] = stats["largestMultiKill"]
        self.features["killingSprees"] = stats["killingSprees"]
        self.features["doubleKills"] = stats["doubleKills"]
        self.features["tripleKills"] = stats["tripleKills"]
        self.features["quadraKills"] = stats["quadraKills"]
        self.features["pentaKills"] = stats["pentaKills"]
        self.features["totalHeal"] = stats["totalHeal"] #/ length
        
        self.features["totalUnitsHealed"] = stats["totalUnitsHealed"] #/ length
        '''
        '''
        self.features["damageSelfMitigated"] = stats["damageSelfMitigated"] #/ length
        self.features["damageDealtToObjectives"] = stats["damageDealtToObjectives"] #/ length
        self.features["damageDealtToTurrets"] = stats["damageDealtToTurrets"] #/ length
        self.features["timeCCingOthers"] = stats["timeCCingOthers"] #/ length
        self.features["goldSpent"] = stats["goldSpent"] #/ length
        self.features["turretKills"] = stats["turretKills"]
        self.features["inhibitorKills"] = stats["inhibitorKills"]
        self.features["totalTimeCrowdControlDealt"] = stats["totalTimeCrowdControlDealt"] #/ length
        '''
        
        #boolean
        '''
        TODO ENCODE BOOLEAN FEATS
        self.features["firstBloodKill"] = stats.get("firstBloodKill",-1)
        self.features["firstBloodAssist"] = stats.get("firstBloodAssist",-1)
        self.features["firstTowerKill"] = stats.get("firstTowerKill",-1)
        self.features["firstTowerAssist"] = stats.get("firstTowerAssist",-1)
        self.features["firstInhibitorKill"] = stats.get("firstInhibitorKill",-1)
        self.features["firstInhibitorAssist"] = stats.get("firstInhibitorAssist",-1)
        '''
        #timeline features
        #minion differences
        
        #CS DIFFERENCES
        '''
        self.features["csDiffPerMinDeltasEarlyGame"] = -1
        self.features["csDiffPerMinDeltasMidGame"] = -1
        self.features["csDiffPerMinDeltasLateGame"] = -1
        self.features["csDiffPerMinDeltasEndGame"] = -1

        if "csDiffPerMinDeltas" in timeline:
            if "0-10" in timeline["csDiffPerMinDeltas"]:
                self.features["csDiffPerMinDeltasEarlyGame"] = timeline["csDiffPerMinDeltas"]["0-10"]
            if "10-20" in timeline["csDiffPerMinDeltas"]:
                self.features["csDiffPerMinDeltasMidGame"] = timeline["csDiffPerMinDeltas"]["10-20"]
            if "20-30" in timeline["csDiffPerMinDeltas"]:
                self.features["csDiffPerMinDeltasLateGame"] = timeline["csDiffPerMinDeltas"]["20-30"]
            if "30-end" in timeline["csDiffPerMinDeltas"]:
                self.features["csDiffPerMinDeltasEndGame"] = timeline["csDiffPerMinDeltas"]["30-end"]
        
        #EXP DIFFERENCES PER MIN
        
        self.features["xpDiffPerMinDeltasEarlyGame"] = -1
        self.features["xpDiffPerMinDeltasMidGame"] = -1
        self.features["xpDiffPerMinDeltasLateGame"] = -1
        self.features["xpDiffPerMinDeltasEndGame"] = -1

        if "xpDiffPerMinDeltas" in timeline:
            if "0-10" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasEarlyGame"] = timeline["xpDiffPerMinDeltas"]["0-10"]
            if "10-20" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasMidGame"] = timeline["xpDiffPerMinDeltas"]["10-20"]
            if "20-30" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasLateGame"] = timeline["xpDiffPerMinDeltas"]["20-30"]
            if "30-end" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasEndGame"] = timeline["xpDiffPerMinDeltas"]["30-end"]
        
        '''

        #DMG TAKEN PER MIN
        self.features["damageTakenPerMinDeltasEarlyGame"] = -1
        self.features["damageTakenPerMinDeltasMidGame"] = -1
        self.features["damageTakenPerMinDeltasLateGame"] = -1
        self.features["damageTakenPerMinDeltasEndGame"] = -1

        if "damageTakenPerMinDeltas" in timeline:
            if "0-10" in timeline["damageTakenPerMinDeltas"]:
                self.features["damageTakenPerMinDeltasEarlyGame"] = timeline["damageTakenPerMinDeltas"]["0-10"]
            if "10-20" in timeline["damageTakenPerMinDeltas"]:
                self.features["damageTakenPerMinDeltasMidGame"] = timeline["damageTakenPerMinDeltas"]["10-20"]
            if "20-30" in timeline["damageTakenPerMinDeltas"]:
                self.features["damageTakenPerMinDeltasLateGame"] = timeline["damageTakenPerMinDeltas"]["20-30"]
            if "30-end" in timeline["damageTakenPerMinDeltas"]:
                self.features["damageTakenPerMinDeltasEndGame"] = timeline["damageTakenPerMinDeltas"]["30-end"]

        #DMG TAKEN DIFFERENCE PER MIN
        '''
        self.features["damageTakenDiffPerMinDeltasEarlyGame"] = -1
        self.features["damageTakenDiffPerMinDeltasMidGame"] = -1
        self.features["damageTakenDiffPerMinDeltasLateGame"] = -1
        self.features["damageTakenDiffPerMinDeltasEndGame"] = -1

        if "damageTakenDiffPerMinDeltas" in timeline:
            if "0-10" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasEarlyGame"] = timeline["damageTakenDiffPerMinDeltas"]["0-10"]
            if "10-20" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasMidGame"] = timeline["damageTakenDiffPerMinDeltas"]["10-20"]
            if "20-30" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasLateGame"] = timeline["damageTakenDiffPerMinDeltas"]["20-30"]
            if "30-end" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasEndGame"] = timeline["damageTakenDiffPerMinDeltas"]["30-end"]
        '''

        self.featureNames = sorted(list(self.features.keys()))
        self.featureVector = []
        for name in self.featureNames:
            self.featureVector.append(self.features[name])

        self.label = self.rank

    def __repr__(self):
        winner = self.features["win"]
        strWinner = "Loser"
        if winner:
            strWinner = "Winner"

        return "  ".join([self.summonerName, self.rank, str(self.winrate), self.role,self.lane,self.champion,strWinner])

if __name__ == "__main__":
    fd = open("rankedGameInfo.json", "r")
    strJSON = fd.read()
    fd.close()
    iM = MatchAnalysis(strJSON)

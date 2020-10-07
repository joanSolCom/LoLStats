import json
from LoLStats import LolStats
from LoLStats import DataGatherer
from dataHelper import DataHelper

iDH = DataHelper()

class MatchAnalysis:

    def __init__(self, matchJSON):
        self.matchDict = json.loads(matchJSON)
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
            rank, winrate = self.dg.getAccountRank(self.server, iP.summonerId)
            iP.setRankInfo(rank, winrate)
            iP.setFeatures()
            self.participants.append(iP)
            self.participantsById[iP.participantId] = iP
            self.teamsById[iP.teamId].addParticipant(iP)

        print(self.participants)

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
        self.statsDict = participantStats["stats"]
        self.timelineDict = participantStats["timeline"]
        self.role = participantStats["timeline"]["role"]
        self.lane = participantStats["timeline"]["lane"]

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
        self.features["win"] = stats["win"]
        self.features["winrate"] = self.winrate
        self.features["champ"] = self.champion
        self.features["role"] = self.role + "_" + self.lane

        #basic performance measures
        self.features["kills"] = stats["kills"] / length
        self.features["deaths"] = stats["deaths"] / length
        self.features["assists"] = stats["assists"] / length
        self.features["goldEarned"] = stats["goldEarned"] / length
        self.features["totalDamageDealt"] = stats["totalDamageDealt"] / length
        self.features["totalDamageDealtToChampions"] = stats["totalDamageDealtToChampions"] / length
        self.features["longestTimeSpentLiving"] = (stats["longestTimeSpentLiving"] // 60) / length
        self.features["totalMinionsKilled"] = stats["totalMinionsKilled"] / length
        self.features["champLevel"] = stats["champLevel"]

        #complementary stats
        self.features["largestKillingSpree"] = stats["largestKillingSpree"]
        self.features["largestMultiKill"] = stats["largestMultiKill"]
        self.features["killingSprees"] = stats["killingSprees"]
        self.features["doubleKills"] = stats["doubleKills"]
        self.features["tripleKills"] = stats["tripleKills"]
        self.features["quadraKills"] = stats["quadraKills"]
        self.features["pentaKills"] = stats["pentaKills"]
        self.features["totalHeal"] = stats["totalHeal"] / length
        self.features["totalUnitsHealed"] = stats["totalUnitsHealed"] / length
        self.features["damageSelfMitigated"] = stats["damageSelfMitigated"] / length
        self.features["damageDealtToObjectives"] = stats["damageDealtToObjectives"] / length
        self.features["damageDealtToTurrets"] = stats["damageDealtToTurrets"] / length
        self.features["visionScore"] = stats["visionScore"]
        self.features["timeCCingOthers"] = stats["timeCCingOthers"] / length
        self.features["totalDamageTaken"] = stats["totalDamageTaken"] / length
        self.features["goldSpent"] = stats["goldSpent"] / length
        self.features["turretKills"] = stats["turretKills"]
        self.features["inhibitorKills"] = stats["inhibitorKills"]
        self.features["totalTimeCrowdControlDealt"] = stats["totalTimeCrowdControlDealt"] / length
        self.features["visionWardsBoughtInGame"] = stats["visionWardsBoughtInGame"] / length
        self.features["sightWardsBoughtInGame"] = stats["sightWardsBoughtInGame"] / length
        self.features["wardsPlaced"] = stats["wardsPlaced"] / length
        self.features["wardsKilled"] = stats["wardsKilled"] / length

        #boolean
        self.features["firstBloodKill"] = stats["firstBloodKill"]
        self.features["firstTowerKill"] = stats["firstTowerKill"]
        self.features["firstTowerAssist"] = stats["firstTowerAssist"]
        self.features["firstInhibitorKill"] = stats["firstInhibitorKill"]
        self.features["firstInhibitorAssist"] = stats["firstInhibitorAssist"]

        #timeline features
        #minion differences
        self.features["creepsPerMinDeltaEarlyGame"] = 0
        if "0-10" in timeline["creepsPerMinDeltas"]:
            self.features["creepsPerMinDeltaEarlyGame"] = timeline["creepsPerMinDeltas"]["0-10"]
    
        self.features["creepsPerMinDeltaMidGame"] = 0
        if "10-20" in timeline["creepsPerMinDeltas"]:
            self.features["creepsPerMinDeltaMidGame"] = timeline["creepsPerMinDeltas"]["10-20"]
    
        self.features["creepsPerMinDeltaLateGame"] = 0
        if "20-30" in timeline["creepsPerMinDeltas"]:
            self.features["creepsPerMinDeltaLateGame"] = timeline["creepsPerMinDeltas"]["20-30"]
    
        self.features["creepsPerMinDeltaEndGame"] = 0
        if "30-end" in timeline["creepsPerMinDeltas"]:
            self.features["creepsPerMinDeltaEndGame"] = timeline["creepsPerMinDeltas"]["30-end"]

        #EXP differences
        self.features["xpPerMinDeltaEarlyGame"] = 0
        if "0-10" in timeline["xpPerMinDeltas"]:
            self.features["xpPerMinDeltaEarlyGame"] = timeline["xpPerMinDeltas"]["0-10"]
    
        self.features["xpPerMinDeltaMidGame"] = 0
        if "10-20" in timeline["xpPerMinDeltas"]:
            self.features["xpPerMinDeltaMidGame"] = timeline["xpPerMinDeltas"]["10-20"]
    
        self.features["xpPerMinDeltaLateGame"] = 0
        if "20-30" in timeline["xpPerMinDeltas"]:
            self.features["xpPerMinDeltaLateGame"] = timeline["xpPerMinDeltas"]["20-30"]
    
        self.features["xpPerMinDeltaEndGame"] = 0
        if "30-end" in timeline["xpPerMinDeltas"]:
            self.features["xpPerMinDeltaEndGame"] = timeline["xpPerMinDeltas"]["30-end"]

        #GOLD DIFFERENCES
        self.features["goldPerMinDeltasEarlyGame"] = 0
        if "0-10" in timeline["goldPerMinDeltas"]:
            self.features["goldPerMinDeltasEarlyGame"] = timeline["goldPerMinDeltas"]["0-10"]
    
        self.features["goldPerMinDeltasMidGame"] = 0
        if "10-20" in timeline["goldPerMinDeltas"]:
            self.features["goldPerMinDeltasMidGame"] = timeline["goldPerMinDeltas"]["10-20"]
    
        self.features["goldPerMinDeltasLateGame"] = 0
        if "20-30" in timeline["goldPerMinDeltas"]:
            self.features["goldPerMinDeltasLateGame"] = timeline["goldPerMinDeltas"]["20-30"]
    
        self.features["goldPerMinDeltasEndGame"] = 0
        if "30-end" in timeline["goldPerMinDeltas"]:
            self.features["goldPerMinDeltasEndGame"] = timeline["goldPerMinDeltas"]["30-end"]

        #CS DIFFERENCES
        self.features["csDiffPerMinDeltasEarlyGame"] = 0
        self.features["csDiffPerMinDeltasMidGame"] = 0
        self.features["csDiffPerMinDeltasLateGame"] = 0
        self.features["csDiffPerMinDeltasEndGame"] = 0

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

        self.features["xpDiffPerMinDeltasEarlyGame"] = 0
        self.features["xpDiffPerMinDeltasMidGame"] = 0
        self.features["cxpDiffPerMinDeltasLateGame"] = 0
        self.features["xpDiffPerMinDeltasEndGame"] = 0

        if "xpDiffPerMinDeltas" in timeline:
            if "0-10" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasEarlyGame"] = timeline["xpDiffPerMinDeltas"]["0-10"]
            if "10-20" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasMidGame"] = timeline["xpDiffPerMinDeltas"]["10-20"]
            if "20-30" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasLateGame"] = timeline["xpDiffPerMinDeltas"]["20-30"]
            if "30-end" in timeline["xpDiffPerMinDeltas"]:
                self.features["xpDiffPerMinDeltasEndGame"] = timeline["xpDiffPerMinDeltas"]["30-end"]

        #DMG TAKEN PER MIN
        self.features["damageTakenPerMinDeltasEarlyGame"] = 0
        self.features["damageTakenPerMinDeltasMidGame"] = 0
        self.features["damageTakenPerMinDeltasLateGame"] = 0
        self.features["damageTakenPerMinDeltasEndGame"] = 0

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

        self.features["damageTakenDiffPerMinDeltasEarlyGame"] = 0
        self.features["damageTakenDiffPerMinDeltasMidGame"] = 0
        self.features["damageTakenDiffPerMinDeltasLateGame"] = 0
        self.features["damageTakenDiffPerMinDeltasEndGame"] = 0

        if "damageTakenDiffPerMinDeltas" in timeline:
            if "0-10" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasEarlyGame"] = timeline["damageTakenDiffPerMinDeltas"]["0-10"]
            if "10-20" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasMidGame"] = timeline["damageTakenDiffPerMinDeltas"]["10-20"]
            if "20-30" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasLateGame"] = timeline["damageTakenDiffPerMinDeltas"]["20-30"]
            if "30-end" in timeline["damageTakenDiffPerMinDeltas"]:
                self.features["damageTakenDiffPerMinDeltasEndGame"] = timeline["damageTakenDiffPerMinDeltas"]["30-end"]

        self.featureVector = self.features.values()
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

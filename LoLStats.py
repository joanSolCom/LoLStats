import json
from riotwatcher import LolWatcher
from dataHelper import DataHelper
from datetime import datetime
import operator
from pprint import pprint
from matchAnalyzer import MatchAnalysis

class LolStats:

    def __init__(self, matchHistory=None):
        self.iD = DataHelper()
        self.dG = DataGatherer()
        self.mh, self.accountId = self.dG.getMatchHistoryByName()
        
    #one request per game
    def statsPerRole(self):
        dictRole = {}
        for match in self.mh:
            matchObj = self.dG.getMatchByGameId(match["platformId"], match["gameId"])
            iM = MatchAnalysis(matchObj)
            for part in iM.participants:
                if part.accountId == self.accountId:
                    role = part.position
                    if role not in dictRole:
                        dictRole[role] = 0

                    dictRole[role]+=1
                    pprint(dictRole)
        return dictRole

    def dateTimeAnalysis(self):
        dictDates = {}
        dictTimes = {}

        for match in self.mh:
            matchId = match["gameId"]
            champId = match["champion"]
            champInfo = self.iD.getChampInfoById(champId)
            
            ts = match["timestamp"]
            date, dateTime, time = self.timestampToDate(ts)
            if date not in dictDates:
                dictDates[date]=0

            dictDates[date]+=1

            if time not in dictTimes:
                dictTimes[time] = 0
            dictTimes[time]+=1
        
        print("RANK OF MOST FREQUENT PLAY TIMES")
        pprint(sorted(dictTimes.items(), key=operator.itemgetter(1), reverse=True))
        
        print("RANK OF MOST PLAYED GAMES PER DAY")
        pprint(sorted(dictDates.items(), key=operator.itemgetter(1), reverse=True))            

    def champAnalysis(self):
        dictChamps = {}
        for match in self.mh:
            matchId = match["gameId"]
            champId = match["champion"]
            champInfo = self.iD.getChampInfoById(champId)
            if champInfo.name not in dictChamps:
                dictChamps[champInfo.name] = 0

            dictChamps[champInfo.name]+=1

        print("RANK OF MOST PLAYED CHAMPS")
        pprint(sorted(dictChamps.items(), key=operator.itemgetter(1), reverse=True))

    def timestampToDate(self, timestamp):
        converted = int(timestamp) / 1000
        dt_object = datetime.fromtimestamp(converted)
        return dt_object.strftime("%d/%m/%Y"), dt_object.strftime("%d/%m/%Y, %H:%M:%S"), dt_object.strftime("%H")

class DataGatherer:

    def __init__(self, apiKey = "RGAPI-80205c82-21eb-4475-a24a-7287968bd15c"):
        self.apiKey = apiKey
        self.iLol = LolWatcher(api_key=apiKey)
    
    def getAccountInfo(self, region, name):
        me = self.iLol.summoner.by_name(region, name)
        idAccount = me["id"]
        info = self.iLol.league.by_summoner(region, idAccount)
        info["region"] = region
        return info

    def getMatchAndTimeline(self, region, gameId):
        match = self.iLol.match.by_id(region=region,match_id=gameId)
        timeline = self.iLol.match.timeline_by_match(region,gameId)

        return match, timeline

    def getMatchTimeline(self, region, gameId):
        timeline = self.iLol.match.timeline_by_match(region,gameId)
        timeline["gameId"] = gameId
        return timeline

    def getUsersPerLeague(self, region, tier, division="I", page=1):
        userList = []
        entries = []
        if tier == "MASTERS":
            entries = self.iLol.league.masters_by_queue(region, "RANKED_SOLO_5x5")
            
            for e in entries["entries"]:
                e["region"] = region
            userList = entries["entries"]

        elif tier == "GRANDMASTER":
            entries = self.iLol.league.grandmaster_by_queue(region, "RANKED_SOLO_5x5")
            for e in entries["entries"]:
                e["region"] = region
            userList = entries["entries"]

        elif tier == "CHALLENGER":
            entries = self.iLol.league.challenger_by_queue(region, "RANKED_SOLO_5x5")
            for e in entries["entries"]:
                e["region"] = region
            userList = entries["entries"]
        else:
            entries = self.iLol.league.entries(region, "RANKED_SOLO_5x5", tier,division, page)
            for userInfo in entries:
                userInfo["region"] = region
                userList.append(userInfo)

        return userList

    def getAccountRank(self, region, summonerId):
        info = self.iLol.league.by_summoner(region, summonerId)
        rank = None
        winrate = None
        if len(info) > 0:
            info = info[0]
            rank = info["tier"] + "_" + info["rank"]
            winrate = info["wins"] / (info["wins"] + info["losses"])

        return rank, winrate

    def getMatchesInfo(self, mh):
        gameInfoList = []
        for m in mh:
            gameInfo = self.getMatchByGameId(m["platformId"], m["gameId"])
            gameInfoList.append(gameInfo)
        return gameInfoList

    def getMatchByGameId(self, region, gameId):
        gameInfo = self.iLol.match.by_id(region=region,match_id=gameId)
        return gameInfo

    def getMatchHistoryByName(self, name="TeslaTronca", region="EUW1", pageLimit=1000):
        me = self.iLol.summoner.by_name(region, name)
        encriptedId = me["accountId"]
        return self.getMatchHistoryByAccountId(encriptedId, region, pageLimit), encriptedId

    def getMatchHistoryByAccountId(self, accountId, region, pageLimit=1000):
        match_obj = self.iLol.match.matchlist_by_account(region, accountId,queue=420)
        matchHistory = []
        page = 0
        while len(match_obj["matches"]) > 0 and page < pageLimit:
            for matchInfo in match_obj["matches"]:
                matchHistory.append(matchInfo)

            endIndex = match_obj["endIndex"]
            match_obj = self.iLol.match.matchlist_by_account(region, accountId, begin_index=endIndex,queue=420)
            page+=1

        return matchHistory

    
if __name__ == "__main__":
    iS = LolStats()
    iS.dateTimeAnalysis()
    iS.champAnalysis()
    iS.statsPerRole()
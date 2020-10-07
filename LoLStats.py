import json
from riotwatcher import LolWatcher
from dataHelper import DataHelper
from datetime import datetime
import operator
from pprint import pprint

class LolStats:

    def __init__(self, matchHistoryJSON=None):
        if not matchHistoryJSON:
            with open("my_match_history.json") as json_file:
                self.raw = json.load(json_file)
        else:
            self.raw = json.loads(matchHistoryJSON)

        self.iD = DataHelper()

    def dateTimeAnalysis(self):
        dictDates = {}
        dictTimes = {}

        for match in self.raw:
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
        for match in self.raw:
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

    def __init__(self, apiKey = "RGAPI-99f28659-6241-4c83-a7f3-6ac27785dee4"):
        self.apiKey = apiKey
        self.iLol = LolWatcher(api_key=apiKey)

    def getAccountRank(self, region, summonerId):
        info = self.iLol.league.by_summoner(region, summonerId)
        rank = None
        winrate = None
        if len(info) > 0:
            info = info[0]
            rank = info["tier"] + "_" + info["rank"]
            winrate = info["wins"] / (info["wins"] + info["losses"])

        return rank, winrate

    def getMatchHistoryByName(self, name="TeslaTronca", region="EUW1"):
        me = self.iLol.summoner.by_name(region, name)
        encriptedId = me["accountId"]
        return self.getMatchHistoryByAccountId(encriptedId, region)

    def getMatchHistoryByAccountId(self, accountId, region):
        match_obj = self.iLol.match.matchlist_by_account(region, accountId)
        matchHistory = []
        while len(match_obj["matches"]) > 0:
            endIndex = match_obj["endIndex"]
            match_obj = self.iLol.match.matchlist_by_account(region, accountId, begin_index=endIndex)
            for matchInfo in match_obj["matches"]:
                matchHistory.append(matchInfo)
        
        return matchHistory

    
if __name__ == "__main__":
    iS = LolStats()
    #iS.dateTimeAnalysis()
    iS.champAnalysis()
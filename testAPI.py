from riotwatcher import LolWatcher
import json
from pprint import pprint
from LoLStats import DataGatherer

def getMatchHistoryByName(iLol, name):
    me = iLol.summoner.by_name(region, name)
    idAccount = me["id"]
    encriptedId = me["accountId"]
    match_obj = iLol.match.matchlist_by_account(region, encriptedId)
    matchHistory = []
    while len(match_obj["matches"]) > 0:
        for matchInfo in match_obj["matches"]:
            matchHistory.append(matchInfo)

        endIndex = match_obj["endIndex"]
        match_obj = iLol.match.matchlist_by_account(region, encriptedId, begin_index=endIndex)
        
    return encriptedId, matchHistory

apiKey = "RGAPI-dd8f97ea-3caa-4460-a09b-889e764c19ed"
region = "EUW1"
iLol = LolWatcher(api_key=apiKey)
name="TeslaTronca"

me = iLol.summoner.by_name(region, name)
idAccount = me["id"]
encriptedId = me["accountId"]

print(iLol.champion_mastery.scores_by_summoner(region,idAccount))


'''
gameId = 2081357982

import roleml
from mongoManager import MongoManager
iM = MongoManager()
match, timeline = iM.getMatchAndTimeline(gameId)
print(roleml.predict(match, timeline))
'''
#print(getMatchHistoryByName(iLol,"TeslaTronca"))
#timeline = iLol.match.timeline_by_match("EUW1","4353208107")
#pprint(timeline)
exit()
#info = iLol.league.by_summoner(region, "JGVQH4bsD6bWEx1NXS2xFpCo5yobPzqW44PF1aGpogW2AjV1")
#with open('playerInfoMine.json', 'w') as outfile:
#    info[0]["region"] = region
#    json.dump(info, outfile)
#print(stats)
#exit()
'''
Basic Stats
stats = iLol.league.by_summoner(region, idAccount)
print(stats)
[{'leagueId': 'a1caa462-e044-4f23-8140-76c40bb5a25a', 'queueType': 'RANKED_SOLO_5x5', 'tier': 'BRONZE', 'rank': 'I', 'summonerId': 'JGVQH4bsD6bWEx1NXS2xFpCo5yobPzqW44PF1aGpogW2AjV1', 'summonerName': 'TeslaTronca', 'leaguePoints': 55, 'wins': 86, 'losses': 102, 'veteran': False, 'inactive': False, 'freshBlood': False, 'hotStreak': False}]
'''



#encriptedId , mh = getMatchHistoryByName(iLol, name)

#with open('my_match_history.json', 'w') as outfile:
#    json.dump(mh, outfile)

#print(iLol.league.masters_by_queue(region, "RANKED_SOLO_5x5"))
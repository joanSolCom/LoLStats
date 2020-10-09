from riotwatcher import LolWatcher
import json
from pprint import pprint
from LoLStats import DataGatherer
apiKey = "RGAPI-7c65bbe4-7df3-4891-bc72-a6bb5671ee55"
region = "EUW1"
name = "Hanjiro"
iLol = LolWatcher(api_key=apiKey)
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

print(getMatchHistoryByName(iLol,"kelzod"))

#encriptedId , mh = getMatchHistoryByName(iLol, name)

#with open('my_match_history.json', 'w') as outfile:
#    json.dump(mh, outfile)

#print(iLol.league.masters_by_queue(region, "RANKED_SOLO_5x5"))
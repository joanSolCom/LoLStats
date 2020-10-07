from riotwatcher import LolWatcher
import json
from pprint import pprint

apiKey = "RGAPI-99f28659-6241-4c83-a7f3-6ac27785dee4"
region = "EUW1"
name = "TeslaTronca"
iLol = LolWatcher(api_key=apiKey)


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

encriptedId , mh = getMatchHistoryByName(iLol, name)
print(encriptedId)
#with open('my_match_history.json', 'w') as outfile:
#    json.dump(mh, outfile)

for match in mh:
    idx = match["gameId"]
    gameInfo = iLol.match.by_id(region=region,match_id=idx)
    #pprint(gameInfo)
    break
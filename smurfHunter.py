from LoLStats import DataGatherer
from playerScore import Score
from random import shuffle

regions = ["EUW1", "NA1", "EUN1","BR1","JP1","KR","LA1","LA2","OC1", "RU","TR1"]
tiers = ["SILVER", "BRONZE","GOLD","IRON"]
divisions = ["I","II","III","IV"]

def highWRSearch():
    N = 10
    i = 1
    page = 1
    iD = DataGatherer()
    for tier in tiers:
        for division in divisions:
            for region in regions:
                while i < N:
                    players = iD.getUsersPerLeague(region,tier,division,page)
                    for player in players:
                        winrate = player["wins"]/(player["wins"]+player["losses"])
                        totalGames = player["wins"]+player["losses"]
                        if winrate > 0.65 and totalGames > 25:
                            print(player["summonerName"],"WR",winrate,player["wins"],player["losses"],"Total Games",totalGames, tier, division, region)

                    i+=1
                    page+=1
                i=1

def scoreGuidedSearch():
    import numpy as np

    M = 20

    iD = DataGatherer()
    shuffle(divisions)
    shuffle(regions)
    pageIdx = {}
    for region in regions:
        pageIdx[region] = {}
        for tier in tiers:
            pageIdx[region][tier] = {}
            for division in divisions:
                pageIdx[region][tier][division] = 1

    change = False
    out = open("probableSmurfsAuto.txt","a")

    while True:
        for tier in tiers:
            for division in divisions:
                for region in regions:
                    print("Switching to",tier, division, region)
                    players = iD.getUsersPerLeague(region,tier,division,pageIdx[region][tier][division])
                    for player in players:
                        winrate = player["wins"]/(player["wins"]+player["losses"])
                        totalGames = player["wins"]+player["losses"]
                        if winrate > 0.65 and totalGames > 45:
                            print("WR probable smurf, writing", player["summonerName"])
                            line = player["summonerName"]+"\t"+region+"\t"+tier+"\t"+division+"\tWinrate\t"+str(winrate)+"\tgames\t"+str(totalGames)+"\n"
                            print(line)
                            out.write(line)
                            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")  
                        else:
                            try:
                                matches = iD.getMatchHistoryByName(player["summonerName"], region, 1)[0][:M]
                            except:
                                print("error")
                                break
                            topPerformances = 0
                            domPerformances = 0
                            for match in matches:
                                idGame = match["gameId"]
                                try:
                                    match = iD.getMatchByGameId(region, idGame)
                                except:
                                    print("error, lets switch")
                                    change = True
                                    break
                                iS = Score(match, False)
                                score, allScores = iS.getScoreOfPlayer(player["summonerId"])
                                sortedScores = sorted(allScores,reverse=True)
                                gameRank = sortedScores.index(score)
                                medianPerf = np.median(sortedScores)
                                incr = medianPerf 
                                if gameRank in [0,1,2]:
                                    #print(score, "TOP",gameRank+1, sortedScores)
                                    topPerformances+=1
                                    if gameRank == 1:
                                        if score > sortedScores[gameRank+1] + incr/2 or score > sortedScores[gameRank+2] + incr:
                                            domPerformances+=1
                                    else:
                                        if score > sortedScores[gameRank+1] + incr:
                                            domPerformances+=1

                            #print(player["summonerName"], tier, division,region,topPerformances/M, domPerformances/M)
                            if topPerformances/M >= 0.60 or domPerformances/M >= 0.40:
                                print(player["summonerName"], "IS PROBABLY A SMURF!!!!! OJO CUIDAOOOOOOOOOOOOO")
                                line = player["summonerName"]+"\t"+region+"\t"+tier+"\t"+division+"\tTopPerf\t"+str(topPerformances/M)+"\tDomPerf\t"+str(domPerformances/M)+"\n"
                                print(line)
                                out.write(line)
                                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")                                
                            
                            if change == True:
                                change = False
                                break

                    pageIdx[region][tier][division]+=1
        
scoreGuidedSearch()
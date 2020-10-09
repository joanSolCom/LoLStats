from LoLStats import DataGatherer
from mongoManager import MongoManager
import json
import random
iMongo = MongoManager()

regions = ["EUW1", "NA1", "EUN1","BR1","JP1","KR","LA1","LA2","OC1", "RU","TR1"]
tiers = ["IRON","BRONZE","SILVER","GOLD","PLATINUM","DIAMOND"]
divisions = ["I","II","III","IV"]

specialTiers = ["MASTERS","GRANDMASTER","CHALLENGER"]
N = 50
i = 1
database = "smurfington"
collection = "players"
iD = DataGatherer()

def crawlPlayers():
    for region in regions:
        for tier in specialTiers:
            players = iD.getUsersPerLeague(region,tier)
            ins = iMongo.insertPlayers(database,collection,players)


    for tier in tiers:
        for division in divisions:
            for region in regions:
                while i < N:
                    players = iD.getUsersPerLeague(region,tier,division,i)
                    ins = iMongo.insertPlayers(database,collection,players)
                    if ins:
                        print("inserted", len(ins.inserted_ids),region, tier, division, "    Page",i)
                    i+=1
                i=1

def crawlMatches(N):
    playerDict = {}
    idxPerRegion = {}
    finishedRegion = {}
    insertions = 0
    retries = 0
    for rg in regions:
        playerList = iMongo.getPlayersPerRegion(rg)
        random.shuffle(playerList)
        playerDict[rg] = playerList
        idxPerRegion[rg] = 0
        finishedRegion[rg] = False

    end = False

    while not end:
        print("NOT END YET")
        for region in regions:
            print("Switching to ",region)
            players = playerDict[region]
            count = 0
            if idxPerRegion[region] == len(playerDict[region]):
                finishedRegion[region] = True
                print("FINISHED REGION",region)
            
            finished = True
            for r in regions:
                if not finishedRegion[r]:
                    finished = False
                    break
            
            if finished:
                print("ALL REGIONS FINISHED")
                end = True
                
            else:
                while count < 3:
                    player = players[idxPerRegion[region]]
                    print(player["summonerName"], region)
                    mh = []
                    games = []
                    
                    try:                        
                        mh = iD.getMatchHistoryByName(player["summonerName"],player["region"])
                        games = iD.getMatchesInfo(mh[0:N])
                    except:
                        print("Exception occured, lets retry")
                        retries+=1
                        if retries == 4:
                            print("Too many retries, lets skip this dude for now")
                            idxPerRegion[region]+=1
                            retries = 0
                        continue

                    print("we have ",len(games),"games")
                    result = iMongo.insertMatches(games)
                    nInsertions = 0
                    if result:
                        nInsertions = len(result.inserted_ids)
                        insertions+= nInsertions

                    idxPerRegion[region]+=1
                    print(nInsertions, "Inserted")
                    print("Total inserted", insertions)
                    print("Count",count)
                    count+=1

        

crawlMatches(10)
from riotwatcher import LolWatcher
from mongoManager import MongoManager
from LoLStats import DataGatherer

apiKey = "RGAPI-c83d27cf-1d50-4568-85f4-fce644e12eaf"
iLol = LolWatcher(api_key=apiKey)
regions = ["EUW1", "NA1", "EUN1","BR1","JP1","KR","LA1","LA2","OC1","RU","TR1"]

iM = MongoManager()
matches = iM.getMatchesWithNoTimelines()

#timeline = iLol.match.timeline_by_match(region,gameId)
gameIdsPerRegion = {}
idxPerRegion = {}
finishedRegion = {}
iD = DataGatherer()

for match in matches:
    region = match["platformId"]
    gameId = match["gameId"]

    if region not in gameIdsPerRegion:
        gameIdsPerRegion[region] = []
        idxPerRegion[region] = 0
        finishedRegion[region] = False

    gameIdsPerRegion[region].append(gameId)

end = False
insertions = 0

while not end:
    print("NOT END YET")
    for region in regions:
        print("Switching to ",region)
        if region not in gameIdsPerRegion:
            print("NOT GAMES IN",region)
            continue

        games = gameIdsPerRegion[region]

        count = 0
        if idxPerRegion[region] == len(gameIdsPerRegion[region]):
            finishedRegion[region] = True
            print("FINISHED REGION",region)
            continue
        
        finished = True
        for r in regions:
            if not finishedRegion[r]:
                finished = False
                break
        
        if finished:
            print("ALL REGIONS FINISHED")
            end = True
        
        else:
            retries = 0
            while count < 3:
                if idxPerRegion[region] == len(games):
                    print("finished")
                    break
                
                gameId = games[idxPerRegion[region]]               
                try:                        
                    timeline = iD.getMatchTimeline(region, gameId)
                
                except:
                    print("Exception occured, lets retry")
                    retries+=1
                    if retries == 4:
                        print("Too many retries, lets skip this dude for now")
                        idxPerRegion[region]+=1
                        retries = 0
                    continue
                

                result = iM.insertTimeline(timeline)
                if result:
                    insertions+= 1

                idxPerRegion[region]+=1
                print("Total inserted", insertions)
                count+=1

from LoLStats import DataGatherer
from mongoManager import MongoManager
import json

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

for region in regions:
    for tier in specialTiers:
        players = iD.getUsersPerLeague(region,tier)
        ins = iMongo.insertPlayers(database,collection,players)

exit()
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

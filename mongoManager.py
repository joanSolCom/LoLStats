from pymongo import MongoClient

class MongoManager:

    def __init__(self, MONGOURI="mongodb://127.0.0.1:27017"):
        self.client = MongoClient(MONGOURI)

    def insertPlayers(self, database, collection, players):
        toInsert = []
        db = self.client[database]
        col = db[collection]
        for player in players:
            sumId = player["summonerId"]
            exists = self.findBySummonerId(database, collection, sumId)
            if not exists:
                toInsert.append(player)
            else:
                print(player["summonerName"],"is already in the database")

        result = None
        if toInsert:
            result = col.insert_many(toInsert)
    
        return result
    
    def findBySummonerId(self, database, collection, summonerId):
        db = self.client[database]
        col = db[collection]
        query = {"summonerId":summonerId}
        res = col.find_one(query)
        return res

    
if __name__ == "__main__":
    URI = "mongodb://127.0.0.1:27017"
    import json
    database = "smurfington"
    collection = "players"
    samplePlayer = json.loads(open("playerInfo.json","r").read())
    iM = MongoManager(URI)
    #print(iM.findBySummonerId(database,collection,"MN6IW9qCcAwpzfS04cDDsDSOscR8mY2ZhRGkhvqSqgiK3ZHM"))
    #print(iM.insertPlayers(database, collection, samplePlayer))
from pymongo import MongoClient

class MongoManager:

    def __init__(self, MONGOURI="mongodb://127.0.0.1:27017"):
        self.client = MongoClient(MONGOURI)
        self.db = self.client["smurfington"]
        self.players = self.db["players"]
        self.matches = self.db["matches"]

    def insertPlayers(self, database, collection, players):
        toInsert = []

        for player in players:
            sumId = player["summonerId"]
            exists = self.findBySummonerId(sumId)
            if not exists:
                toInsert.append(player)
            else:
                print(player["summonerName"],"is already in the database")

        result = None
        if toInsert:
            result = self.players.insert_many(toInsert)
    
        return result
    
    def findBySummonerId(self, summonerId):
        query = {"summonerId":summonerId}
        res = self.players.find_one(query)
        return res

    def getPlayers(self):
        players = []
        for player in self.players.find():
            players.append(player)
            print(len(players))

        return players
    
    def getMatches(self):
        matches = []
        for match in self.matches.find():
            matches.append(match)
            print(len(matches))

        return matches

    def getPlayersPerRegion(self, region):
        players = []
        query = {"region":region}
        for player in self.players.find(query):
            players.append(player)
            print(len(players))

        return players

    def findMatch(self, gameId):
        query = {"gameId":gameId}
        return self.matches.find_one(query)

    def insertMatches(self, matches):
        toInsert = []
        for match in matches:
            exists = self.findMatch(match["gameId"])
            if not exists:
                toInsert.append(match)
            else:
                print(match["gameId"],"already in database")
        print("We have ",len(toInsert),"to insert")
        result = None
        if toInsert:
            result = self.matches.insert_many(toInsert)

        print(result)
        return result
    
    def getMatchesPerRank(self):
        matches = self.getMatches()
        matchesPerRank = {}
        unregistered = set()
        instances = []
        for match in matches:
            for participant in match["participantIdentities"]:
                summonerId = participant["player"]["summonerId"]
                player = self.findBySummonerId(summonerId)
                if player:
                    instances.append(summonerId)
                    rank = "ABOVE_DIAMOND"
                    if "tier" in player:
                        rank = player["tier"]+"_"+player["rank"]

                    if rank not in matchesPerRank:
                        matchesPerRank[rank] = 0
                    
                    matchesPerRank[rank]+=1
                else:
                    unregistered.add(summonerId)
        #print(len(instances), len(unregistered))
        return matchesPerRank
    
if __name__ == "__main__":
    URI = "mongodb://127.0.0.1:27017"
    import json
    database = "smurfington"
    collection = "players"
    samplePlayer = json.loads(open("playerInfo.json","r").read())
    iM = MongoManager(URI)
    #iM.getPlayers()
    print(iM.getMatchesPerRank())
    #print(iM.findBySummonerId(database,collection,"MN6IW9qCcAwpzfS04cDDsDSOscR8mY2ZhRGkhvqSqgiK3ZHM"))
    #print(iM.insertPlayers(database, collection, samplePlayer))
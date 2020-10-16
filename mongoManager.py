from pymongo import MongoClient
from pprint import pprint
from random import shuffle

class MongoManager:

    def __init__(self, MONGOURI="mongodb://127.0.0.1:27017"):
        self.client = MongoClient(MONGOURI)
        self.db = self.client["smurfington"]
        self.players = self.db["players"]
        self.matches = self.db["matches"]
        self.timelines = self.db["timelines"]
        self.fullmatches = self.db["fullmatches"]

    def buildFullMatches(self):
        matches, timelines = self.getAllMatchesAndTimelines(3500)

        for match, timeline in zip(matches, timelines):
            query = {"gameId":match["gameId"]} 
            fullmatch = self.fullmatches.find_one(query)
            if not fullmatch:
                obj = {}
                obj["gameId"] = match["gameId"]
                obj["participants"] = []
                for part in match["participantIdentities"]:
                    idx = part["player"]["currentAccountId"]
                    obj["participants"].append(idx)

                obj["match"] = match
                obj["timeline"] = timeline
                self.fullmatches.insert_one(obj)
            else:
                print("had this one")

    def getMatchAndTimeline(self, gameId):
        query = {"gameId":gameId}
        match = self.matches.find_one(query)
        timeline = self.timelines.find_one(query)
        return match, timeline

    def getTimelines(self, maxNumber = None):
        timelines = []
        if maxNumber:
            for t in self.timelines.aggregate([{"$sample": {"size": maxNumber}}]):
                timelines.append(t)
        
        else:
            for t in self.timelines.find():
                timelines.append(t)

        return timelines
    
    def getAllMatchesAndTimelines(self, maxNumber=30000):
        fullmatches = self.getFullMatches(maxNumber)
        return fullmatches

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

    def getMatchesWithNoTimelines(self):
        matches = self.getMatches()
        print("Total matches",len(matches))
        toCrawl = []

        for match in matches:
            gameId = match["gameId"]
            query = {"gameId":gameId}
            alreadyHave = self.timelines.find_one(query)
            if not alreadyHave:
                toCrawl.append(match)

        print("With no timeline",len(toCrawl))
        return toCrawl
    
    def insertTimeline(self, timeline):
        result = self.timelines.insert_one(timeline)
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

    def getSpecificFullmatches(self, keyfullmatches):
        fms = []
        for gameId in keyfullmatches:
            fm = self.getFullMatchById(int(gameId))
            fms.append(fm)
        return fms

    def getMatches(self):
        matches = []
        for match in self.matches.find():
            matches.append(match)

        return matches

    def getFullMatches(self, maxNumber=30000):
        fmatches = []
        for fmatch in self.fullmatches.find({"match.gameDuration":{"$gt":1200}}).limit(maxNumber):
            fmatches.append(fmatch)

        return fmatches

    def getFullMatchById(self, gameId):
        query = {"gameId":gameId}
        fmatch = self.fullmatches.find_one(query)
        return fmatch

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
        matchesPerRankSimple = {}
        unregistered = set()
        instances = []
        for match in matches:
            for participant in match["participantIdentities"]:
                summonerId = participant["player"]["summonerId"]
                player = self.findBySummonerId(summonerId)
                if player:
                    instances.append(summonerId)
                    rank = "ABOVE_DIAMOND"
                    simpleRank = "ABOVE_DIAMOND"

                    if "tier" in player:
                        rank = player["tier"]+"_"+player["rank"]
                        simpleRank = player["tier"]

                    if rank not in matchesPerRank:
                        matchesPerRank[rank] = 0

                    if simpleRank not in matchesPerRankSimple:
                        matchesPerRankSimple[simpleRank] = 0

                    matchesPerRank[rank]+=1
                    matchesPerRankSimple[simpleRank]+=1
                else:
                    unregistered.add(summonerId)
        print("Number of instances", len(instances), "Number of not located users", len(unregistered))
        return matchesPerRank, matchesPerRankSimple
    
if __name__ == "__main__":
    URI = "mongodb://127.0.0.1:27017"
    import json
    database = "smurfington"
    collection = "players"
    samplePlayer = json.loads(open("playerInfo.json","r").read())
    iM = MongoManager(URI)
    iM.buildFullMatches()
    #iM.getPlayers()
    #pprint(iM.getMatchesPerRank())
    #print(iM.findBySummonerId(database,collection,"MN6IW9qCcAwpzfS04cDDsDSOscR8mY2ZhRGkhvqSqgiK3ZHM"))
    #print(iM.insertPlayers(database, collection, samplePlayer))
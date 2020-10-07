import json
import os

class DataHelper:

    def __init__(self, pathDT="./dragonTail/", patch="10.20.1", lang = "en_US"):
        self.basePath = pathDT
        self.patch = patch
        self.dataPath = pathDT + patch + "/data/" + lang + "/"
        self.load()

    def load(self):
        self.loadChampInfo()
        self.loadItemInfo()
        self.loadConstants()

    def loadConstants(self):
        self.queueInfo = {}
        with open("./constants/queues.json") as json_file:
            raw = json.load(json_file)
            for q in raw:
                self.queueInfo[q["queueId"]] = q["description"]

    def loadItemInfo(self):
        self.itemsById = {}
        with open(self.dataPath+"item.json") as json_file:
            raw = json.load(json_file)
            dictItems = raw["data"] 
            for name, dictInfo in dictItems.items():
                iI = Item(name, dictInfo, self.basePath, self.patch)
                self.itemsById[name] = iI

    def loadChampInfo(self):
        self.champsById = {}

        with open(self.dataPath+"championFull.json") as json_file:
            raw = json.load(json_file)
            dictChamps = raw["data"]
            for name, dictInfo in dictChamps.items():
                iC = Champion(dictInfo, self.basePath, self.patch)
                self.champsById[dictInfo["key"]] = iC
            
    def getChampInfoById(self, idx):
        return self.champsById.get(str(idx))

class Item:
    def __init__(self, idx, dictInfo, pathDT, patch):
        self.basePath = pathDT
        self.patch = patch
        self.name = dictInfo["name"]
        self.idx = idx
        self.description = dictInfo["description"]
        self.plaintext = dictInfo["plaintext"]
        self.transformsIntoList = dictInfo["into"]
        self.goldInfoDict = dictInfo["gold"]
        self.tagList = dictInfo["tags"]
        self.mapDict = dictInfo["maps"]
        self.imagePath = pathDT + patch + "/img/item/"+idx+".png"


class Champion:

    def __init__(self, dictInfo, pathDT, patch):
        self.basePath = pathDT
        self.patch = patch
        self.name = dictInfo["name"]
        self.id = dictInfo["key"]
        self.title = dictInfo["title"]
        self.lore = dictInfo["lore"]
        self.allytips = dictInfo["allytips"]
        self.enemytips = dictInfo["enemytips"]
        self.tags = dictInfo["tags"]
        self.statsDict = dictInfo["stats"]
        self.spellsDict = dictInfo["spells"]
        self.passiveDict = dictInfo["passive"]
        self.recommendedDict = dictInfo["recommended"]
        self.loadImgInfo()

    def loadImgInfo(self):

        self.iconPath = self.basePath + self.patch + "/img/champion/"+self.name+".png"

        path = self.basePath + "img/champion/"
        tilePath = path + "tiles/"
        self.tileImgPaths = []
        for fname in os.listdir(tilePath):
            if self.name in fname:
                self.tileImgPaths.append(tilePath+fname)
        
        splashPath = path + "splash/"
        self.splashImgPaths = []
        for fname in os.listdir(splashPath):
            if self.name in fname:
                self.splashImgPaths.append(splashPath+fname)

        loadPath = path + "loading/"
        self.loadImgPaths = []
        for fname in os.listdir(loadPath):
            if self.name in fname:
                self.loadImgPaths.append(loadPath+fname)

    
    def __repr__(self):
        return self.name

if __name__ == "__main__":
    iD = DataHelper()

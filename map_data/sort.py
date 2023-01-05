import json
from os import listdir
from os.path import isfile, join
from operator import itemgetter

def getFile(filetype):
    
    try:
        detect = [f for f in listdir("..\\map_data") if isfile(join("..\\map_data", f))]
    except:
        detect = [f for f in listdir("map_data") if isfile(join("map_data", f))]

    count = 0
    for name in range(len(detect)):
        name = detect[count].split(".")
        if name[len(name)-1].lower() == filetype:
            detect[count] = name[0]
            count += 1
        else:
            detect.pop(count)
    return detect

def getData(fileName):
    data = {}
    try:
        with open(fileName, "r") as file:
            data = json.load(file)
    except:
        with open("..\\map_data\\"+fileName, "r") as file:
            data = json.load(file)
    return data

def sorting(inputFile):
    # print(inputFile)
    for blockName in inputFile["blocks"]:
        blockData = inputFile["blocks"][blockName]
        if blockName not in ["chest", "teleporter"] and blockData:
            print(blockData["X"], blockData["Y"])
            try:
                blockData["X"], blockData["Y"] = list(zip(*sorted(zip( blockData["X"], blockData["Y"] ), key=itemgetter(0,1))))
            except:
                print("error")
            inputFile["blocks"][blockName] = blockData
    for livingName in inputFile["living"]:
        livingData = inputFile["living"][livingName]
        if livingName != "MC" and livingData["X"]:
            livingData["X"], livingData["Y"] = list(zip(*sorted(zip( livingData["X"], livingData["Y"] ), key=itemgetter(0,1))))
    pathData = inputFile["enemyPath"]
    if pathData["X"]:
        pathData["X"], pathData["Y"] = list(zip(*sorted(zip( pathData["X"], pathData["Y"] ), key=itemgetter(0,1))))

    return inputFile

def main():
    file = getFile("json")
    for each in file:
        each = each+".json"
        sc = getData(each)
        sc = sorting(sc)

        with open(each, "w") as writeIn:
            json.dump(sc, writeIn, indent = 4)

if __name__ == '__main__':
    main()
    input("Successfully sorted all of the files!")
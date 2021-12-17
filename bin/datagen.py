import argparse
import math
import os
import common_modules
import gzip
import json
from model_compiler import main as model_compiler
from mixer import main as mixer


def findsize(text, model):
    notInModelCost = math.log2(len(set(text)))
    order = len( list(model['model'].keys())[0] )#get length of a random key to know order, all the keys in a given model have same order anyway
    start_up = text[-order:]
    default_cost = -math.log2(1/len(model['alphabet'])) #in case we haven't seen a prefix
    filesize = common_modules.calculateFileSize(model,text,start_up,default_cost,notInModelCost)
    return filesize


def getTextCosts(costs, textDir, model, keyModelName):
    for textName in os.listdir(textDir):
        with open(f"{textDir}/{textName}", "r") as file:
            cost = findsize(file.read(), model)
            keyTextName = textName.split("-test")[0]
            if keyTextName not in costs:
                costs[keyTextName] = {}
            costs[keyTextName][keyModelName] = cost
    return costs


def getLineCosts(costs, textDir, model, keyModelName):
    for textName in os.listdir(textDir):
        with open(f"{textDir}/{textName}", "r") as file:
            i = -1
            for line in file.readlines():
                i+=1
                line = line.split("	", 1)[1]
                cost = findsize(line, model)
                keyTextName = textName.split("-test")[0]
                if keyTextName not in costs:
                    costs[keyTextName] = {}
                if i not in costs[keyTextName]:
                    costs[keyTextName][i] = {}
                costs[keyTextName][i][keyModelName] = cost
    return costs


def getTextPositives(costs):
    testCount = len(costs)
    correct = 0
    for textName, textCosts in costs.items():
        if textName == sorted(textCosts.keys(), key=lambda x: textCosts[x])[0]:
            correct += 1
    return testCount, correct


def getLinePositives(costs):
    testCount = 0
    correct = 0
    for textName, lines in costs.items():
        testCount += len(lines)
        for _, lineCosts in lines.items():
            if textName == sorted(lineCosts.keys(), key=lambda x: lineCosts[x])[0]:
                correct += 1
    return testCount, correct


def getMixedIntervals(modelIntervals, textDir, model, keyModelName):
    for textName in os.listdir(textDir):
        with open(f"{textDir}/{textName}", "r") as file:
            offsets = file.readline()
            line = file.readline()
            notInModelCost = math.log2(len(line))
            for windowSize in [1, 5, 10, 15, 20]:
                for threshold in [1, 3, 5]:
                    intervals, validLength = common_modules.calculateLanguageIntervals(model, line, notInModelCost, windowSize, threshold)
                    if len(intervals) > 0:
                        if textName not in modelIntervals:
                            offsets = [int(i) for i in offsets.split(" ")] + [len(line)]
                            offsetModels = textName.removesuffix(".txt").split(";")
                            expected =  {m: (offsets[i], offsets[i+1]) for i, m in enumerate(offsetModels)}
                            modelIntervals[textName] = {"calculated": {}, "expected": expected}
                        if windowSize not in modelIntervals[textName]["calculated"]:
                            modelIntervals[textName]["calculated"][windowSize] = {}
                        if threshold not in modelIntervals[textName]["calculated"][windowSize]:
                            modelIntervals[textName]["calculated"][windowSize][threshold] = {}
                        modelIntervals[textName]["calculated"][windowSize][threshold][keyModelName] = (intervals, validLength)
    return modelIntervals


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--folder",help="Folder with the texts for the model", required=True)
    parser.add_argument("--models-folder",help="Folder to store the models", required=True)
    parser.add_argument("--outputprefix", help="Output prefix", required=True)
    parser.add_argument("--fulltest-dir",help="Folder with full texts under analysis", required=True)
    parser.add_argument("--longtest-dir",help="Folder with long texts under analysis", required=True)
    parser.add_argument("--mediumtest-dir",help="Folder with medium texts under analysis", required=True)
    parser.add_argument("--shorttest-dir",help="Folder with short texts under analysis", required=True)
    parser.add_argument("--tinytest-dir",help="Folder with tiny texts under analysis", required=True)
    parser.add_argument("--mixedtest-dir",help="Folder with mixed texts under analysis", required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.mixedtest_dir):
        mixer(5, args.shorttest_dir, args.mixedtest_dir, 5, 1)

    accuracies = {}
    intervals = {}

    for modelSize in [i/10 for i in range(1, 11)]:

        modelDir = f'{args.models_folder}{int(modelSize*100):0>3d}/'
        if not os.path.isdir(modelDir):
            model_compiler(3, 0.1, args.folder, modelDir, modelSize)

        costs = {"full":{}, "long":{}, "medium":{}, "short":{}, "tiny":{}}

        modelIntervals = {}

        for f in os.listdir(modelDir):
            keyModelName = f.removesuffix(".tar.gz").removesuffix("-train")
            fullpath = f"{modelDir}{f}"
            with gzip.open(fullpath,"rt") as fileobj:
                model = json.load(fileobj)

            costs["full"] = getTextCosts(costs["full"], args.fulltest_dir, model, keyModelName)
            costs["long"] = getLineCosts(costs["long"], args.longtest_dir, model, keyModelName)
            costs["medium"] = getLineCosts(costs["medium"], args.mediumtest_dir, model, keyModelName)
            costs["short"] = getLineCosts(costs["short"], args.shorttest_dir, model, keyModelName)
            costs["tiny"] = getLineCosts(costs["tiny"], args.tinytest_dir, model, keyModelName)

            modelIntervals = getMixedIntervals(modelIntervals, args.mixedtest_dir, model, keyModelName)

        accuracies[modelSize] = {
            "full": getTextPositives(costs["full"]),
            "long": getLinePositives(costs["long"]),
            "medium": getLinePositives(costs["medium"]),
            "short": getLinePositives(costs["short"]),
            "tiny": getLinePositives(costs["tiny"])
        }

        intervals[modelSize] = modelIntervals

    with gzip.open(f"{args.outputprefix}.tar.gz", "wt") as f:
        json.dump({"accuracies": accuracies, "intervals": intervals}, f)

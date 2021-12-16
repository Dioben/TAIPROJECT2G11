import argparse
import math
import os
import common_modules
import gzip
import json
from model_compiler import main as model_compiler


def findsize(text, model):
    notInModelCost = math.log2(len(set(text)))
    order = len( list(model['model'].keys())[0] )#get length of a random key to know order, all the keys in a given model have same order anyway
    start_up = text[-order:]
    default_cost = -math.log2(1/len(model['alphabet'])) #in case we haven't seen a prefix
    filesize = common_modules.calculateFileSize(model,text,start_up,default_cost,notInModelCost)
    return filesize


def getTextCosts(costs, textDir, model):
    for textName in os.listdir(textDir):
        with open(f"{textDir}/{textName}", "r") as file:
            cost = findsize(file.read(), model)
            keyTextName = textName.removesuffix("-test.utf8")
            if keyTextName not in costs:
                costs[keyTextName] = {}
            costs[keyTextName][keyModelName] = cost
    return costs


def getLineCosts(costs, textDir, model):
    for textName in os.listdir(textDir):
        with open(f"{textDir}/{textName}", "r") as file:
            i = -1
            for line in file.readlines():
                i+=1
                line = line.split("	", 1)[1]
                cost = findsize(line, model)
                keyTextName = textName.removesuffix("-test.utf8")
                if keyTextName not in costs:
                    costs[keyTextName] = {}
                if i not in costs[keyTextName]:
                    costs[keyTextName][i] = {}
                costs[keyTextName][i][keyModelName] = cost
    return costs


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--folder", help="Models folder", required=True)
    parser.add_argument("--fulltest-dir",help="Folder with full texts under analysis", required=True)
    parser.add_argument("--longtest-dir",help="Folder with long texts under analysis", required=True)
    parser.add_argument("--mediumtest-dir",help="Folder with medium texts under analysis", required=True)
    parser.add_argument("--shorttest-dir",help="Folder with short texts under analysis", required=True)
    parser.add_argument("--tinytest-dir",help="Folder with tiny texts under analysis", required=True)
    args = parser.parse_args()

    accuracies = {}

    for modelSize in [i/10 for i in range(1, 11)]:

        modelDir = f'testModels{int(modelSize*10):0>2d}/'
        if not os.path.isdir(modelDir):
            model_compiler(3, 0.1, args.folder, modelDir, modelSize)

        costs = {"full":{}, "long":{}, "medium":{}, "short":{}, "tiny":{}}

        for f in os.listdir(modelDir):
            keyModelName = f.removesuffix(".tar.gz").removesuffix("-train")
            fullpath = f"{modelDir}{f}"
            fileobj = gzip.open(fullpath,"rt")
            model = json.load(fileobj)

            costs["full"] = getTextCosts(costs["full"], args.fulltest_dir, model)
            costs["long"] = getLineCosts(costs["long"], args.longtest_dir, model)
            costs["medium"] = getLineCosts(costs["medium"], args.mediumtest_dir, model)
            costs["short"] = getLineCosts(costs["short"], args.shorttest_dir, model)
            costs["tiny"] = getLineCosts(costs["tiny"], args.tinytest_dir, model)

        # TODO: calculate accuracies

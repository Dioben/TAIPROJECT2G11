import argparse
import math
import os
import common_modules
import gzip
import json


def findsize(text, model):
    notInModelCost = math.log2(len(set(text)))
    order = len( list(model['model'].keys())[0] )#get length of a random key to know order, all the keys in a given model have same order anyway
    start_up = text[-order:]
    default_cost = -math.log2(1/len(model['alphabet'])) #in case we haven't seen a prefix
    filesize = common_modules.calculateFileSize(model,text,start_up,default_cost,notInModelCost)
    return filesize

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", required=True)
    # parser.add_argument("--fulltest-dir",help="Folder with full texts under analysis", required=True)
    # parser.add_argument("--shorttest-dir",help="Folder with short texts under analysis", required=True)
    args = parser.parse_args()

    args.fulltest_dir = "../DS/test/"
    args.shorttest_dir = "../DS/testsets-short/"

    fullTestCosts = {}
    shortTestCosts = {}

    for f in os.listdir(args.classes):
        keyModelName = f.removesuffix(".tar.gz").removesuffix("-train")
        fullpath = f"{args.classes}/{f}"
        fileobj = gzip.open(fullpath,"rt")
        model = json.load(fileobj)

        for textName in os.listdir(args.fulltest_dir):
            with open(f"{args.fulltest_dir}/{textName}", "r") as file:
                cost = findsize(file.read(), model)
                keyTextName = textName.removesuffix("-test.utf8")
                if keyTextName not in fullTestCosts:
                    fullTestCosts[keyTextName] = {}
                fullTestCosts[keyTextName][keyModelName] = cost
    
        for textName in os.listdir(args.shorttest_dir):
            with open(f"{args.shorttest_dir}/{textName}", "r") as file:
                i = -1
                for line in file.readlines():
                    i+=1
                    line = line.split("	", 1)[1]
                    cost = findsize(line, model)
                    keyTextName = textName.removesuffix("-test.utf8")
                    if keyTextName not in shortTestCosts:
                        shortTestCosts[keyTextName] = {}
                    if i not in shortTestCosts[keyTextName]:
                        shortTestCosts[keyTextName][i] = {}
                    shortTestCosts[keyTextName][i][keyModelName] = cost

    # compare text and model name to know if correct
    for textName, models in fullTestCosts.items():
        print(f'{textName}: {models}')

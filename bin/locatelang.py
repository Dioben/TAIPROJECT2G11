import argparse
import gzip
import json
import common_modules
import math
import os


def loadModelPaths(path):
    models = {}
    for f in os.listdir(args.classes):
        keyname = f.removesuffix(".tar.gz")
        fullpath = f"{args.classes}/{f}"
        models[keyname]=fullpath
    return models


def LocateLangs(models,text,windowSize,threshold):
    langs = dict()
    textAlphabet = set(text)
    notInModelCost = math.log2(len(textAlphabet))
    startup = sorted(textAlphabet)[0] * 999 #if you use more than this stuff breaks, please do not compute a model with k = 1000
    for modelName, modelPath in models.items():
        file = gzip.open(modelPath, "rt")
        model = json.load(file)
        file.close()
        intervals, validLength = common_modules.calculateLanguageIntervals(model, text, startup, notInModelCost, windowSize, threshold)
        if len(intervals) > 0:
            langs[modelName] = intervals, validLength
    return langs


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", required=True)
    parser.add_argument("--input",help="Text under analysis", required=True)
    parser.add_argument("--window-size",help="Size of the window", type=int, default=10)
    parser.add_argument("--threshold",help="Maximum average cost (bytes) of a window to be considered a language", type=float, default=2)
    args = parser.parse_args()

    file = open(args.input,"r")
    text = file.read()
    file.close()

    models = loadModelPaths(args.classes)
    gaps = LocateLangs(models,text,args.window_size,args.threshold)

    print(*gaps.items(), sep="\n")

import argparse
import gzip
import json
import common_modules
import math
import os


def loadModelPaths(classes):
    models = {}
    for f in os.listdir(classes):
        keyname = f.removesuffix(".tar.gz")
        fullpath = f"{classes}/{f}"
        models[keyname]=fullpath
    return models


def LocateLangs(models,text,windowSize,threshold):
    langs = dict()
    textAlphabet = set(text)
    notInModelCost = math.log2(len(textAlphabet))
    for modelName, modelPath in models.items():
        file = gzip.open(modelPath, "rt")
        model = json.load(file)
        file.close()
        intervals, validLength = common_modules.calculateLanguageIntervals(model, text, notInModelCost, windowSize, threshold)
        if len(intervals) > 0:
            langs[modelName] = intervals, validLength
    return langs


def main(input, classes, window_size, threshold):
    file = open(input,"r")
    text = file.read()
    file.close()

    models = loadModelPaths(classes)
    return LocateLangs(models,text,window_size,threshold)


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", required=True)
    parser.add_argument("--input",help="Text under analysis", required=True)
    parser.add_argument("--window-size",help="Size of the window", type=int, default=20)
    parser.add_argument("--threshold",help="Maximum average cost (bytes) of a window to be considered a language", type=float, default=3)
    args = parser.parse_args()
    
    gaps = main(args.input, args.classes, args.window_size, args.threshold)

    print(*gaps.items(), sep="\n")

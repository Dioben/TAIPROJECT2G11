import argparse
import gzip
import json
import common_modules
import math


def LocateLangs(models,text,windowSize,threshold):
    langs = dict()
    textAlphabet = set(text)
    notInModelCost = math.log2(len(textAlphabet))
    for modelGroupName, modelPathList in models.items():
        for modelPath in modelPathList:
            file = gzip.open(modelPath, "rt")
            model = json.load(file)
            file.close()
            intervals, validLength = common_modules.calculateLanguageIntervals(model, text, notInModelCost, windowSize, threshold)
            if len(intervals) > 0:
                try:
                    if langs[modelGroupName][1] > validLength:
                        langs[modelGroupName] = intervals, validLength
                except:
                    langs[modelGroupName] = intervals, validLength
    return langs


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--groups",help="Class model groups JSON file", required=True)
    parser.add_argument("--input",help="Text under analysis", required=True)
    parser.add_argument("--window-size",help="Size of the window", type=int, default=20)
    parser.add_argument("--threshold",help="Maximum average cost (bytes) of a window to be considered a language", type=float, default=3)
    args = parser.parse_args()


    file = open(args.input,"r")
    text = file.read()
    file.close()

    file = open(args.groups,"r")
    models = json.load(file)
    file.close()

    gaps = LocateLangs(models,text,args.window_size,args.threshold)

    print(*gaps.items(), sep="\n")

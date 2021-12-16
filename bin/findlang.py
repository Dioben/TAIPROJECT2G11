import argparse
import gzip
import json
import common_modules
import math
import os


def main(text, classes):
    notInModelCost = math.log2(len(set(text)))

    costs = {}

    for f in os.listdir(classes):
        keyname = f.removesuffix(".tar.gz").removesuffix("-train")
        fullpath = f"{classes}/{f}"
        fileobj = gzip.open(fullpath,"rt")
        model = json.load(fileobj)
        fileobj.close()
        order = len( list(model['model'].keys())[0] )#get length of a random key to know order, all the keys in a given model have same order anyway
        start_up = text[-order:]
        default_cost = -math.log2(1/len(model['alphabet'])) #in case we haven't seen a prefix
        filesize = common_modules.calculateFileSize(model,text,start_up,default_cost,notInModelCost)
        costs[keyname]= filesize

    return costs


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", required=True)
    parser.add_argument("--input",help="Text under analysis", required=True)
    args = parser.parse_args()

    with open(args.input, "r") as file:
        costs = main(file.read(), args.classes)

    print("Ranked choices (top 100):")
    keys = sorted(costs.keys(),key=lambda x:costs[x])[:100]
    for x in keys:
        print(f"file size: {costs[x]}, model: {x}")
    

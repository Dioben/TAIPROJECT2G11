import argparse
import gzip
import json
import common_modules
import math
import os

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", required=True)
    parser.add_argument("--input",help="Text under analisis", required=True)
    args = parser.parse_args()


    file = open(args.input,"r")
    text= file.read()
    file.close()
    notInModelCost = math.log2(len(set(text)))

    bestcost = math.inf
    bestmodel = None

    for f in os.listdir(args.classes):
        keyname = f.removesuffix(".tar.gz")
        fullpath = f"{args.classes}/{f}"
        fileobj = gzip.open(fullpath,"rt")
        model = json.load(fileobj)
        fileobj.close()
        order = len( list(model['model'].keys())[0] )#get length of a random key to know order, all the keys in a given model have same order anyway
        start_up = sorted(model['alphabet'])[0]*order
        default_cost = -math.log2(1/len(model['alphabet'])) #in case we haven't seen a prefix
        filesize = common_modules.calculateFileSize(model,text,start_up,default_cost,notInModelCost)
        if filesize<bestcost:
            bestmodel = keyname
            bestcost = filesize
    
    print(f"Best filesize was {bestcost} for model {bestmodel}")
    

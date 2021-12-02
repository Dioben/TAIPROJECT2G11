import argparse
import gzip
import json
import common_modules
import math
import os

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", default="models")
    parser.add_argument("--input",help="Text under anaylisis", default="../example/example.txt")
    args = parser.parse_args()


    file = open(args.input,"r")
    text= file.read()
    file.close()

    bestcost = math.inf
    bestmodel = None
    for f in os.listdir(args.classes):
        keyname = f.removesuffix(".tar.gz")
        fullpath = f"{args.classes}/{f}"
        fileobj = gzip.open(fullpath,"rt")
        model = json.load(fileobj)
        start_up = sorted(model['alphabet'])[0]*args.order
        default_cost = -math.log2(1/len(model['alphabet'])) #in case we haven't seen a prefix
        filesize = common_modules.calculateFileSize(model['model'],text,start_up,default_cost)
        if filesize<bestcost:
            bestmodel = keyname
            bestcost = filesize
    
    print(f"Best filesize was {bestcost} for model {bestmodel}")
    

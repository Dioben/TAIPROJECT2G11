import argparse
import gzip
import json
import common_modules
import math
import os

def loadModelsFull(path):
    models = {}
    for f in os.listdir(args.classes):
        keyname = f.removesuffix(".tar.gz")
        fullpath = f"{args.classes}/{f}"
        fileobj = gzip.open(fullpath,"rt")
        model = json.load(fileobj)
        fileobj.close()
        models[keyname]=model
    return models

def loadModelPaths(path):
    models = {}
    for f in os.listdir(args.classes):
        keyname = f.removesuffix(".tar.gz")
        fullpath = f"{args.classes}/{f}"
        models[keyname]=fullpath
    return models

def LocateLangsMemory(models,text,min_length,max_default):
    pass

def LocateLangsIO(models,text,min_length,max_default):
    pass

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", default="models")
    parser.add_argument("--input",help="Text under analisis", default="../example/example.txt")
    parser.add_argument("--intensive",dest="memory",help="Enable high memory use",action="store_true")
    parser.add_argument("--low-memory",dest="memory",help="Enable low memory use, more IO",action="store_false")
    parser.set_defaults(memory=True)
    parser.add_argument("--min-length",help="Minimum length of a language chunk",type=int, default=50)
    parser.add_argument("--max-default",help="Consecutive Unknown sequences tolerated",type=int, default=7)
    args = parser.parse_args()

    file = open(args.input,"r")
    text= file.read()
    file.close()

    if args.memory:
        models = loadModelsFull(args.classes)
        gaps = LocateLangsMemory(models,text,args.min_length,args.max_default)
    else:
        models = loadModelPaths(args.classes)
        gaps = LocateLangsIO(models,text,args.min_length,args.max_default)
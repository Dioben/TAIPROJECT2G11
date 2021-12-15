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
    langs = []
    checkpoint = 0
    max = len(text)
    text_alphabet = set(text)
    notInModelCost = math.log2(len(text_alphabet))
    while checkpoint<max:
        results = {}
        effective_text = text[checkpoint:]
        for keyname,model in models.items():
            default_cost = -math.log2(1/len(model['alphabet']))
            cost,travelled = common_modules.calculateFileSizeStopEarly(model,effective_text,default_cost,notInModelCost,max_default)
            results[keyname] = (cost,travelled)

        ending = max-checkpoint<min_length #do we have enough characters left to enforce min_length
        
        filteredresults={x for x,y in results.items() if y[1]>=min_length or ending}
        sortedbest = sorted(results.keys(),key=lambda x:results[x][0]/results[x][1])

        best = None
        for result in sortedbest:
            if result in filteredresults:
                best = result
                break
        if not best:
            best = sortedbest[0]

        langs.append((best,checkpoint)) #we want to know where a lang starts so this goes first
        offset = results[best][1] 
        checkpoint+= offset 
        if checkpoint<max: #means we stopped via the default max rule
            checkpoint-=max_default
        if offset>=999: #full replace
            start_up = effective_text[offset-999:offset]
        else:  #partial update
            start_up = start_up[offset:]+effective_text[:offset]
            
    return langs

def LocateLangsIO(models,text,min_length,max_default):
    langs = []
    checkpoint = 0
    max = len(text)
    text_alphabet = set(text)
    notInModelCost = math.log2(len(text_alphabet))
    while checkpoint<max:
        results = {}
        effective_text = text[checkpoint:]
        for keyname,modelpath in models.items():
            
            #load model
            fileobj = gzip.open(modelpath,"rt")
            model = json.load(fileobj)
            fileobj.close()

            default_cost = -math.log2(1/len(model['alphabet']))
            cost,travelled = common_modules.calculateFileSizeStopEarly(model,effective_text,default_cost,notInModelCost,max_default)
            results[keyname] = (cost,travelled)

        ending = max-checkpoint<min_length #do we have enough characters left to enforce min_length
        
        filteredresults={x for x,y in results.items() if y[1]>=min_length or ending}
        sortedbest = sorted(results.keys(),key=lambda x:results[x][0]/results[x][1])[0]

        best = None
        for result in sortedbest:
            if result in filteredresults:
                best = result
                break
        if not best:
            best = sortedbest[0]

        langs.append((best,checkpoint)) #we want to know where a lang starts so this goes first
        offset = results[best][1] 
        checkpoint+= offset 
        if checkpoint<max: #means we stopped via the default max rule
            checkpoint-=max_default
        if offset>=999: #full replace
            start_up = effective_text[offset-999:offset]
        else:  #partial update
            start_up = start_up[offset:]+effective_text[:offset]
            
    return langs

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", required=True)
    parser.add_argument("--input",help="Text under analysis", required=True)
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

print(*gaps, sep="\n")

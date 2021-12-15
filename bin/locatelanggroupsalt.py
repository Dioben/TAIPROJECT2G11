import argparse
import gzip
import json
import common_modules
import math
import os

def loadModelsFull(jsonList):
    models = {}
    for key,values in jsonList.items():
        models[key] = []
        for fullpath in values:
            fileobj = gzip.open(fullpath,"rt")
            model = json.load(fileobj)
            fileobj.close()
            models[key].append(model)
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
        for keyname,modelList in models.items():
            for model in modelList:
                default_cost = -math.log2(1/len(model['alphabet']))
                cost,travelled = common_modules.calculateFileSizeStopEarly(model,effective_text,default_cost,notInModelCost,max_default)
                if not results[keyname]:
                    results[keyname] = (cost,travelled)
                else:
                    if results[keyname][0]/results[keyname][1]> cost/travelled:
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
        
        for keyname,modelPathList in models.items():
            for modelpath in modelPathList:

                #load model
                fileobj = gzip.open(modelpath,"rt")
                model = json.load(fileobj)
                fileobj.close()

                default_cost = -math.log2(1/len(model['alphabet']))
                cost,travelled = common_modules.calculateFileSizeStopEarly(model,effective_text,default_cost,notInModelCost,max_default)
                if not results[keyname]:
                    results[keyname] = (cost,travelled)
                else:
                    if results[keyname][0]/results[keyname][1]> cost/travelled:
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
    parser.add_argument("--groups",help="Class model groups JSON file", required=True)
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

    file = open(args.groups)
    models = json.load(file)
    file.close()

    if args.memory:
        models = loadModelsFull(models)
        gaps = LocateLangsMemory(models,text,args.min_length,args.max_default)
    else:
        gaps = LocateLangsIO(models,text,args.min_length,args.max_default)

print(*gaps, sep="\n")
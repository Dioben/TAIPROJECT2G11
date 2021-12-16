import argparse
import os
import random
import itertools


def exportRandomMix(filelist,samples,suffix,lines,folder):
    lines = {}
    outputfile = ""
    for filekey in filelist:
        outputfile+=filekey+";"
        file = open(samples[filekey],"r")
        filelines = file.readLines()
        file.close()
        lines[filekey] = [line.split(" ",1)[1].strip() for line in filelines] #remove model identifier and trim whitespace
    outputfile = outputfile[:-1]
    outputfile+=f"{suffix}.txt"
    outputfile = folder + "/"+outputfile
    f = open(outputfile,"w")
    for _ in range(lines):
        str = ""
        offsets = [0]
        for poss in lines.values():
            text=random.choice(poss)
            str+=text
            offsets.append(offsets[-1]+len(text))
        str+="\n"
        f.write(" ".join(offsets[:-1])+"\n")
        f.write(str+"\n")
    f.close()

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--count",help="How many models we're concatenating",type=int,default=3)
    parser.add_argument("--input", help="test texts folder", required=True)
    parser.add_argument("--outputfolder", help="Output folder", required=True)
    parser.add_argument("--outputs",help="Number of files put out",default=50,type=int)
    parser.add_argument("--lines", help="lines per file",type=int, default=50)

    args = parser.parse_args()

    samples = {}
    for f in os.listdir(args.input):
        fullpath = f"{args.classes}/{f}"
        keyname = f.split("-test")[0]
        samples[keyname] = fullpath

    combs = itertools.permutations(samples.keys(),args.count)
    random.shuffle(combs)
    combs = combs[:args.outputs]

    outputfiles = 0
    for filelist in combs:
        exportRandomMix(filelist,samples,str(outputfiles),args.lines,args.outputfolder)
        outputfiles+=1
        

import argparse
import os
import random
import itertools


def exportRandomMix(filelist,samples,lineCount,folder):
    os.makedirs(os.path.dirname(folder), exist_ok=True)
    lines = {}
    outputfile = ""
    for filekey in filelist:
        outputfile+=filekey+";"
        file = open(samples[filekey],"r")
        filelines = file.readlines()
        file.close()
        lines[filekey] = [line.split("	",1)[1].strip() for line in filelines] #remove model identifier and trim whitespace
    outputfile = folder+"/"+outputfile[:-1]+".txt"
    f = open(outputfile,"w")
    for _ in range(lineCount):
        mix = ""
        offsets = [0]
        for poss in lines.values():
            text=random.choice(poss)
            mix+=text
            offsets.append(offsets[-1]+len(text))
        mix+="\n"
        f.write(" ".join([str(x) for x in offsets][:-1])+"\n")
        f.write(mix+"\n")
    f.close()


def main(count, input, outputfolder, outputs, lines):
    samples = {}
    for f in os.listdir(input):
        fullpath = f"{input}/{f}"
        keyname = f.split("-test")[0]
        samples[keyname] = fullpath

    combs = list(itertools.permutations(samples.keys(),count))
    random.shuffle(combs)
    combs = combs[:outputs]

    for filelist in combs:
        exportRandomMix(filelist,samples,lines,outputfolder)


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--count",help="How many models we're concatenating",type=int,default=3)
    parser.add_argument("--input", help="test texts folder", required=True)
    parser.add_argument("--outputfolder", help="Output folder", required=True)
    parser.add_argument("--outputs",help="Number of files put out",default=5,type=int)
    parser.add_argument("--lines", help="lines per file",type=int, default=1)
    args = parser.parse_args()
    
    main(args.count, args.input, args.outputfolder, args.outputs, args.lines)

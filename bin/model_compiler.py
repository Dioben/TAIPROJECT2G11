import lzma
import argparse
import os
import json
import gzip

from common_modules import calculateBitCostMap
#compiles all text files in /models into a pickle

def getFileFrequenciesXZ(filename,order): #same as common modules func with for compressed text files
    try:
        file = lzma.open(filename,"rt")
        text= file.read()
        file.close()
    except:
        return None,None,None #bad file

    if len(text)<order:
        raise ValueError("Text is smaller than order")

    alphabet = set(text)
    current_buffer = text[:order]
    text = text[order:]
    table = {}
    appearances={}
    for character in text:
        if current_buffer not in table.keys():
            table[current_buffer]= {}
        if character not in table[current_buffer].keys():
            table[current_buffer][character]=1
        else:
            table[current_buffer][character]+=1
        if current_buffer in appearances.keys():
            appearances[current_buffer]+=1
        else:
            appearances[current_buffer]=1
        current_buffer = current_buffer [1:]+character
        
    return table,appearances,alphabet


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--order",help="Order of the model",type=int,default=3)
    parser.add_argument("--smoothing", help="Smoothing parameter", type=float,default=0.1)
    parser.add_argument("--folder", help="Models folder", default="../models")
    parser.add_argument("--outputprefix", help="Output prefix", default="models/")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.outputprefix), exist_ok=True)
    if args.order<1:
        raise ValueError("Order must be at least 1")
    if args.smoothing<=0:
        raise ValueError("Smoothing must be larger than 0")

    ignores = []
    for f in os.listdir(args.folder):
        keyname = f.removesuffix(".wiki.utf8.xz")
        fullpath = f"{args.folder}/{f}"
        table,appearances,alphabet = getFileFrequenciesXZ(fullpath,args.order)
        if not table:
            ignores.append(keyname)
            continue
        bit_cost_map = calculateBitCostMap(table,alphabet,args.smoothing)
        outputfile = gzip.open(f"{args.outputprefix}{keyname}.tar.gz","wt")
        json.dump({"model":bit_cost_map,"alphabet":sorted(alphabet)},outputfile)
        outputfile.close()
    
    print("Compilation finished")
    print("Failed files:")
    if not ignores:
        print("None")
    else:
        print(ignores)
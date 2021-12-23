import lzma
import argparse
import os
import json
import gzip

from common_modules import calculateBitCostMap
#compiles all text files in /models into a pickle

def getFileFrequenciesXZ(filename,order,fraction): #same as common modules func with for compressed text files
    try:
        try:
            file = open(filename,"rt")
            text = file.read()
            file.close
        except:
            file = lzma.open(filename,"rt")
            text= file.read()
            file.close()
    except:
        return None,None,None #bad file
    
    text = text[0:int(len(text)*fraction)]

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


def main(order, smoothing, folder, outputprefix, fraction):
    os.makedirs(os.path.dirname(outputprefix), exist_ok=True)
    if order<1:
        raise ValueError("Order must be at least 1")
    if smoothing<=0:
        raise ValueError("Smoothing must be larger than 0")
    if fraction>1 or fraction<=0:
        raise ValueError("Percentage must be between [1,0[")

    ignores = []
    for f in os.listdir(folder):
        keyname = f.removesuffix(".utf8").removesuffix(".wiki.utf8.xz")
        fullpath = f"{folder}/{f}"
        table,_,alphabet = getFileFrequenciesXZ(fullpath,order,fraction)
        if not table:
            ignores.append(keyname)
            continue
        bit_cost_map = calculateBitCostMap(table,alphabet,smoothing)
        outputfile = gzip.open(f"{outputprefix}{keyname}.tar.gz","wt")
        json.dump({"model":bit_cost_map,"alphabet":sorted(alphabet)},outputfile)
        outputfile.close()
    return ignores


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--order",help="Order of the model",type=int,default=3)
    parser.add_argument("--smoothing", help="Smoothing parameter", type=float,default=0.1)
    parser.add_argument("--folder", help="Models folder", required=True)
    parser.add_argument("--outputprefix", help="Output prefix", required=True)
    parser.add_argument("--fraction", help="Fraction of each model used", type=float, default=1)
    args = parser.parse_args()

    ignores = main(args.order, args.smoothing, args.folder, args.outputprefix, args.fraction)
    
    print("Compilation finished")
    print("Failed files:")
    if not ignores:
        print("None")
    else:
        print(ignores)
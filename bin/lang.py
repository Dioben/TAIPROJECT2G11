import argparse
from math import log2
import common_modules

if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--order",help="Order of the model",type=int,default=2)
    parser.add_argument("--classsource",help="Class source text file", default="../example/english.txt")
    parser.add_argument("--input",help="Text under anaylisis", default="../example/example.txt")
    parser.add_argument("--smoothing", help="Smoothing parameter", type=float,default=1)

    args = parser.parse_args()

    if args.order<1:
        raise ValueError("Order must be at least 1")
    if args.smoothing<=0:
        raise ValueError("Smoothing must be larger than 0")

    table,_,alphabet = common_modules.getFileFrequencies(args.classsource,args.order)
    bit_cost_map = common_modules.calculateBitCostMap(table,alphabet,args.smoothing)

    start_up = sorted(alphabet)[0]*args.order

    default_cost = -log2(1/len(alphabet)) #in case we haven't seen a prefix
    
    file = open(args.input,"r")
    text= file.read()
    file.close()

    filesize = common_modules.calculateFileSize(bit_cost_map,text,start_up,default_cost)
    print(filesize)
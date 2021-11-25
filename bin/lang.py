import argparse
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
    if args.smoothing<0:
        raise ValueError("Smoothing must be non-negative")

    table,_,alphabet = common_modules.getFileFrequencies(args.classsource,args.order)
    #_,appearances,alphabet2 = common_modules.getFileFrequencies(args.input,args.order)
    
    p_map = common_modules.calculateProbabilityMapSmoothingGT0(table,alphabet,args.smoothing)

    filesize = common_modules.calculateFileSize(p_map,args.input)
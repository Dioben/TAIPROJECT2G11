import argparse
import os
from findlang import main as findlang


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("--classes",help="Class models source folder", required=True)
    parser.add_argument("--input-folder",help="Folder with texts under analysis", required=True)
    args = parser.parse_args()

    costs = {}

    for textName in os.listdir(args.input_folder):
        cost = findlang(f"{args.input_folder}/{textName}", args.classes)
        keyTextName = textName.removesuffix("-test.utf8")
        keyModelName = sorted(cost.keys(), key=lambda x: cost[x])[0]
        costs[keyTextName] = (keyModelName, cost[keyModelName])
    
    # compare text and model name to know if correct
    for textName, (modelName, size) in costs.items():
        print(f'{textName}: {modelName}, {size}')

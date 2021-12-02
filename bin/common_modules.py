import math
import random



def getFileFrequencies(filename,order):
    file = open(filename,"r")
    text= file.read()
    file.close()

    if len(text)<order:
        raise ValueError("Text is smaller than order")

    alphabet = set(text)
    current_buffer = text[:order]
    text = text[order:]
    table = {}
    appearances={}
    for character in text:
        if current_buffer not in table.keys(): #have we seen this predecessor yet?
            table[current_buffer]= {}
        if character not in table[current_buffer].keys(): #have we seen this sequence?
            table[current_buffer][character]=1
        else:
            table[current_buffer][character]+=1
        #REVISED: NO LONGER CONSIDERS LAST CHARACTER
        if current_buffer in appearances.keys():
            appearances[current_buffer]+=1
        else:
            appearances[current_buffer]=1
        current_buffer = current_buffer [1:]+character
        
    return table,appearances,alphabet


def calculateBitCostMap(frequencies,alphabet,smoothing):
    if not smoothing>=0:
        raise ValueError("Smoothing has to be equal to or greater than 0")
    result = {}
    smoothing_denominator = smoothing*len(alphabet)

    for sequence,appearances in frequencies.items():
        total = sum(appearances.values())
        denominator = total+smoothing_denominator
        result[sequence] = { x: -math.log2((y+smoothing)/denominator) for x,y in appearances.items() }
        result[sequence]['default']=-math.log2(smoothing/denominator)
    return result

def calculateFileSize(cost_map,inputfile,start_up,default_cost):
    file = open(inputfile,"r")
    text= file.read()
    file.close()

    current_buffer = start_up
    cost = 0

    for character in text:
        if current_buffer not in cost_map: #do we know this predecessor?
            cost+=default_cost
        else:
            if character in cost_map[current_buffer]: #do we know this follow-up character?
                cost+=cost_map[current_buffer][character]
            else:
                cost+=cost_map[current_buffer]['default']
        current_buffer = current_buffer [1:]+character
        
    return cost

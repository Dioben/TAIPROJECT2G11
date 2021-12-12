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

def calculateFileSize(model,text,start_up,default_cost,notInModelCost):
    current_buffer = start_up
    cost = 0
    cost_map = model['model']
    alphabet = set(model['alphabet'])
    for character in text:
        if character not in alphabet:
            cost+=notInModelCost
        elif current_buffer not in cost_map: #do we know this predecessor?
            cost+=default_cost
        else:
            if character in cost_map[current_buffer]: #do we know this follow-up character?
                cost+=cost_map[current_buffer][character]
            else:
                cost+=cost_map[current_buffer]['default']
        current_buffer = current_buffer [1:]+character
        
    return cost


def calculateFileSizeStopEarly(model,text,start_up,default_cost,notInModelCost,default_limit):
    order = len ( list (model['model'].keys())[0] )
    current_buffer = start_up[-order:]
    cost = 0
    cost_map = model['model']
    alphabet = set(model['alphabet'])
    current_defaults= 0
    checked = 0
    for character in text:
        checked+=1
        if character not in alphabet:
            cost+=notInModelCost
            current_defaults+=1
        elif current_buffer not in cost_map: #do we know this predecessor?
            cost+=default_cost
            current_defaults+=1
        else:
            if character in cost_map[current_buffer]: #do we know this follow-up character?
                cost+=cost_map[current_buffer][character]
                current_defaults=0
            else:
                cost+=cost_map[current_buffer]['default']
                current_defaults+=1
        if current_defaults>=default_limit:
            break
        current_buffer = current_buffer [1:]+character
        
    return cost,checked


def calculateLanguageIntervals(model, text, startup, notInModelCost, windowSize, threshold):
    order = len(list(model['model'].keys())[0])
    costMap = model['model']
    alphabet = set(model['alphabet'])
    defaultCost = -math.log2(1/len(alphabet))
    textLen = len(text)
    currentBuffer = startup[-order:]
    offset = windowSize
    window = text[0:windowSize]
    intervals = []
    validWindow = False
    firstLocalValidOffset = -1
    validLength = 0
    while offset < textLen:
        cost = 0
        localCurrentBuffer = currentBuffer
        for char in window:
            if char not in alphabet:
                cost += notInModelCost
            elif localCurrentBuffer not in costMap:
                cost += defaultCost
            elif char in costMap[localCurrentBuffer]:
                cost += costMap[localCurrentBuffer][char]
            else:
                cost += costMap[localCurrentBuffer]['default']
            localCurrentBuffer = localCurrentBuffer[1:] + char
        if cost/windowSize <= threshold:
            if not validWindow:
                firstLocalValidOffset = offset - windowSize
                validWindow = True
        else:
            if validWindow:
                validLength += offset - windowSize - firstLocalValidOffset
                intervals.append((firstLocalValidOffset, offset - windowSize))
                validWindow = False
        window = window[1:] + text[offset]
        currentBuffer = currentBuffer[1:] + text[offset - windowSize]
        offset += 1
    if validWindow:
        validLength += offset - windowSize - firstLocalValidOffset
        intervals.append((firstLocalValidOffset, offset - windowSize))
    return intervals, validLength

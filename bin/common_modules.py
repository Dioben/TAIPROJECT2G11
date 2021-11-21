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

def calculateProbabilityMap(frequencies,alphabet,smoothing):
    if not smoothing>=0:
        raise ValueError("Smoothing has to be equal to or greater than 0")
    result = {}
    smoothing_denominator = smoothing*len(alphabet)

    for sequence,appearances in frequencies.items():
        total = sum(appearances.values())
        denominator = total+smoothing_denominator
        result[sequence] = { x: (y+smoothing)/denominator for x,y in appearances.items() }
        result[sequence]['default']=smoothing/denominator
    return result

def calculateProbabilityMapSmoothingGT0(frequencies,alphabet,smoothing):
    if not smoothing>0:
        raise ValueError("Smoothing has to be bigger than 0")
    result = {}
    smoothing_denominator = smoothing*len(alphabet)

    for sequence,appearances in frequencies.items():
        total = sum(appearances.values())
        denominator = total+smoothing_denominator
        result[sequence] = { x: (y+smoothing)/denominator for x,y in appearances.items() }
        result[sequence]['default']=smoothing/denominator
    return result


def calculateEntropy(probabilities,appearances,alphabet_len):
    """
    Element entropy:
        - log( probability_of_element_in_row )

    Row entropy:
        sum( probability_of_element_in_row * element_entropy )
    
    Full entropy:
        sum( probability_of_row_key_in_text * row_entropy )
    """
    statetotal = sum(appearances.values())
    rowvalues = {x: -sum([y[z]*math.log2(y[z]) if z!="default" else (alphabet_len-len(y)+1) * (y[z]*math.log2(y[z])) for z in y.keys()]) for x,y in probabilities.items()}
    return sum([rowvalues[state]*appearances[state]/statetotal for state in appearances])


def generateText(probabilities,alphabet,length,start):
    #return length*chars 
    order = len(list(probabilities.keys())[0])
    if len(start)<order:
        raise ValueError("Given start is too small to work with")
    
    alphabet_indexable = list(alphabet) #allow consistent ordering for use in unseen sequences
    alphabet_size = len(alphabet)
    current_buffer = start[-order:]
    generated_string = ""
    #debugging: SO FAR SO GOOD
    known_sequences = probabilities.keys()
    while len(generated_string)<length:
        if current_buffer not in known_sequences:#if we haven't observed this any character is equally likely as a follow-up
            char = alphabet_indexable[math.floor(random.random()*alphabet_size)]
        else:
            seen = probabilities[current_buffer].keys()
            value = random.random()
            cumulative_chance = 0
            for char in seen: #first try with probabilities we already know
                if char!="default":
                    cumulative_chance+=probabilities[current_buffer][char]
                    if cumulative_chance>=value:
                        break
            if cumulative_chance<value: #try to get an unseen letter here
                unseen = alphabet.difference(seen) #might include the word "default" 
                default_add = probabilities[current_buffer]['default']
                for char in unseen:
                    cumulative_chance+=default_add
                    if cumulative_chance>=value:
                        break
                if cumulative_chance>1.0000001 or cumulative_chance<0.99999999: #There may be a rounding error
                    continue #significant rounding error, we will reroll
        generated_string+=char
        current_buffer= current_buffer[1:]+char
    return generated_string


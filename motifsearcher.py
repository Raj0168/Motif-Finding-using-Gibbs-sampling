# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 03:12:18 2014

@author: mit
"""

"""
Module Gibbs contains method to perform Gibbs sampling
"""

from numpy.random import randint
from numpy.random import rand
import numpy as np

def sampling(sequences, w):
    """Perform gibbs sampling to predict the start position of hidden word in a
    sequence"""
    
    K = len(sequences)      # The number of sequence
    
    char_set = set()
    for seq in sequences:
        char_list = list(seq)
        for chara in char_list:
            char_set.add(chara)
    
    alphabet = list(char_set)       # List of all character used in the sequence
    
    # First, randomly set the start position
    pos = [randint(0, len(seq)-w+1) for seq in sequences]  
    
    # Loop until converge (the burn-in phase)
    last_pos = None
    while last_pos != pos:
        last_pos = pos[:]
        
        # We pick the sequence, well, in sequence starting from index 0
        for i in range(K):
            # We sample the next position of magic word in this sequence
            # Therefore, we exclude this sequence from model calculation
            seq_minus = sequences[:]; del seq_minus[i]
            pos_minus = pos[:]; del pos_minus[i]
            q, p = compute_model(seq_minus, pos_minus, alphabet, w)
            
            # We try for every possible position of magic word in sequence i and
            # calculate the probability of it being as background or magic word
            # The probability for magic word is calculated by multiplying the probability
            # for each character in each position
            N = len(sequences[i])
            qx = [1]*(N-w+1)
            px = [1]*(N-w+1)
            for j in range(N-w+1):
                for k in range(w):
                    c = sequences[i][j+k]
                    qx[j] = qx[j] * q[c][k]
                    px[j] = px[j] * p[c]
            
            # Compute the ratio between word and background, the pythonic way
            Aj = [x/y for (x,y) in zip(qx, px)]
            norm_c = sum(Aj)
            Aj = map(lambda x: x/norm_c, Aj)
            #print 'Aj', Aj
            
            # Sampling new position with regards to probability distribution Aj
            pos[i] = sample(range(N-w+1), list(Aj))
        #print pos
    return pos
            
def compute_model(sequences, pos, alphabet, w):
    """
    This method compute the probability model of background and word based on data in 
    the sequences.
    """
    q = {x:[1]*w for x in alphabet}
    p = {x: 1 for x in alphabet}
    
    # Count the number of character occurrence in the particular position of word
    for i in range(len(sequences)):
        start_pos = pos[i]        
        for j in range(w):
            c = sequences[i][start_pos+j]
            q[c][j] += 1
    # Normalize the count
    for c in alphabet:
        for j in range(w):
            q[c][j] = q[c][j] / float( len(sequences)+len(alphabet) )
    
    # Count the number of character occurrence in background position
    # which mean everywhere except in the word position
    for i in range(len(sequences)):
        for j in range(len(sequences[i])):
            if j < pos[i] or j > pos[i]+w:
                c = sequences[i][j]
                p[c] += 1
    # Normalize the count
    total = sum(p.values())
    for c in alphabet:
        p[c] = p[c] / float(total)
    
    return q, p
    
def sample(alphabet, dist):
    """ This method produce a new discrete sample list by alphabet with probability
    distribution given by dist.
    The length of alphabet and dist must be same."""
    sampl = None
    cum_dist = np.cumsum(dist)
    r = rand()
    for i in range(len(dist)):
        if r < cum_dist[i]:
            sampl = alphabet[i]
            break
    
    return sampl

# If this module is used as script
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        w = int(sys.stdin.readline())
        sequences = []
        for line in sys.stdin:
            sequences += [line]
        print(sampling(sequences, w))
    
    elif len(sys.argv) == 2:
        sequences = []
        f = open(sys.argv[1], 'r')
        w = int(f.readline())
        for line in f.readlines():
            sequences += [line[:-1]]
        print(sampling(sequences, w))
        
    else:
        print('Error!!! Either use 1 argument or feed the data directly through standard input. For more information, read the README')

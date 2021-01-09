# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:07:48 2021

@author: timvr
"""
import math
import numpy as np
from itertools import permutations, combinations
from mastermind.arithmetic.comp import compare
from mastermind.arithmetic.count import count, icount
from mastermind.arithmetic.increm import countcnincrement, countcndecrement
from mastermind.arithmetic.qft import qft, iqft

def build_mastermind_a_circuit(circuit, q, a, secret_sequence, do_inverse=False):
    '''
    Counts correct positions and colours in query q according to permutation p.

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to perform counting on.
    q : QuantumRegister
        Query register.
    a : QuantumRegister
        Register which stores amount of correct positions and colours.
    p : Int list
        Permutation of secret string.

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with a oracle.

    '''
    # Amount of colours is the amount of qubits in q divided by the amount of 
    # positions
    amount_colour_bits = len(q)//len(secret_sequence)
    
    # Write p in binary representation
    binary_list = [bin(x)[2:].zfill(amount_colour_bits) for x in secret_sequence]
    
    # Apply x gates to implement permuted secret string
    binary_to_x_gates(circuit, q, binary_list)
    
    # Count the amount of correct qubits
    if not do_inverse:
        count(circuit, q, a, amount_colour_bits)
    else:
        icount(circuit, q, a, amount_colour_bits)
    
    # permute back
    binary_to_x_gates(circuit, q, binary_list)
    
    return circuit

def build_mastermind_b_circuit(circuit, q, b, secret_sequence, do_inverse = False):
    n = len(secret_sequence)
    logk = len(q)//n
    # how often which colour occurs in the list
    secret_sequence_colours_amount = [list(secret_sequence).count(i) for i in range(2**logk)] # rather k, but that's annoying
    
    qft(circuit, b)
    for (c, nc) in enumerate(secret_sequence_colours_amount):
        if nc != 0:
            comp_list = [1] + (nc-1)*[0]
            for nc_q in range(nc+1,n+1):
                n_perm = [math.comb(nc_q,i) for i in range(1,nc_q)]
                res = sum([a*b for a,b in zip(n_perm,comp_list)])
                comp_list += [nc - res]
            binary_list = [bin(c)[2:].zfill(logk)]*n
            binary_to_x_gates(circuit, q, binary_list)
            for i in range(n):
                if not do_inverse:
                    countcnincrement(circuit, q[(logk*i):(logk*(i+1))], b)
                else:
                    countcndecrement(circuit, q[(logk*i):(logk*(i+1))], b)
            for i in range(n-nc):
                j = i+nc
                comp = comp_list[j]
                for combination in list(combinations(range(n), j+1)):
                    qtemptemp = [q[(logk*l):(logk*(l+1))] for l in combination]
                    qtemp = []
                    for qlist in qtemptemp:
                        qtemp += qlist
                    if comp != 0:
                        if not do_inverse:
                            countcnincrement(circuit, qtemp, b, amount=comp)
                        else:
                            countcndecrement(circuit, qtemp, b, amount=comp)
            binary_to_x_gates(circuit, q, binary_list)
    iqft(circuit, b)
    
def binary_to_x_gates(circuit, q, secret_binary):
    '''
    Places an x gate for each 0 of an element of secret_binary

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to add x gates to.
    q : QuantumRegister
        Register to add x gates to.
    secret_binary : str list
        list containing binary strings.

    Returns
    -------
    circuit : QuantumCircuit
        Circuit appended with x gates according to secret_binary.

    '''
    amount_colour_bits = len(secret_binary[0])
    
    for (i,binary) in enumerate(secret_binary):
        for (j,bit) in enumerate(binary[::-1]):
            if bit == '0':
                circuit.x(q[i*amount_colour_bits + j])
            else:
                circuit.i(q[i*amount_colour_bits + j])
    
    return circuit
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:07:48 2021

@author: timvr
"""

import math
import numpy as np
from itertools import permutations, combinations
from mastermind.arithmetic.dradder import cadd, csub
from mastermind.arithmetic.comp import compare
from mastermind.arithmetic.count import count, icount
from mastermind.arithmetic.increm import increment, decrement, cnincrement, cndecrement
from mastermind.arithmetic.qft import qft, iqft


def build_mastermind_a_circuit(circuit, q, a, s, do_inverse=False):
    '''
    Counts a_s(q): the number of correct positions and colours in query q (compared to s).

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to perform counting on.
    q : QuantumRegister, length n*ceil(log(k))
        Query register.
    a : QuantumRegister, length ceil(log(n))+1
        Register which stores amount of correct positions and colours.
    s : Int list, length n
        Permutation of secret string.
    do_inverse : bool (default: False)
        Whether to perform the inverse of the circuit.

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with a-oracle.
    
    '''
    
    # Extract basic system parameters (n = # of pins, k = # of colours, logk = # of bits for k)
    n = len(s)
    logk = len(q)//n
    
    # Write s in binary representation
    binary_list = [bin(x)[2:].zfill(logk) for x in s]
    
    # Apply x gates to implement permuted secret string
    binary_to_x_gates(circuit, q, binary_list)
    
    # Count the amount of correct qubits
    if not do_inverse:
        count(circuit, q, a, logk)
    else:
        icount(circuit, q, a, logk)
    
    # permute back
    binary_to_x_gates(circuit, q, binary_list)
    
    return circuit


def build_mastermind_b_circuit(circuit, q, b, s, do_inverse=False):
    '''
    Counts b_s(q): the number of correct colours in query q (compared to s).

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to perform counting on.
    q : QuantumRegister, length n*ceil(log(k))
        Query register.
    b : QuantumRegister, length ceil(log(n))+1
        Register which stores amount of correct colours.
    s : Int list, length n
        Secret string.
    do_inverse : bool (default: False)
        Whether to perform the inverse of the circuit.

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with b-oracle.
    
    '''
    
    # Extract basic system parameters (n = # of pins, k = # of colours, logk = # of bits for k)
    n = len(s)
    logk = len(q)//n
    
    # how often which colour occurs in the list
    secret_sequence_colours_amount = [list(s).count(i) for i in range(2**logk)] # rather k, but that's annoying
    
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
                    cnincrement(circuit, q[(logk*i):(logk*(i+1))], b, do_qft=False)
                else:
                    cndecrement(circuit, q[(logk*i):(logk*(i+1))], b, do_qft=False)
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
                            cnincrement(circuit, qtemp, b, amount=comp, do_qft=False)
                        else:
                            cndecrement(circuit, qtemp, b, amount=comp, do_qft=False)
            binary_to_x_gates(circuit, q, binary_list)
    iqft(circuit, b)
    
    return circuit


def build_mastermind_b_circuit_v2(circuit, q, b, c, d, s, do_inverse=False):
    '''
    Counts b_s(q): the number of correct colours in query q (compared to s).

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to perform counting on.
    q : QuantumRegister, length n*ceil(log(k))
        Query register.
    b : QuantumRegister, length ceil(log(n))+1
        Register which stores amount of correct colours.
    c : QuantumRegister, length ceil(log(n))+1
        Ancilla register which stores the differences abs(n_s(q)-n_c(q)).
    d : QuantumRegister, length 1
        Ancilla register which stores the sign sgn(n_s(q)-n_c(q)).
    s : Int list, length n
        Secret string.
    do_inverse : bool (default: False)
        Whether to perform the inverse of the circuit.

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with b-oracle.
    
    '''
    
    # Extract basic system parameters (n = # of pins, k = # of colours, logk = # of bits for k)
    n = len(s)
    logk = len(q)//n
    
    # How often which colour occurs in the list
    secret_sequence_colours_amount = [list(s).count(i) for i in range(2**logk)] # rather k, but that's annoying
    
    # Check if valid secret string
    if sum(secret_sequence_colours_amount) != n:
        raise ValueError("Secret string contains illegal values")
    
    
    # Put QFT on reg b outside loop for efficiency
    qft(circuit, b)
    
    # Add n to reg b (equivalent to adding n_c for each c; more efficient)
    increment(circuit, b, amount=n, do_qft=False)
    
    # Flip sign bit d
    circuit.x(d)
    # Loop over colours (and how often they're used)
    for (clr, nc) in enumerate(secret_sequence_colours_amount):
        # Only start counting process is colour is used at all
        if nc != 0:
            
            # Write colour clr in n*binary...
            binary_list = [bin(clr)[2:].zfill(logk)]*n
            # ... to CNOT with query (so if matches, then |11>)
            binary_to_x_gates(circuit, q, binary_list)
            
            if not do_inverse:
                
                # Add n_c(s) to reg c...
                increment(circuit, c, amount=nc, do_qft=True)
                
                # ... and subtract n_c(q) from that value (with sign bit d)
                icount(circuit, q, [*c, d], step=logk, do_qft=True)
                
                # If sign bit d has not flipped (i.e. is True, i.e n_c(q)<n_c(s)):
                #  subtract difference n_c(s)-n_c(q)
                csub(circuit, a=c, b=b, c=d, do_qft=False)
                
                # Undo step 1 & 2
                count(circuit, q, [*c, d], step=logk, do_qft=True)
                decrement(circuit, c, amount=nc, do_qft=True)
                
            else:
                
                # Inverse of steps above
                increment(circuit, c, amount=nc, do_qft=True)
                icount(circuit, q, [*c, d], step=logk, do_qft=True)
                cadd(circuit, a=c, b=b, c=d, do_qft=False)
                decrement(circuit, b, amount=nc, do_qft=False)
                count(circuit, q, [*c, d], step=logk, do_qft=True)
                decrement(circuit, c, amount=nc, do_qft=True)
            
            # Undo query CNOT
            binary_to_x_gates(circuit, q, binary_list)
            circuit.barrier()
    
    # Flip sign bit d
    circuit.x(d)
    
    # Finish sum procedure with iQFT on reg b
    iqft(circuit, b)
    
    return circuit


def binary_to_x_gates(circuit, q, s_bin):
    '''
    Places an x gate for each 0 of an element of s_bin

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to add x gates to.
    q : QuantumRegister, length n*ceil(log(k))
        Register to add x gates to.
    s_bin : str list, length n (and strings of length ceil(log(k)))
        list containing binary strings.

    Returns
    -------
    circuit : QuantumCircuit
        Circuit appended with x gates according to secret_binary.
    
    '''
    
    # Amount of colour bits
    logk = len(s_bin[0])
    
    for (i,binary) in enumerate(s_bin):
        for (j,bit) in enumerate(binary[::-1]):
            if bit == '0':
                # add an X gate for a 0
                circuit.x(q[i*logk + j])
            else:
                # and otherwise an identity for clarity
                circuit.i(q[i*logk + j])
    
    return circuit

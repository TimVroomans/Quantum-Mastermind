# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:08:17 2021

@author: timvr
"""

from mastermind.game.algorithms.Mastermind_Oracle import build_mastermind_circuit, count_permuted
from mastermind.arithmetic.dradder import add, sub
from mastermind.arithmetic.count import count, icount
from mastermind.arithmetic.increm import increment, decrement
from qiskit import QuantumCircuit
import numpy as np

def build_find_colour_positions_circuit(circuit, x, q, a, c, d, secret_sequence):
    '''
    Builds mastermind check circuit on circuit. Requires the inputs q, a, b, c
    and secret_sequence. You can optionally choose to measure the outcomes.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to build mastermind circuit on.
    x : QuantumRegister, length n
        holds binary proto-quereis
    q : QuantumRegister, length n*ceil(log2(k))
        holds two-colour queries to the oracle
    a : QuantumRegister, length 1+ceil(log2(k))
        holds oracle 'a' outputs
    c : integer, c in {0, 1, ..., k-1}
        the colour of which we want to know the positions
    c : integer, d in {0, 1, ..., k-1}
        any colour which does not occur in the secret string
    secret_sequence: List, length n
        Secret sequence.

    Returns
    -------
    circuit : QuantumRegister
        ...

    '''
    print('Building quantum circuit...')
    
    #0: init
    circuit.barrier()
    
    #1: Hadamard
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    #2: build query
    _build_query_two_colours(circuit, x, q, c, d)
    circuit.barrier()
    
    #3: get Oracle a response
    count_permuted(circuit, q=q, a=a, p=secret_sequence)
    circuit.barrier()
    
    #4: Z gate on output LSB
    circuit.z(a[0]) # should be the LSB; maybe that's actually a[-1]!!!!!!!!!!
    circuit.barrier()
    
    #5: undo step 2 & 3
    count_permuted(circuit, q=q, a=a, p=secret_sequence, do_inverse=True)
    _build_query_two_colours(circuit, x, q, c, d)
    circuit.barrier()
    
    #11
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    # Return the check circuit
    return circuit


def build_find_colour_positions_alt_circuit(circuit, x, q, a, b, c, k, secret_sequence):
    '''
    Builds mastermind check circuit on circuit. Requires the inputs q, a, b, c
    and secret_sequence. You can optionally choose to measure the outcomes.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to build mastermind circuit on.
    x : QuantumRegister, length n
        holds binary proto-queries
    q : QuantumRegister, length n*ceil(log2(k))
        holds two-colour queries to the oracle
    a : QuantumRegister, length 1+ceil(log2(k))
        holds oracle 'a' outputs
    b : QuantumRegister, length 1+ceil(log2(k))+ceil(log2(n))
        holds inner product outputs
    c : integer, c in {0, 1, ..., k-1}
        the colour of which we want to know the positions
    k : integer
        number of available colours
    secret_sequence: List, length n
        Secret sequence.

    Returns
    -------
    circuit : QuantumRegister
        ...

    '''
    print('Building quantum circuit...')
    
    logk = int(np.ceil(np.log2(k)))
    
    #0: init
    circuit.barrier()
    
    #1: Hadamard
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    #2: calculate the MMa sum
    for d in range(k):
        #2a: build query
        _build_query_two_colours(circuit, x, q, c, d)
        circuit.barrier()
        
        #2b: get Oracle a response
        count_permuted(circuit, q=q, a=a, p=secret_sequence)
        circuit.barrier()
        
        #2c: add to output reg
        add(circuit, a, b)
        circuit.barrier()
        
        #2d: undo #2a & #2b
        count_permuted(circuit, q=q, a=a, p=secret_sequence, do_inverse=True)
        _build_query_two_colours(circuit, x, q, c, d)
        circuit.barrier()
    
    #3: add the count of c colours to the b reg
    count(circuit, a=x, b=b, step=1)  # or step=-1?????
    circuit.barrier()
    
    #4: ignore the logk LSBs in the b reg
    #... which of course requires literally no code, but I'll add identity gates for clarity
    for i in range(logk):
        circuit.i(b[i])
    circuit.barrier()
    
    #5: decrement the remaining value by 1 to find the desired inner product
    decrement(circuit, b[logk::])
    circuit.barrier()
    
    #6: Z gate on output LSB (the effective LSB, not the actual one)
    circuit.z(b[logk]) # should be the remaining LSB; not exactly sure if this is the correct one!
    circuit.barrier()
    
    #7: undo steps 2 through 5
    increment(circuit, b[logk::])
    for i in range(logk):
        circuit.i(b[i])
    icount(circuit, a=x, b=b, step=1)
    for d in range(k):
        _build_query_two_colours(circuit, x, q, c, d)
        count_permuted(circuit, q=q, a=a, p=secret_sequence)
        sub(circuit, a, b)
        count_permuted(circuit, q=q, a=a, p=secret_sequence, do_inverse=True)
        _build_query_two_colours(circuit, x, q, c, d)
    
    #8
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    # Return the check circuit
    return circuit


def _build_query_two_colours(circuit, x, q, c, d):
    
    n_x = len(x)
    n_q = len(q)
    
    amount_colour_bits = n_q // n_x
    
    binary_c = bin(c)[2:].zfill(amount_colour_bits)
    binary_d = bin(d)[2:].zfill(amount_colour_bits)
    
    for i in range(n_x):
        for (j,bit) in enumerate(binary_c[::-1]):
            if bit == '1':
                circuit.cnot(x[i], q[i*amount_colour_bits + j])
            else:
                pass
        circuit.x(x[i])
        for (j,bit) in enumerate(binary_d[::-1]):
            if bit == '1':
                circuit.cnot(x[i], q[i*amount_colour_bits + j])
            else:
                pass
        circuit.x(x[i])
    
    return circuit


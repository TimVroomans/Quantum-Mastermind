# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:08:17 2021

@author: timvr
"""

from mastermind.game.algorithms.Mastermind_Oracle import build_mastermind_circuit, count_permuted
from qiskit import QuantumCircuit

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
    count_permuted(circuit, q=q, a=a, p=secret_sequence)
    _build_query_two_colours(circuit, x, q, c, d)
    circuit.barrier()
    
    #11
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


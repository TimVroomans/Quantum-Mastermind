# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:08:00 2021

@author: 0tmar
"""


from abc import ABC
import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from experiment.qiskit_experiment import QiskitExperiment
from experiment.util import filter_at
from .game import Game
from mastermind.arithmetic.count import icount
from mastermind.arithmetic.comp import compare
from mastermind.algorithms.Mastermind_Oracle import build_mastermind_circuit

def build_find_colours_circuit(circuit, b0, x, q, b, c, d, e, f, secret_sequence):
    '''
    Builds mastermind check circuit on circuit. Requires the inputs q, a, b, c
    and secret_sequence. You can optionally choose to measure the outcomes.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to build mastermind circuit on.
    a : QuantumRegister
        ...
    b : QuantumRegister
        ...
    c : QuantumRegister
        ...
    . : ...
        ...
    secret_sequence: List
        Secret sequence.

    Returns
    -------
    circuit : QuantumRegister
        ...

    '''
    print('Building quantum circuit...')
    
    #0
    circuit.barrier()
    
    #1
    build_mastermind_circuit(circuit, q=q, a=c, b=b0, c=d, secret_sequence=secret_sequence, keep_a=False)
    circuit.barrier()
    
    #2
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    #3
    _build_query(circuit, x, q)
    circuit.barrier()
    
    #4
    build_mastermind_circuit(circuit, q=q, a=c, b=b, c=d, secret_sequence=secret_sequence, keep_a=False)
    circuit.barrier()
    
    #5
    circuit.x(c[-1])  # should be MSB
    circuit.barrier()
    
    #6
    icount(circuit, a=b, b=c, step=1)  # or step = -1?
    circuit.barrier()
    
    #7
    compare(circuit, a=b, b=c, c=d)
    circuit.barrier()
    
    #8
    circuit.x(e)
    [circuit.x(qubit) for qubit in b0]
    _ncx(circuit, a=b0, b=e)
    [circuit.x(qubit) for qubit in b0]
    
    _ncx(circuit, a=b, b=f)
    _ncx(circuit, a=[c[0], d, e], b=f)
    circuit.x(d)
    _ncx(circuit, a=[b0[0], d, e], b=f)
    _ncx(circuit, a=[x[0], d, e], b=f)
    circuit.x(d)
    circuit.barrier()
    
    #9
    circuit.z(f)
    circuit.barrier()
    
    #10
    circuit.x(d)
    _ncx(circuit, a=[x[0], d, e], b=f)
    _ncx(circuit, a=[b0[0], d, e], b=f)
    circuit.x(d)
    _ncx(circuit, a=[c[0], d, e], b=f)
    _ncx(circuit, a=b, b=f)
    [circuit.x(qubit) for qubit in b0]
    _ncx(circuit, a=b0, b=e)
    [circuit.x(qubit) for qubit in b0]
    circuit.x(e)
    compare(circuit, a=b, b=c, c=d)
    icount(circuit, a=b, b=c, step=1)  # or step = -1?
    circuit.x(c[-1])  # should be MSB
    build_mastermind_circuit(circuit, q=q, a=c, b=b, c=d, secret_sequence=secret_sequence, keep_a=False)
    _build_query(circuit, x, q)
    circuit.barrier()
    
    #11
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    # Return the check circuit
    return circuit


def _build_query(circuit, x, q):
    
    n_x = len(x)
    n_q = len(q)
    
    amount_colour_bits = n_q // n_x
    
    binary_list = [bin(x)[2:].zfill(amount_colour_bits) for x in range(n_x)]
    
    for (i,binary) in enumerate(binary_list):
        for (j,bit) in enumerate(binary[::-1]):
            if bit == '0':
                circuit.cnot(x[i], q[i*amount_colour_bits + j])
            else:
                pass
                # circuit.i(q[i*amount_colour_bits + j])
    
    return circuit


def _ncx(circuit, a, b):
    # a: crtl reg
    # b: single output qubit
    
    na = len(a)
    
    temp_circuit = QuantumCircuit(1)
    temp_circuit.x(0)
    ncx = temp_circuit.to_gate().control(na)
    circuit.append(ncx, [*a, b])
    
    return circuit


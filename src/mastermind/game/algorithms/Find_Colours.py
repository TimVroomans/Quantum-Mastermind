# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:08:00 2021

@author: 0tmar
"""

from mastermind.arithmetic.count import icount
from mastermind.arithmetic.comp import compare

from mastermind.game.algorithms.Mastermind_Oracle import build_mastermind_circuit, count_permuted
from qiskit import QuantumCircuit

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
    
    #0: init
    circuit.barrier()
    
    
    #1: calc b0
    count_permuted(circuit, q=q, a=b0, p=secret_sequence)
    circuit.barrier()
    
    
    #2: Hadamard to get binary proto-query superpos
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    
    #3: build the actual queries
    _build_query(circuit, x, q)
    circuit.barrier()
    
    
    #4: find corresponding oracle b answers
    build_mastermind_circuit(circuit, q=q, a=c, b=b, c=d, secret_sequence=secret_sequence, keep_a=False)
    circuit.barrier()
    
    
    #5: init c reg to k (=power of two)
    circuit.x(c[-1])  # should be MSB
    circuit.barrier()
    
    
    #6: calc ell in reg c
    icount(circuit, a=b, b=c, step=1)  # or step = -1?
    circuit.barrier()
    
    
    #7: boolean 1
    compare(circuit, a=b, b=c, c=d)
    circuit.barrier()
    
    
    #8: boolean 2&3
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
    
    
    #9: Z gate to get inner product rotation
    circuit.z(f)
    circuit.barrier()
    
    
    #10: undo steps 3-8
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
    
    temp_circuit = QuantumCircuit(q,b,c,d) #(beuned inverse of MMb)
    build_mastermind_circuit(temp_circuit, q=q, a=c, b=b, c=d, secret_sequence=secret_sequence, keep_a=False)
    temp_circuit.inverse()
    circuit += temp_circuit
    
    _build_query(circuit, x, q)
    circuit.barrier()
    
    
    #11: get x_s
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
            if bit == '1':
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


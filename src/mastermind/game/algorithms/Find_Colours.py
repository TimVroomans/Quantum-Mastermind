# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:08:00 2021

@author: 0tmar
"""

from itertools import combinations

from mastermind.arithmetic.qft import qft, iqft
from mastermind.arithmetic.increm import increment, decrement, cnincrement, cndecrement, countcnincrement, countcndecrement

from mastermind.arithmetic.count import count, icount
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
    count_permuted(circuit, q, b0, secret_sequence) # MMa == MMb in this case (with input = 0000)
    circuit.barrier()
    
    
    #2: Hadamard to get binary proto-query superpos
    [circuit.h(qubit) for qubit in x]
    circuit.barrier()
    
    
    #3: build the actual queries
    _build_query(circuit, x, q)
    circuit.barrier()
    
    
    #4: find corresponding oracle b answers
    #build_mastermind_circuit(circuit, q=q, a=c, b=b, c=d, secret_sequence=secret_sequence, keep_a=False)
    build_mastermind_circuit_beun(circuit, x, b, secret_sequence)
    circuit.barrier()
    
    
    #5: calc ell in reg c: init to k (=assumed power of two, so 100 for k=4)
    circuit.x(c[-1])  # should be MSB
    icount(circuit, x, c)
    circuit.barrier()
    
    
    #7: boolean 1
    compare(circuit, b0, c, d) # b0 > ell (c)
    circuit.barrier()
    
    
    #8: boolean 2&3
    circuit.x(e)
    [circuit.x(qubit) for qubit in b0]
    _ncx(circuit, b0, e)
    [circuit.x(qubit) for qubit in b0]
    
    circuit.cnot(b[0], f)
    _ncx(circuit, [c[0], d, e], f)
    circuit.x(d)
    _ncx(circuit, [b0[0], d, e], f)
    _ncx(circuit, [x[0], d, e], f)
    circuit.x(d)
    circuit.barrier()
    
    
    #9: Z gate to get inner product rotation
    circuit.z(f)
    circuit.barrier()
    
    
    #10: undo steps 3-8
    circuit.x(d)
    _ncx(circuit, [x[0], d, e], f)
    _ncx(circuit, [b0[0], d, e], f)
    circuit.x(d)
    _ncx(circuit, [c[0], d, e], f)
    circuit.cnot(b[0], f)
    [circuit.x(qubit) for qubit in b0]
    _ncx(circuit, b0, e)
    [circuit.x(qubit) for qubit in b0]
    circuit.x(e)
    
    compare(circuit, b0, c, d)
    count(circuit, x, c)
    circuit.x(c[-1])  # should be MSB
    
    # temp_circuit = QuantumCircuit(q,b,c,d) #(beuned inverse of MMb)
    # build_mastermind_circuit(temp_circuit, q=q, a=c, b=b, c=d, secret_sequence=secret_sequence, keep_a=False)
    # temp_circuit.inverse()
    # circuit += temp_circuit
    ##
    #circuit.reset(b)
    ##
    build_mastermind_circuit_beun(circuit, x, b, secret_sequence, do_inverse=True)
    
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
            if bit == '1': # or '0'?
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


def build_mastermind_circuit_beun(circuit, x, b, secret_sequence, do_inverse=False):
    '''
    Builds mastermind check circuit on circuit. Requires the inputs q, a, b, c
    and secret_sequence. You can optionally choose to measure the outcomes.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to build mastermind circuit on.
    q : QuantumRegister
        Query register.
    a : QuantumRegister
        Register for correct colours and positions.
    b : QuantumRegister
        Register for maximum number of correct colours and positions of all
        permutations of secret_sequence.
    c : QuantumRegister
        Registers which compares a>b, len(c)=1.
    secret_sequence : List
        Secret sequence.

    Returns
    -------
    circuit : QuantumRegister
        Circuit appended with mastermind circuit.

    '''
    print('Building quantum circuit...')
    
    k = len(x)
    
    # how often which colour occurs in the list
    secret_sequence_colours_amount = [list(secret_sequence).count(i) for i in range(k)]
    
    for (c, nc) in enumerate(secret_sequence_colours_amount):
        if c == 0:
            if nc != 0:
                if not do_inverse:
                    increment(circuit, b)
                else:
                    decrement(circuit, b)
                circuit.barrier()
                if nc > 1:
                    qft(circuit, b)
                    circuit.barrier()
                    for c in range(1,k):
                        circuit.x(x[c])
                    circuit.barrier()
                    for c in range(1,k):
                        if not do_inverse:
                            countcnincrement(circuit, [x[c]], b)
                        else:
                            countcndecrement(circuit, [x[c]], b)
                    circuit.barrier()
                    for i in range(k-nc):
                        j = i+nc
                        sgn = i%2
                        for combination in list(combinations(range(1, k), j)):
                            xtemp = [x[l] for l in combination]
                            if (sgn ^ do_inverse):
                                countcnincrement(circuit, xtemp, b)
                            else:
                                countcndecrement(circuit, xtemp, b)
                    circuit.barrier()
                    for c in range(1,k):
                        circuit.x(x[c])
                    circuit.barrier()
                    iqft(circuit, b)
            else:
                circuit.i(x[c])
                for i in range(len(b)):
                    circuit.i(b[i])
        else:
            if nc != 0:
                if not do_inverse:
                    cnincrement(circuit, [x[c]], b)
                else:
                    cndecrement(circuit, [x[c]], b)
            else:
                circuit.i(x[c])
                for i in range(len(b)):
                    circuit.i(b[i])
        circuit.barrier()
    
    # Return the check circuit
    return circuit


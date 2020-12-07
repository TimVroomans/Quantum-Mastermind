"""
Created on Wed Dec  2 18:25:35 2020

@author: Gielc
"""
from math import pi
from qiskit import *
from qft import qft, iqft
def increment(circuit, q, n):
    """Adds +1 on the first n qubits of circuit"""
    qft(circuit, q, n)
    for qubit in range(q,q+n):
        circuit.rz(pi/2**(n+q-1-qubit), qubit)    
    iqft(circuit, q, n)
    return circuit
def decrement(circuit, q, n):
    """Subtracts +1 on the first n qubits of circuit"""
    qft(circuit, q, n)
    for qubit in range(q,q+n):
        circuit.rz(-pi/2**(n+q-1-qubit), qubit)    
    iqft(circuit, q, n)
    return circuit
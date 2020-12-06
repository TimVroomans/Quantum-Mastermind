"""
Created on Wed Dec  2 18:25:35 2020

@author: Gielc
"""
from math import pi
from qft import qft, iqft

def increment(circuit, n):
    """Adds +1 on the first n qubits of circuit"""
    qft(circuit,n)
    for qubit in range(n):
        circuit.rz(pi/2**(n-1-qubit), qubit)    
    iqft(circuit,n)
    return circuit

def decrement(circuit, n):
    """Subtracts +1 on the first n qubits of circuit"""
    qft(circuit,n)
    for qubit in range(n):
        circuit.rz(-pi/2**(n-1-qubit), qubit)    
    iqft(circuit,n)
    return circuit
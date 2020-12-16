# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:46:05 2020

@author: Giel Coemans
implements positive integer addition and subtraction functions based on a Draper Adder
"""

from math import pi
from qiskit import *
from mastermind.arithmetic.qft import qft, iqft
def dradloop(circuit, a, b, n, m):
    if m >= n:
        return circuit
    m += 1
    for (qubit) in range(m):
        """Does not actually take the mth qubit of circuit for the actual operation"""
        circuit.cp(pi/2**(m-qubit-1), a[n-m],b[qubit])
    circuit.barrier()
    dradloop(circuit,a,b,n,m)
def add(circuit, a, b):
    """Adds the first na qubits from qubit a to the first nb qubits from qubit b"""
    """if a and b are of unequal length, a must be the shorter number"""
    n = len(b)
    m = len(b)-len(a) 
    circuit.barrier()
    qft(circuit, b)
    circuit.barrier()
    #repeat loop
    dradloop(circuit, a, b, n, m)
    iqft(circuit, b)
    return circuit
def dradsubloop(circuit, a, b, n, m):
    if m >= n:
        return circuit
    m += 1
    for (qubit) in range(m):
        """Does not actually take the mth qubit of circuit for the actual operation"""
        circuit.cp(-pi/2**(m-qubit-1), a[n-m],b[qubit])
    circuit.barrier()
    dradsubloop(circuit,a,b,n,m)
def sub(circuit, a, b):
    """Adds the first na qubits from qubit a to the first nb qubits from qubit b"""
    """if a and b are of unequal length, a must be the shorter number"""
    n = len(b)
    m = len(b)-len(a) 
    circuit.barrier()
    qft(circuit, b)
    circuit.barrier()
    #repeat loop
    dradsubloop(circuit, a, b, n, m)
    iqft(circuit, b)
    return circuit
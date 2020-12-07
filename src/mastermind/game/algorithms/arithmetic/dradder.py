# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:46:05 2020

@author: Giel Coemans
implements positive integer addition and subtraction functions based on a Draper Adder
"""

from math import pi
from qiskit import *
from qft import qft, iqft
def dradloop(circuit, a, b, n, m):
    if m >= n:
        return circuit
    m += 1
    for qubit in range(m):
        circuit.cp(pi/2**(m-qubit-1), a+n-m,b+qubit)
    circuit.barrier()
    dradloop(circuit,a,b,n, m)
def adder(circuit, a, b, na, nb):
    """Adds the first na qubits from qubit a to the first nb qubits from qubit b"""
    """if a and b are of unequal length, a must be the shorter number"""
    if na > nb:
        print("Draper Adder Error: a must be of smaller length than b!")
    n = nb
    m = n-na 
    circuit.barrier()
    qft(circuit, b, n)
    circuit.barrier()
    #repeat loop
    dradloop(circuit, a, b, n, m)
    iqft(circuit, b, n)
    return circuit
def drapsubloop(circuit, a, b, n, m):
    if m >= n:
        return circuit
    m += 1
    for qubit in range(m):
        circuit.cp(-pi/2**(m-qubit-1), a+n-m,b+qubit)
    circuit.barrier()
    drapsubloop(circuit,a,b,n, m)
def subber(circuit, a, b, na, nb):
    """subtracts the first na qubits from qubit a to the first nb qubits from qubit b"""
    """if a and b are of unequal size, a must be the shorter number"""
    if na > nb:
        print("Draper Subtractor Error: a must be of smaller length than b!")
    n = nb
    m = n-na 
    circuit.barrier()
    qft(circuit, b, n)
    circuit.barrier()
    #repeat loop
    drapsubloop(circuit, a, b, n, m)
    iqft(circuit, b, n)
    return circuit
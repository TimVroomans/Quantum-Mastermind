# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 14:56:56 2020

@author: Giel
"""
from qiskit import *
from mastermind.arithmetic.qft import qft, iqft
from mastermind.arithmetic.increm import countcnincrement, countcndecrement

def k4count(circuit, a1, an, b1, bn):
    """"Count function for 4 colours. Takes a1 to an-1 as control qubits. Adds to b (b1, bn-1) """
    circuit.barrier()
    qft(circuit, b1, bn)
    for qubit in range(a1,an+a1,2):
        countcnincrement(circuit, b1, bn, qubit, 2)
    iqft(circuit, b1, bn)
    circuit.barrier()
    return circuit 
def ik4count(circuit, a1, an, b1, bn):
    """"Inverse Count function for 4 colours. Takes a1 to an-1 as control qubits. Subtracts to b (b1, bn-1) """
    circuit.barrier()
    qft(circuit, b1, bn)
    for qubit in range(a1,an+a1,2):
        countcndecrement(circuit, b1, bn, qubit, 2)
    iqft(circuit, b1, bn)
    circuit.barrier()
    return circuit 
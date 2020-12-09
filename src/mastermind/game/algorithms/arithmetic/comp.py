# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:23:00 2020

@author: Giel
"""
from math import pi
from qiskit import *
from qft import qft, iqft
from dradder import adder, subber
def compare(circuit, a, b, na, nb):
    """ Length of b must be >= a. Checks if b>a. a, b first qubits, na, nb length of numbers"""
    circuit.barrier()
    subber(circuit, a, b, na, nb+1)
    circuit.barrier()
    adder(circuit, a, b, na, nb)
    circuit.barrier()
    return circuit
    
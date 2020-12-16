# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:23:00 2020

@author: Giel
"""
from qiskit import *
from mastermind.arithmetic.qft import qft, iqft
from mastermind.arithmetic.dradder import add, sub
def compare(circuit, a, b, c):
    """ Length of b must be >= a. Checks if b>a. a, b first qubits, na, nb length of numbers"""
    sub(circuit, a,[*b,*c])
    add(circuit, a, b)
    return circuit
    
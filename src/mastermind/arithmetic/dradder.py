# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:46:05 2020

@author: Giel Coemans
implements positive integer addition and subtraction functions based on a Draper Adder
"""

from math import pi
from qiskit import *
from mastermind.arithmetic.qft import qft, iqft


def dradloop(circuit, a, b, n, m, amount=1):
    if m >= n:
        return circuit
    m += 1
    for (qubit) in range(m):
        """Does not actually take the mth qubit of circuit for the actual operation"""
        circuit.cp(amount*pi/2**(m-qubit-1), a[n-m], b[qubit])
    #circuit.barrier()
    dradloop(circuit, a, b, n, m, amount)
        
    return circuit


def add(circuit, a, b, do_qft=True, amount=1):
    """Adds the first na qubits from qubit a to the first nb qubits from qubit b"""
    """if a and b are of unequal length, a must be the shorter number"""
    n = len(b)
    m = len(b)-len(a) 
    circuit.barrier()
    if do_qft:
        qft(circuit, b)
        circuit.barrier()
    #repeat loop
    dradloop(circuit, a, b, n, m, amount)
    if do_qft:
        iqft(circuit, b)
        circuit.barrier()
        
    return circuit


def dradsubloop(circuit, a, b, n, m, amount=1):
    if m >= n:
        return circuit
    m += 1
    for (qubit) in range(m):
        """Does not actually take the mth qubit of circuit for the actual operation"""
        circuit.cp(-amount*pi/2**(m-qubit-1), a[n-m], b[qubit])
    #circuit.barrier()
    dradsubloop(circuit, a, b, n, m, amount)
        
    return circuit


def sub(circuit, a, b, do_qft=True, amount=1):
    """Adds the first na qubits from qubit a to the first nb qubits from qubit b"""
    """if a and b are of unequal length, a must be the shorter number"""
    n = len(b)
    m = len(b)-len(a) 
    circuit.barrier()
    if do_qft:
        qft(circuit, b)
        circuit.barrier()
    #repeat loop
    dradsubloop(circuit, a, b, n, m, amount)
    if do_qft:
        iqft(circuit, b)
        circuit.barrier()
        
    return circuit


def cadd(circuit, a, b, c, do_qft=True, amount=1):
    n = len(b)
    m = len(b)-len(a) 
    nc = len(c)
    
    circuit.barrier()
    
    if do_qft:
        qft(circuit, b)
        circuit.barrier()
    
    qcs = QuantumCircuit(a,b)
    dradloop(qcs, a, b, n, m, amount)
    cdradloop = qcs.to_gate().control(nc)
    circuit.append(cdradloop, [*c, *a, *b])
    circuit.barrier()
    
    if do_qft:
        iqft(circuit, b)
        circuit.barrier()
        
    return circuit


def csub(circuit, a, b, c, do_qft=True, amount=1):
    n = len(b)
    m = len(b)-len(a) 
    nc = len(c)
    
    circuit.barrier()
    
    if do_qft:
        qft(circuit, b)
        circuit.barrier()
    
    qcs = QuantumCircuit(a,b)
    dradsubloop(qcs, a, b, n, m, amount)
    cdradsubloop = qcs.to_gate().control(nc)
    circuit.append(cdradsubloop, [*c, *a, *b])
    circuit.barrier()
    
    if do_qft:
        iqft(circuit, b)
        circuit.barrier()
        
    return circuit
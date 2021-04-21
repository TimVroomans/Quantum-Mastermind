# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 14:56:56 2020

@author: Giel
"""
from qiskit import *
from mastermind.arithmetic.qft import qft, iqft
from mastermind.arithmetic.increm import cnincrement, cndecrement

def count(circuit, a, b, step=1):
    '''
    Count function for k colours. Takes register a as control qubits. 
    Counts in register b 

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to be appended with counter.
    a : QuantumRegister
        Control register a
    b : QuantumRegister
        Count register b
    step : int
        the length of each individual sub-interval in register a

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with counter

    '''
    
    # Constants
    an = len(a)
    bn = len(b)
    
    # QFT
    circuit.barrier()
    qft(circuit, b)
    
    # Core count sub blocks
    for (i,qubit) in enumerate(a[0:an:step]):
        cnincrement(circuit, a[(i*step):(i+1)*step], b, do_qft=False)
    
    # iQFT
    iqft(circuit, b)
    circuit.barrier()
    
    return circuit 


def icount(circuit, a, b, step=1):
    '''
    Count function for k colours. Takes register a as control qubits. 
    Counts in register b 

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to be appended with counter.
    a  : QuantumRegister
        Control register a
    b  : QuantumRegister
        Count register b
    step : int
        the length of each individual sub-interval in register a

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with counter

    '''
    
    # Constants
    an = len(a)
    bn = len(b)
    
    # QFT
    circuit.barrier()
    qft(circuit, b)
    
    # Core count sub blocks
    for (i,qubit) in enumerate(a[0:an:step]):
        cndecrement(circuit, a[(i*step):(i+1)*step], b, do_qft=False)
    
    # iQFT
    iqft(circuit, b)
    circuit.barrier()
    
    return circuit 
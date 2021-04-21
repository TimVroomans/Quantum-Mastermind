# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 14:58:05 2020

@author: Gielc
"""
from numpy import pi
from qiskit import QuantumCircuit, execute, Aer

def qft_rotations(circuit, q):
    n = len(q)
    '''
    Performs qft on the first n qubits from qubit register q in circuit
    (without swaps)

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum Circuit to perform QFT upon.
    q : QuantumRegister
        Register to perform QFT upon.
    n : Integer, optional
        Perform QFT upon first n qubits of q. The default is len(q).

    Returns
    -------
    circuit : QuantumCircuit
        Quantum Circuit appended with QFT rotations.

    '''
    
    # No qubits = no QFT
    if n == 0:
        return circuit
    
    # Decrement n to accomodate starting index at 0
    n -= 1
    
    # Apply R_1 = H to the qubit
    circuit.h(q[n])
    
    # For the remaining qubits apply the gates R_i controlled by qubit i.
    for (i,qubit) in enumerate(q[0:n]):
        circuit.cp(pi/2**(n-i), qubit, q[n])
        
    # At the end of our function, we call the same function again on
    # the next qubits (we reduced n by one earlier in the function)
    qft_rotations(circuit, q[0:n])
    
    return circuit

    
def swap_registers(circuit, q):
    '''
    Function to swap registers at the end of QFT

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum Circuit to perform QFT upon.
    q : QuantumRegister
        Register to perform QFT upon.
    n : Integer, optional
        Perform QFT upon first n qubits of q. The default is len(q).

    Returns
    -------
    circuit : QuantumCircuit
        Quantum Circuit appended with end of QFT swaps.
    
    '''
    
    n = len(q)
    
    for i in range(n//2):
        circuit.swap(q[i], q[n-1-i])
        
    return circuit


def qft(circuit, q):
    '''
    QFT on the first n qubits from q in circuit
    Simply combines qft_rotations() and swap_registers()

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum Circuit to perform QFT upon.
    q : QuantumRegister
        Register to perform QFT upon.
    n : Integer, optional
        Perform QFT upon first n qubits of q. The default is len(q).

    Returns
    -------
    circuit : QuantumCircuit
        Quantum Circuit appended with QFT.
    
    '''
    
    qft_rotations(circuit, q)
    swap_registers(circuit, q)
    
    return circuit


def iqft(circuit, q):
    '''
    Does the inverse QFT on the first n qubits from q in circuit
    
    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum Circuit to perform inverse QFT upon.
    q : QuantumRegister
        Register to perform inverse QFT upon.
    n : Integer, optional
        Perform inverse QFT upon first n qubits of q. The default is len(q).

    Returns
    -------
    circuit : QuantumCircuit
        Quantum Circuit appended with inverse QFT.
    
    '''
    
    n = len(q)
    
    # First we create a QFT circuit of the correct size:
    qft_circ = QuantumCircuit(n)
    qft_circ = qft(qft_circ, qft_circ.qubits)
    
    # Then we take the inverse of this circuit
    invqft_circ = qft_circ.inverse()
    
    # And add it to the first n qubits in our existing circuit
    circuit.append(invqft_circ, q[0:n])
    
    # .decompose() allows us to see the individual gates
    return circuit.decompose()
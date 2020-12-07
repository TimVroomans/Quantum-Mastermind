"""
Created on Wed Dec  2 18:25:35 2020

@author: Giel Coemans
"""
from math import pi
from qiskit import *
from qft import qft, iqft
def increment(circuit, q, n):
    """Adds +1 on number spanned by qubits q to q+n"""
    qft(circuit, q, n)
    for qubit in range(q,q+n):
        circuit.rz(pi/2**(n+q-1-qubit), qubit)    
    iqft(circuit, q, n)
    return circuit
def decrement(circuit, q, n):
    """Subtracts +1 on number spanned by qubits q to q+n"""
    qft(circuit, q, n)
    for qubit in range(q,q+n):
        circuit.rz(-pi/2**(n+q-1-qubit), qubit)    
    iqft(circuit, q, n)
    return circuit
def c2increment(circuit, q, n, c1, c2):
    """Adds +1. On qubits q to q+n of circuit with control qubits c1 and c2"""
    circuit.barrier()
    qft(circuit, q, n)
    circuit.barrier()
    for qubit in range(q, q+n):
        circuit.cp(pi/2**(n+q-qubit), c2,qubit)
        circuit.cx(c1,c2)
        circuit.cp(-pi/2**(n+q-qubit), c2,qubit)
        circuit.cx(c1,c2)
        circuit.cp(pi/2**(n+q-qubit), c1,qubit)
    circuit.barrier()
    iqft(circuit, q, n)
    circuit.barrier()
    return circuit
def c2decrement(circuit, q, n, c1, c2):
    """Subtracts +1. On qubits q to q+n of circuit with control qubits c1 and c2"""
    circuit.barrier()
    qft(circuit, q, n)
    circuit.barrier()
    for qubit in range(q, q+n):
        circuit.cp(-pi/2**(n+q-qubit), c2,qubit)
        circuit.cx(c1,c2)
        circuit.cp(+pi/2**(n+q-qubit), c2,qubit)
        circuit.cx(c1,c2)
        circuit.cp(-pi/2**(n+q-qubit), c1,qubit)
    circuit.barrier()
    iqft(circuit, q, n)
    circuit.barrier()
    return circuit
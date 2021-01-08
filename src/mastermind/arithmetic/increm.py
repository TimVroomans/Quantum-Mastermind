"""
Created on Wed Dec  2 18:25:35 2020

@author: Giel Coemans
"""
from math import pi
from qiskit import *
from mastermind.arithmetic.qft import qft, iqft

def increment(circuit, q):
    """Adds +1 on number spanned by qubits q to q+n-1"""
    n = len(q)
    qft(circuit, q)
    for (i,qubit) in enumerate(q):
        circuit.rz(pi/2**(n-1-i), qubit)    
    iqft(circuit, q)
    return circuit
def decrement(circuit, q):
    """Subtracts +1 on number spanned by qubits q to q+n-1"""
    n = len(q)
    qft(circuit, q)
    for (i,qubit) in enumerate(q):
        circuit.rz(-pi/2**(n-1-i), qubit)    
    iqft(circuit, q)
    return circuit
# def c2increment(circuit, q, n, c1, c2):
#     """Adds +1. On qubits q to q+n-1 of circuit with control qubits c1 and c2"""
#     circuit.barrier()
#     qft(circuit, q, n)
#     circuit.barrier()
#     for qubit in range(q, q+n):
#         circuit.cp(pi/2**(n+q-qubit), c2,qubit)
#         circuit.cx(c1,c2)
#         circuit.cp(-pi/2**(n+q-qubit), c2,qubit)
#         circuit.cx(c1,c2)
#         circuit.cp(pi/2**(n+q-qubit), c1,qubit)
#     circuit.barrier()
#     iqft(circuit, q, n)
#     circuit.barrier()
#     return circuit
# def c2decrement(circuit, q, n, c1, c2):
#     """Subtracts +1. On qubits q to q+n-1 of circuit with control qubits c1 and c2"""
#     circuit.barrier()
#     qft(circuit, q, n)
#     circuit.barrier()
#     for qubit in range(q, q+n):
#         circuit.cp(-pi/2**(n+q-qubit), c2,qubit)
#         circuit.cx(c1,c2)
#         circuit.cp(+pi/2**(n+q-qubit), c2,qubit)
#         circuit.cx(c1,c2)
#         circuit.cp(-pi/2**(n+q-qubit), c1,qubit)
#     circuit.barrier()
#     iqft(circuit, q, n)
#     circuit.barrier()
#     return circuit
def cnincrement(circuit, c, q):
    n = len(q)
    nc = len(c)
    """Adds +1. On qubits q to q+n-1 of circuit with nc control qubits from qubit c1"""
    circuit.barrier()
    qft(circuit, q)
    circuit.barrier()
    for (i,qubit) in enumerate(q):
        qcs = QuantumCircuit(1)
        qcs.rz(pi/2**(n-i-1),0)
        ncrz = qcs.to_gate().control(nc)
        circuit.append(ncrz, [*c, qubit])
    circuit.barrier()
    iqft(circuit, q)
    circuit.barrier()
    return circuit
def cndecrement(circuit, c, q):
    n = len(q)
    nc = len(c)
    """Subtracts +1. On qubits q to q+n-1 of circuit with nc control qubits from qubit c1"""
    circuit.barrier()
    qft(circuit, q)
    circuit.barrier()
    for (i,qubit) in enumerate(q):
        qcs = QuantumCircuit(1)
        qcs.rz(-pi/2**(n-i-1),0)
        ncrz = qcs.to_gate().control(nc)
        circuit.append(ncrz, [*c, qubit])
    circuit.barrier()
    iqft(circuit, q)
    circuit.barrier()
    return circuit

def countcnincrement(circuit, c, q):
    '''
    Does the same as cnincrement but does not perform an automatic qft and
    iqft at the start/end

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to be appended with increment.
    q : QuantumRegister
        Register to be incremented.
    n : Integer
        Amount of qubits available in q for increment.
    c  : Qubit List
        control qubits

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with increment.

    '''
    n = len(q)
    nc = len(c)
    circuit.barrier()
    for (i,qubit) in enumerate(q):
        qcs = QuantumCircuit(1)
        qcs.rz(pi/2**(n-i-1),0)
        ncrz = qcs.to_gate().control(nc)
        circuit.append(ncrz, [*c, qubit])
    circuit.barrier()
    return circuit

def countcndecrement(circuit, c, q):
    """Does the same as cndecrement but does not perform an automatic qft and iqft at the start/end"""
    n = len(q)
    nc = len(c)
    circuit.barrier()
    for (i,qubit) in enumerate(q):
        qcs = QuantumCircuit(1)
        qcs.rz(-pi/2**(n-i-1),0)
        ncrz = qcs.to_gate().control(nc)
        circuit.append(ncrz, [*c, qubit])
    circuit.barrier()
    return circuit
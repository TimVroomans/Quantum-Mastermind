"""
Created on Wed Dec  2 18:25:35 2020

@author: Giel Coemans
"""
from math import pi
from qiskit import *
from mastermind.arithmetic.qft import qft, iqft

def increment(circuit, q, n):
    """Adds +1 on number spanned by qubits q to q+n-1"""
    qft(circuit, q, n)
    for qubit in range(q,q+n):
        circuit.rz(pi/2**(n+q-1-qubit), qubit)    
    iqft(circuit, q, n)
    return circuit
def decrement(circuit, q, n):
    """Subtracts +1 on number spanned by qubits q to q+n-1"""
    qft(circuit, q, n)
    for qubit in range(q,q+n):
        circuit.rz(-pi/2**(n+q-1-qubit), qubit)    
    iqft(circuit, q, n)
    return circuit
def c2increment(circuit, q, n, c1, c2):
    """Adds +1. On qubits q to q+n-1 of circuit with control qubits c1 and c2"""
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
    """Subtracts +1. On qubits q to q+n-1 of circuit with control qubits c1 and c2"""
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
def cnincrement(circuit, q, n, c1, nc):
    """Adds +1. On qubits q to q+n-1 of circuit with nc control qubits from qubit c1"""
    circuit.barrier()
    qft(circuit, q, n)
    circuit.barrier()
    for qubit in range(q, q+n):
        qcs = QuantumCircuit(1)
        qcs.rz(pi/2**(n+q-qubit-1),0)
        ncrz = qcs.to_gate().control(nc)
        circuit.append(ncrz, [*range(c1,c1+nc), qubit])
    circuit.barrier()
    iqft(circuit, q, n)
    circuit.barrier()
    return circuit
def cndecrement(circuit, q, n, c1, nc):
    """Subtracts +1. On qubits q to q+n-1 of circuit with nc control qubits from qubit c1"""
    circuit.barrier()
    qft(circuit, q, n)
    circuit.barrier()
    for qubit in range(q, q+n):
        qcs = QuantumCircuit(1)
        qcs.rz(-pi/2**(n+q-qubit-1),0)
        ncrz = qcs.to_gate().control(nc)
        circuit.append(ncrz, [*range(c1,c1+nc), qubit])
    circuit.barrier()
    iqft(circuit, q, n)
    circuit.barrier()
    return circuit

def countcnincrement(circuit, q, n, c):
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
    circuit.barrier()
    for (i,qubit) in enumerate(q[0:n]):
        qcs = QuantumCircuit(1)
        phi = pi/2**(n-i)
        #phi = pi/2**(n+q-qubit-1)
        qcs.rz(phi,0)
        ncrz = qcs.to_gate().control(len(c))
        circuit.append(ncrz, [c, qubit], [])
    circuit.barrier()
    return circuit

def countcndecrement(circuit, q, n, c1, nc):
    """Does the same as cndecrement but does not perform an automatic qft and iqft at the start/end"""
    circuit.barrier()
    for qubit in range(q, q+n):
        qcs = QuantumCircuit(1)
        qcs.rz(-pi/2**(n+q-qubit-1),0)
        ncrz = qcs.to_gate().control(nc)
        circuit.append(ncrz, [*range(c1,c1+nc), qubit])
    circuit.barrier()
    return circuit
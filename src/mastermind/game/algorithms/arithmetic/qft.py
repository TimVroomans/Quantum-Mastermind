import numpy as np
from numpy import pi
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram, plot_bloch_multivector
def qft_rotations(circuit, q, n):
    """Performs qft on the first n qubits from qubit q in circuit (without swaps)"""
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n+q)
    for qubit in range(q, q+n):
        circuit.cp(pi/2**(n+q-qubit), qubit, q+n)
    # At the end of our function, we call the same function again on
    # the next qubits (we reduced n by one earlier in the function)
    qft_rotations(circuit, q, n)

def swap_registers(circuit, q, n):
    for qubit in range(n//2):
        circuit.swap(q+qubit, q+n-qubit-1)
    return circuit

def qft(circuit, q, n):
    """QFT on the first n qubits from q in circuit"""
    qft_rotations(circuit, q, n)
    swap_registers(circuit, q, n)
    return circuit
def iqft(circuit, q, n):
    """Does the inverse QFT on the first n qubits from q in circuit"""
    # First we create a QFT circuit of the correct size:
    qft_circ = qft(QuantumCircuit(n), 0, n)
    # Then we take the inverse of this circuit
    invqft_circ = qft_circ.inverse()
    # And add it to the first n qubits in our existing circuit
    circuit.append(invqft_circ, circuit.qubits[q:n+q])
    return circuit.decompose() # .decompose() allows us to see the individual gates
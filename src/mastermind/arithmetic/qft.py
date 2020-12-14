import numpy as np
from numpy import pi
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram, plot_bloch_multivector

"""
@Giel: De enige verandering is als volgt: nu worden qubits aangewezen via hun
index in het Quantum Register waar ze bij horen. Dit stelde ik voor omdat het
bij grotere circuits snel onoverzichtelijk wordt om qubits bij hun globale
index aan te roepen.

Verder heb ik n = len(q) de default gemaakt voor alle functies.
"""

def qft_rotations(circuit, q, n=None):
    if n is None:
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
        circuit.cp(pi/2**(i+1), qubit, q[n])
    # At the end of our function, we call the same function again on
    # the next qubits (we reduced n by one earlier in the function)
    qft_rotations(circuit, q, n)

def swap_registers(circuit, q, n=None):
    if n is None:
        n = len(q)
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
    for i in range(n//2):
        circuit.swap(q[i], q[n-1-i])
    return circuit

def qft(circuit, q, n=None):
    if n is None:
        n = len(q)
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
    qft_rotations(circuit, q, n)
    swap_registers(circuit, q, n)
    return circuit

def iqft(circuit, q, n=None):
    if n is None:
        n = len(q)
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
    # First we create a QFT circuit of the correct size:
    qft_circ = qft(QuantumCircuit(n), 0, n)
    # Then we take the inverse of this circuit
    invqft_circ = qft_circ.inverse()
    # And add it to the first n qubits in our existing circuit
    circuit.append(invqft_circ, q[0:n-1])
    # .decompose() allows us to see the individual gates
    return circuit.decompose() 
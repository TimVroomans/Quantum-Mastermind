# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:07:48 2021

@author: timvr
"""
from itertools import permutations
from mastermind.arithmetic.comp import compare
from mastermind.arithmetic.count import count

def build_mastermind_circuit(circuit, q, a, b, c, secret_sequence, keep_a=True):
    '''
    Builds mastermind check circuit on circuit. Requires the inputs q, a, b, c
    and secret_sequence. You can optionally choose to measure the outcomes.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to build mastermind circuit on.
    q : QuantumRegister
        Query register.
    a : QuantumRegister
        Register for correct colours and positions.
    b : QuantumRegister
        Register for maximum number of correct colours and positions of all
        permutations of secret_sequence.
    c : QuantumRegister
        Registers which compares a>b, len(c)=1.
    secret_sequence : List
        Secret sequence.

    Returns
    -------
    circuit : QuantumRegister
        Circuit appended with mastermind circuit.

    '''
    print('Building quantum circuit...')
    
    # Find all permutations of the secret sequence
    # Reverse order because we want to end with the secret sequence
    permutation_list = [p for p in permutations(secret_sequence)]
    permutation_list.reverse()  
    
    # Build a mastermind stage for each permutation
    for (i,p) in enumerate(permutation_list):
        if i != len(permutation_list)-1:
            mastermind_stage(circuit, q, a, b, c, p)
            print('building stage ', i+1, ' of ', len(permutation_list), '...')
        else:
            mastermind_stage(circuit, q, a, b, c, p, keep_a)
            print('building last stage...')
    
    # Return the check circuit
    return circuit
    
def mastermind_stage(circuit, q, a, b, c, p, keep_a=False):
    '''
    Builds a mastermind oracle stage on circuit. requires inputs circuit, q, a,
    b, c and p. Last is an optional input.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to build mastermind circuit on.
    q : QuantumRegister
        Query register.
    a : QuantumRegister
        Register for correct colours and positions.
    b : QuantumRegister
        Register for maximum number of correct colours and positions of all
        permutations of secret_sequence.
    c : QuantumRegister
        Registers which compares a>b, len(c)=1.
    p : List
        Permutation of secret sequence
    keep_a : Boolean, optional
        Denotes if this stage is the last stage of the oracle.
        The default is False.

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with a mastermind stage.

    '''
    # Count correct positions in q according to p, store in a
    count_permuted(circuit, q, a, p)
    
    # Compare a > b, store in c
    compare(circuit, a, b, c)
    
    # SWAP a and b if c == 1
    for i in range(len(a)):
        circuit.cswap(c, a[i], b[i])
    
    # If keep_a is true keep a
    if keep_a:
        return circuit
    else:
        circuit.reset(a)
        circuit.reset(c)
        return circuit

def count_permuted(circuit, q, a, p):
    '''
    Counts correct positions and colours in query q according to permutation p.

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuit to perform counting on.
    q : QuantumRegister
        Query register.
    a : QuantumRegister
        Register which stores amount of correct positions and colours.
    p : Int list
        Permutation of secret string.

    Returns
    -------
    circuit : QuantumCircuit
        Quantum circuit appended with a oracle.

    '''
    # Amount of colours is the amount of qubits in q divided by the amount of 
    # positions
    amount_colour_bits = len(q)//len(p)
    
    # Write p in binary representation
    binary_list = [bin(x)[2:].zfill(amount_colour_bits) for x in p]
    
    # Apply x gates to implement permuted secret string
    binary_to_x_gates(circuit, q, binary_list)
    
    # Count the amount of correct qubits
    count(circuit, q, a, amount_colour_bits)
    
    # permute back
    binary_to_x_gates(circuit, q, binary_list)
    
    return circuit

def binary_to_x_gates(circuit, q, secret_binary):
    '''
    Places an x gate for each 0 of an element of secret_binary

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to add x gates to.
    q : QuantumRegister
        Register to add x gates to.
    secret_binary : str list
        list containing binary strings.

    Returns
    -------
    circuit : QuantumCircuit
        Circuit appended with x gates according to secret_binary.

    '''
    amount_colour_bits = len(secret_binary[0])
    
    for (i,binary) in enumerate(secret_binary):
        for (j,bit) in enumerate(binary[::-1]):
            if bit == '0':
                circuit.x(q[i*amount_colour_bits + j])
            else:
                circuit.i(q[i*amount_colour_bits + j])
    
    return circuit
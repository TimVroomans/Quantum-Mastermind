from abc import ABC
from itertools import permutations
import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from experiment.qiskit_experiment import QiskitExperiment
from experiment.util import filter_at
from .game import Game
from mastermind.arithmetic.count import k4count
from mastermind.arithmetic.comp import compare

def _construct_check_circuit(self, secret_sequence):
    '''
    Builds the quantum circuit used to obtain results from mastermind

    Parameters
    ----------
    secret_sequence : List
        Secret sequence as used in mastermind.

    Returns
    -------
    Check circuit.

    '''
    # Find all permutations of the secret sequence
    # Reverse order because we want to end with the secret sequence
    sequence_permutations = [p for p in permutations(secret_sequence)]
    sequence_permutations.reverse()    
    # Build an oracle stage for each permutation of the secret sequence
    for (i,p) in enumerate(sequence_permutations):
        # Count the number of correct query qubits according to permutation
        _count(self,p)
        
        # Compare a > b, value stord in qubit directly below b register
        compare(self.circuit, self.a[0], self.b[0], len(self.a), len(self.b))
        
        # SWAP controlled by c
        for qubit in range(len(self.a)):
            self.circuit.cswap(self.c, self.a[qubit], self.b[qubit])
                    
        # Reset a and c 
        if i+1 != len(sequence_permutations()):
            self.circuit.reset(self.a)
            self.circuit.reset(self.c)
        
        # Measure registers a and b
        self.circuit.measure(self.a, self.classical_a)
        self.circuit.measure(self.b, self.classical_b)
        
        # Return the check circuit
        return self.circuit
        
def _count(self, secret_sequence):
    '''
    Counts the amount of correct colours in the query according to
    secret_sequence

    Parameters
    ----------
    secret_sequence : List
        The secret sequence the query is to be compared against.

    Returns
    -------
    None.

    '''
    # write secret sequence as a bit string
    secret_binary = [bin(x)[2:].zfill(self.amount_colour_qubits) for x in secret_sequence]
    
    # place x-gates where secret bit string equals zero
    _secret_binary_to_x_gates(self,secret_binary)
    
    # count
    k4count(self.circuit, self.q, len(self.q), self.a, len(self.a))
            
    # place x-gates where secret bit string equals zero
    _secret_binary_to_x_gates(self,secret_binary)
    
def _secret_binary_to_x_gates(self, secret_binary):
    '''
    Places x-gates where secret_binary equals 0

    Parameters
    ----------
    secret_binary : List
        List of binary strings, each binary string corresponds to a colour
        in the secret string.

    Returns
    -------
    Quantum circuit appended with X gates according to secret_binary.

    '''
    for (pin,b) in enumerate(secret_binary):
        for (i,j) in enumerate(b):
            qubit = pin*self.amount_colour_qubits + i
            if j == '0':
                self.circuit.x(self.q[qubit])
            else:
                self.circuit.i(self.q[qubit])
    
    return self.circuit

class QuantumGame(Game, ABC):
    def __init__(self, turns=10, num_slots=4, colour_amount=6, ask_input=True):
        '''
        Initialises quantum and classical registers for the quantum version of
        mastermind

        Parameters
        ----------
        turns : integer, optional
            Amount of allowed turns. The default is 10.
        num_slots : integer, optional
            Amount of elements in the code. The default is 4.
        colour_amount : integer, optional
            Amount of colours available for the code. The default is 6.
        ask_input : boolean, optional
            Ask user for input. The default is True.

        Returns
        -------
        None.

        '''
        self.amount_colour_qubits = int(np.ceil(np.log2(colour_amount)))
        self.amount_answer_qubits = int(np.ceil(np.log2(num_slots))) + 1
        
        # Query register
        self.q = QuantumRegister(self.amount_colour_qubits * num_slots, 'q')
        
        # Answer pin registers
        self.a = QuantumRegister(self.amount_answer_qubits, 'a')
        self.b = QuantumRegister(self.amount_answer_qubits, 'b')
        self.classical_a = ClassicalRegister(self.amount_answer_qubits, 'ca')
        self.classical_b = ClassicalRegister(self.amount_answer_qubits, 'cb')
        
        # Compare qubit register
        self.c = QuantumRegister(1, 'c')
        
        # Build circuit from registers
        self.circuit = QuantumCircuit(self.q, self.a, self.b, self.c, self.classical_a, self.classical_b)
        
        # Set up qiskit experiment
        self.experiment = QiskitExperiment()
        
        # Initialise Mastermind
        super(QuantumGame, self).__init__(turns, num_slots, colour_amount, ask_input)
         
    def check_input(self, int_list, secret_sequence):
        '''
        

        Parameters
        ----------
        int_list : List of integers
            The query played.
        secret_sequence : List of integers
            The secret sequence to be compared against.

        Returns
        -------
        a : Integer
            Amount of correct pins.
        b : TYPE
            sum of a and amount of correct pins in wrong positions.

        '''
        # If the check circuit has not been made yet, make it
        if self.circuit.size() == 0:
            _construct_check_circuit(self,secret_sequence)
        
        # Run the circuit
        result = self.experiment.run(self.circuit, 1)
        result.save()
        
        return a,b
    
    def random_sequence(self):
        # Choose numbers between 0 and pin_amount (do this num_slots times)
        return np.random.randint(0, self.pin_amount, size=self.num_slots)
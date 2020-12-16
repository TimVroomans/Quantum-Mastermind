from abc import ABC
from itertools import permutations
import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from experiment.qiskit_experiment import QiskitExperiment
from experiment.util import filter_at
from .game import Game
from mastermind.arithmetic.count import count
from mastermind.arithmetic.comp import compare

def _build_mastermind_circuit(circuit, q, a, b, c, secret_sequence):
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
            _mastermind_stage(circuit, q, a, b, c, p)
            print('building stage ', i+1, ' of ', len(permutation_list), '...')
        else:
            _mastermind_stage(circuit, q, a, b, c, p, True)
            print('building last stage...')
    
    # Return the check circuit
    return circuit
    
def _mastermind_stage(circuit, q, a, b, c, p, keep_a=False):
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
    _count_permuted(circuit, q, a, p)
    
    # Compare a > b, store in c
    compare(circuit, a, b, c)
    
    # SWAP a and b if c == 1
    for i in range(len(a)):
        circuit.cswap(c, a[i], b[i])
    
    # If keep_a is true keep a
    if keep_a:
        circuit.reset(c)
        return circuit
    else:
        circuit.reset(a)
        circuit.reset(c)
        return circuit

def _count_permuted(circuit, q, a, p):
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
    _binary_to_x_gates(circuit, q, binary_list)
    
    # Count the amount of correct qubits
    count(circuit, q, a, amount_colour_bits)
    
    # permute back
    _binary_to_x_gates(circuit, q, binary_list)
    
    return circuit

def _binary_to_x_gates(circuit, q, secret_binary):
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

class QuantumGame(Game, ABC):
    def __init__(self, turns=10, num_slots=4, colour_amount=4, ask_input=True):
        # Get some relevant numbers
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
        
        
    def check_input(self, query, secret_sequence):   
        # If ther is no check circuit:
        if self.circuit.size() == 0:
            # Build check circuit
            _build_mastermind_circuit(self.circuit, self.q, self.a, self.b, self.c, self.sequence) 
            self.circuit.measure(self.a, self.classical_a)
            self.circuit.measure(self.b, self.classical_b)
        
        # Prepare q register in query
        binary_query = [bin(q)[2:].zfill(self.amount_colour_qubits) for q in query]
        prep_q = QuantumCircuit(self.q, self.a, self.b, self.c, self.classical_a, self.classical_b)
        for (i,binary) in enumerate(binary_query):
            for (j,bit) in enumerate(binary[::-1]):
                if bit == '1':
                    prep_q.x(self.q[i*self.amount_colour_qubits + j])
                else:
                    prep_q.i(self.q[i*self.amount_colour_qubits + j])
        
        
        # Finish circuit with q prepped in query
        self.circuit = prep_q + self.circuit
        
        # Run the circuit
        result = self.experiment.run(self.circuit, 1)
        counts = result.get_counts(self.circuit)
        print('Secret string: ', self.sequence)
        print('Counts: ', counts)
        
        # a = 
        # b = 
        
        # correct = a
        # semi_correct = b - a
        
        # return correct, semi_correct
    
    def random_sequence(self):
        # Choose numbers between 0 and pin_amount (do this num_slots times)
        return np.random.randint(0, self.pin_amount, size=self.num_slots)
from abc import ABC
from itertools import combinations, permutations

import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from scipy.special import binom

from experiment.qiskit_experiment import QiskitExperiment
from experiment.util import filter_at
from .game import Game
from mastermind.arithmetic.increm import increment


def _sum_filter(index, counts):
    return sum(n for _, n in filter(filter_at(index), counts.items()))


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
            Ask thu user for input. The default is True.

        Returns
        -------
        None.

        '''
        self.amount_colour_bits = int(np.ceil(np.log2(colour_amount)))
        self.amount_answer_qubits = int(np.ceil(np.log2(num_slots))) + 1
        
        # Query register
        self.q = QuantumRegister(self.amount_colour_bits * num_slots + 2, 'q')
        
        # Answer pin registers
        self.a = QuantumRegister(self.amount_answer_qubits, 'a')
        self.b = QuantumRegister(self.amount_answer_qubits, 'b')
        self.classical_a = ClassicalRegister(self.amount_answer_qubits, 'A')
        self.classical_b = ClassicalRegister(self.amount_answer_qubits, 'B')
        
        # Compare qubit register
        self.COMP = QuantumRegister(1, 'COMP')
        
        # Build circuit from registers
        self.circuit = QuantumCircuit(self.q, self.a, self.b, self.COMP, self.classical_a, self.classical_b)
        
        # Set up qiskit experiment
        self.experiment = QiskitExperiment()
        
        # Initialise Mastermind
        super(QuantumGame, self).__init__(turns, num_slots, colour_amount, ask_input)

    def check_input(self, int_list, sequence):
        if self.circuit.size() == 0:
            self._construct_check_circuit(sequence)

    def _qc_sequence_chk(self, sequence, circuit, input_mode=False):
        for (pos, num) in enumerate(sequence):
            self.qc_chk(pos, num, circuit, input_mode)

    def _construct_check_circuit(self, sequence):
        '''
        Builds the quantum circuit used to obtain results from mastermind

        Parameters
        ----------
        sequence : List
            Secret sequence as used in mastermind.

        Returns
        -------
        Check circuit.

        '''
        # Find all permutations of the secret sequence
        sequence_permutations = [p for p in permutations(sequence)]
        
        for p in sequence_permutations:
            for q in 
    

    def random_sequence(self):
        # While not part of our project, we could've used our ndie.py to roll an 'pin_amount' sided dice 'num_slots'
        # times to generate our sequence in a quantum way
        return np.random.randint(0, self.pin_amount, size=self.num_slots).tolist()


    def qc_xor(self, pin):
        for i_p in range(pin):
            for i_c in range(self.color_bits):
                self.circuit.cx(self.color_bits * pin + i_c, self.color_bits * i_p + i_c)

    def qc_inv(self, pin):
        for i_q in range(self.color_bits * pin):
            self.circuit.x(i_q)

    def qc_tst(self, pin, color, code):
        for i1 in range(code.count(color) + 1, pin + 2):
            controls_list = list(combinations(range(pin), i1 - 1))
            for i2 in controls_list:
                angle = (-1) ** (i1 + code.count(color)) * binom(i1 - 2, code.count(color) - 1) * np.pi / self.num_slots
                controls = [self.q[self.color_bits * pin + i] for i in range(self.color_bits)]
                for i_p in i2:
                    controls += [self.q[self.color_bits * i_p + i] for i in range(self.color_bits)]
                self.circuit.mcrx(angle, controls, self.q[self.color_bits * self.num_slots + 1])

    def qc_chk(self, pin, color, circuit, input_mode=False):
        for i_c in range(self.color_bits):
            condition = (color & 2 ** i_c)
            if (not condition and not input_mode) or (condition and input_mode):
                circuit.x(self.color_bits * pin + i_c)

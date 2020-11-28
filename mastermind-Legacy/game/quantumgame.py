from abc import ABC
from itertools import combinations

import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from scipy.special import binom

# Following import is actually necessary for the 'mcrx' gate.
# noinspection PyUnresolvedReferences
from qiskit.extensions.standard import multi_control_rotation_gates

from experiment.qiskit_experiment import QiskitExperiment
from experiment.util import filter_at
from .game import Game


def _sum_filter(index, counts):
    return sum(n for _, n in filter(filter_at(index), counts.items()))


class QuantumGame(Game, ABC):
    def __init__(self, turns=10, num_slots=4, pin_amount=8, ask_input=True):
        self.color_bits = int(np.ceil(np.log2(pin_amount)))

        self.q = QuantumRegister(self.color_bits * num_slots + 2)
        self.b = ClassicalRegister(self.color_bits * num_slots + 2)
        self.circuit: QuantumCircuit = QuantumCircuit(self.q, self.b)

        self.experiment = QiskitExperiment()

        super(QuantumGame, self).__init__(turns, num_slots, pin_amount, ask_input)

    def _qc_sequence_chk(self, sequence, circuit, input_mode=False):
        for (pos, num) in enumerate(sequence):
            self.qc_chk(pos, num, circuit, input_mode)

    def _construct_check_circuit(self, sequence):
        self.qc_blacks(sequence)
        self.qc_whites(sequence)

    def check_input(self, int_list, sequence):
        if self.circuit.size() == 0:
            self._construct_check_circuit(sequence)

        input_circuit = QuantumCircuit(self.q, self.b)
        self._qc_sequence_chk(int_list, input_circuit, True)

        check_circuit = input_circuit.combine(self.circuit)

        shots = 1024

        result = self.experiment.run(check_circuit, shots, optimization=0)
        blacks = (_sum_filter(1, result.get_counts()) / shots) * self.num_slots
        whites = (_sum_filter(0, result.get_counts()) / shots) * self.num_slots

        print("Probablity distribution blacks: ", blacks, " and whites:", whites)
        return int(round(blacks)), int(round(whites))

    def random_sequence(self):
        # While not part of our project, we could've used our ndie.py to roll an 'pin_amount' sided dice 'num_slots'
        # times to generate our sequence in a quantum way
        return np.random.randint(0, self.pin_amount, size=self.num_slots).tolist()

    def qc_blacks(self, code):
        for i_p in range(self.num_slots):
            # Place opening quantum circuit
            self.qc_chk(i_p, code[i_p], self.circuit)

            # Place mcrx gate
            controls = [self.q[self.color_bits * i_p + i] for i in range(self.color_bits)]
            self.circuit.mcrx(np.pi / self.num_slots, controls, self.q[self.color_bits * self.num_slots])

            # Place closing quantum circuit
            self.qc_chk(i_p, code[i_p], self.circuit)

    def qc_whites(self, code):
        for i_p in range(self.num_slots):
            # Place opening quantum circuit
            self.qc_xor(i_p)
            self.qc_inv(i_p)

            testcolors = [2 ** self.color_bits - 1] + list(set(code))
            for i_c in range(1, len(testcolors)):
                # Place x gates dependent on code
                self.qc_chk(i_p, (testcolors[i_c] ^ testcolors[i_c - 1]) ^ (2 ** self.color_bits - 1), self.circuit)

                # Place single pin mcrx gate
                if code[i_p] != testcolors[i_c]:
                    controls = [self.q[self.color_bits * i_p + i] for i in range(self.color_bits)]
                    self.circuit.mcrx(np.pi / self.num_slots, controls, self.q[self.color_bits * self.num_slots + 1])

                # Place multiple pin mcrx gates
                self.qc_tst(i_p, testcolors[i_c], code)

            # Place closing quantum circuit
            self.qc_chk(i_p, testcolors[-1], self.circuit)
            self.qc_inv(i_p)
            self.qc_xor(i_p)

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

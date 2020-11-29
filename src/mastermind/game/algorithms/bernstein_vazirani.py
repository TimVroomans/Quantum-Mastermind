from qiskit import QuantumCircuit
from experiment.qiskit_experiment import QiskitExperiment
from mastermind.game.classicalgame import ClassicalGame
from itertools import chain
import numpy as np


class BernsteinVazirani(ClassicalGame):

    def lost(self, sequence):
        print('Impossible! I cannot lose!')

    def won(self, moves_used, sequence):
        print('I won! Quantum supremacy strikes again! I used:', moves_used + 1, "moves. The sequence was ", sequence)

    def get_input(self):
        if self.moves_used == 0:
            guess = [0, 0, 1, 1]
        else:
            guess = self._bernstein()

        print("I'm guessing: ", guess)
        return guess

    def _bernstein(self):
        binary_length = int(round(np.log2(self.pin_amount)))

        # Handle secret sequence
        y = [tuple(bin(x)[2:].zfill(binary_length)) for x in self.sequence]
        y = list(chain(*y))
        y = [int(x) for x in y]

        amount_qubits = len(y)
        amount_bits = amount_qubits
        circuit = QuantumCircuit(amount_qubits + 1, amount_bits)

        circuit.h(range(amount_qubits))
        circuit.x(amount_qubits)
        circuit.h(amount_qubits)

        circuit.barrier()

        for i in range(amount_qubits):
            if y[amount_qubits - 1 - i] == 1:
                circuit.cx(i, amount_qubits)

        circuit.barrier()

        circuit.h(range(amount_qubits))
        circuit.barrier()
        circuit.measure(range(amount_qubits), range(amount_bits))

        circuit.draw(output='mpl')

        experiment = QiskitExperiment()
        results = experiment.run(circuit, 1)

        guess_bin = list(results.get_counts())[0]
        guess_bin = tuple(guess_bin)
        guess_bin = [int(x) for x in guess_bin]

        guess = np.zeros(int(len(y) / binary_length))
        for i in range(int(len(y) / binary_length)):
            binary = guess_bin[i * binary_length:i * binary_length + binary_length]
            num = binary[0] * 2 ** 2 + binary[1] * 2 ** 1 + binary[2] * 2 ** 0
            guess[i] = num

        return guess.astype(int).tolist()

    def give_feedback(self, correct, semi_correct):
        # I don't need feedback ;)
        pass


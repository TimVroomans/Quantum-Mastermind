from abc import ABC
import numpy as np

from experiment.qiskit_experiment import QiskitExperiment
from .game import Game

class QuantumSolverGame(Game, ABC):
    def __init__(self, turns=10, num_slots=4, colour_amount=4, ask_input=True):
        # Set up qiskit experiment
        self.experiment = QiskitExperiment()
        
        # Initialise Mastermind
        super(QuantumSolverGame, self).__init__(turns, num_slots, colour_amount, ask_input)
        
        
    def check_input(self, query, secret_sequence):   
        pass
    
    def random_sequence(self):
        # Choose numbers between 0 and pin_amount (do this num_slots times)
        return np.random.randint(0, self.pin_amount, size=self.num_slots)
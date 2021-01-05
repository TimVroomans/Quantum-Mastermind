# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 17:38:52 2021

@author: timvr
"""
import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from abc import ABC
from mastermind.game.algorithms.Find_Colours import build_find_colours_circuit
from mastermind.game.game import Game

class Buhrman(Game, ABC):
    def __init__(self, num_slots=4, num_colours=4):
        n = num_slots
        k = num_colours
        logn = int(np.ceil(np.log2(n)))
        logk = int(np.ceil(np.log2(k)))
        # Quantum Registers
        self.b0 = QuantumRegister(logk+1,'b0')
        self.x = QuantumRegister(k, 'x')
        self.q = QuantumRegister(n*logk, 'q')
        self.b = QuantumRegister(logk+1,'b')
        self.c = QuantumRegister(logn+1,'c')
        self.d = QuantumRegister(1,'d')
        self.e = QuantumRegister(1,'e')
        self.f = QuantumRegister(1,'f')
        # Classical register
        self.classical_x = ClassicalRegister(num_colours,'cx')
        
        # Circuit
        self.circuit = QuantumCircuit(self.b0,self.x,self.q,self.b,self.c,self.d,self.e,self.f,self.classical_x)
        
        # Initialise Quantum Game
        super(Buhrman, self).__init__(10, num_slots, num_colours, False)
        
        self.Algorithm()
        
    def Algorithm(self):
        # If ther is no check circuit:
        if self.circuit.size() == 0:
            # Build check circuit
            build_find_colours_circuit(self.circuit, self.b0, self.x, self.q, self.b, self.c, self.d, self.e, self.f, self.sequence)
            # Measure register x
            self.circuit.measure(self.x, self.classical_x)
        
        # Run the circuit
        result = self.experiment.run(self.circuit, 1)
        counts = result.get_counts(self.circuit)
        x = list(counts.keys())[0] 
        print(x)
        return x
    
    def give_feedback(self, correct, semi_correct):
        pass
    
    def random_sequence(self):
        # Choose numbers between 0 and pin_amount (do this num_slots times)
        
        arr = np.array([1, 1, 2, 2])
        print("\n\nWATCH OUT: RUNNING WITH HARDCODED STRING %s !!!\n\n" % (arr))
        return arr
        #return np.random.randint(0, self.pin_amount, size=self.num_slots)
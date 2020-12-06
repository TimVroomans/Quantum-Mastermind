from abc import ABC

import numpy as np

from .game import Game


def _check_input(code_list, sequence):
    '''
    Checks the given code against the secret sequence and returns the black
    and white pins according to the rules of Mastermind.
    
    Parameters
    ----------
    code_list : LIST.
    sequence : LIST.

    Returns
    -------
    correct : LIST.
    semi_correct : LIST.

    '''
    
    blacks = set()
    whites = set()

    correct = 0
    semi_correct = 0
    for (pos, num) in enumerate(code_list):
        if sequence[pos] == num:
            blacks.add(pos)
            correct += 1
    for (i, num1) in enumerate(code_list):
        if i not in blacks:
            for (j, num2) in enumerate(sequence):
                if j not in blacks and j not in whites and i != j and num1 == num2:
                    whites.add(j)
                    semi_correct += 1
                    break

    return correct, semi_correct


class ClassicalGame(Game, ABC):

    def check_input(self, int_list, sequence):
        return _check_input(int_list, sequence)

    def random_sequence(self):
        # Choose numbers between 0 and pin_amount (do this num_slots times)
        return np.random.randint(0, self.pin_amount, size=self.num_slots)

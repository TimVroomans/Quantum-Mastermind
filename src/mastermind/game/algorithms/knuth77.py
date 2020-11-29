from abc import ABC
from functools import partial
from itertools import product

import numpy as np

from mastermind.game.classicalgame import _check_input
from mastermind.game.game import Game


def _score_code(code, max_num, pegs, guesses):
    """
    :param code: current code to compare
    :param max_num: A large number
    :param pegs: list of possible black/white combinations for pegs
    :param guesses:  guesses left
    """
    eliminate_min = max_num
    for p in pegs:
        eliminate = 0
        for guess in guesses:
            if p != _check_input(list(code), list(guess)):
                eliminate += 1
        eliminate_min = min(eliminate, eliminate_min)
    return eliminate_min


def _generate_pegs(num_slots):
    n = num_slots + 1
    return [(i, j - i) for i in range(n) for j in range(n) if j - i >= 0 and not (i == n - 2 and j - i > 0)]


class Knuth(Game, ABC):
    _Codes: list = None
    _Guesses: list = None
    _Score = list()
    _Move = list()

    # List of all possible outcomes.
    _Pegs = None

    def get_input(self):
        if self.game_end:
            return
        if self._Pegs is None:
            self._Pegs = _generate_pegs(self.num_slots)
        if self.moves_used == 0:
            # Initialise a list with all possible codes and the list with remaining possible secret codes
            self._Codes = list(product(range(0, self.pin_amount), repeat=self.num_slots))
            self._Guesses = self._Codes.copy()

            # First move is always 0011
            move = (0, 0, 1, 1)
        else:
            # Generate the scores via minmax method
            self._min_max()

            # Select the moves with the highest scores
            indices = np.where(self._Score == np.max(self._Score))[0]
            possible_moves = [self._Codes[i] for i in indices]

            # Select a possible key whenever possible
            move = possible_moves[0]
            for m in possible_moves:
                if m in self._Guesses:
                    move = m
                    break

        print('Move ', self.moves_used + 1, ': ', move)

        # Remove selected move from possible codes
        self._Codes.remove(move)

        self._Move = move
        return list(move)

    def give_feedback(self, correct, semi_correct):
        print("Received feedback: ", correct, "blacks and", semi_correct, "whites")

        # Remove from the remaining possible codes, those codes who do not give the same response if the previous move
        # would be the code
        self._Guesses = [el for el in self._Guesses if (correct, semi_correct) == _check_input(el, self._Move)]

    def _min_max(self):
        """
        Minmax technique: the score for the next guess will be the minimum amount of codes it can eliminate if that
        code is played and the peg score is returned
        """

        # Construct a 'maximum' size Threadpool
        #pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)

        # Populate the score list via multithreading. For each code execute the _score_code(...) method.
        # the partial() method here is used for the multithreading.
        self._Score = _score_code(self._Codes, len(self._Codes), self._Pegs, self._Guesses)

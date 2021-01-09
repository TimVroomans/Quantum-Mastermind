from abc import ABC
from itertools import product

import numpy as np

from mastermind.game.classicalgame import _check_input
from mastermind.game.game import Game


def _score_code(code, max_num, pegs, guesses):
    '''
    Returns the minimum amount of remaining guesses a code can eliminate.

    Parameters
    ----------
    code : List
        code to score.
    max_num : Int
        Largest possible number.
    pegs : List
        Different combinations of answer pegs.
    guesses : List
        Remaining possible guesses.

    Returns
    -------
    eliminate_min : Int
        Amount of guesses this score can eliminate.

    '''
    eliminate_min = max_num
    for p in pegs:
        eliminate = 0
        for guess in guesses:
            if p != _check_input(list(code), list(guess)):
                eliminate += 1
        eliminate_min = min(eliminate, eliminate_min)
    return eliminate_min


def _generate_pegs(num_slots):
    '''
    Generates the different combinations of answer pegs from the length of the
    query.

    Parameters
    ----------
    num_slots : length of the query.

    Returns
    -------
    pegs : different combinations of answer pegs.

    '''
    n = num_slots + 1
    pegs = [(i, j - i) for i in range(n) for j in range(n) if j - i >= 0 and not (i == n - 2 and j - i > 0)]
    return pegs

def _min_max(self):
    '''
    Assigns a score to each remaining code according to the minimum amount
    of remaining guesses it can eliminate.

    Returns
    -------
    none.

    '''
    C = len(self._Codes)
    self._Score = [0]*C
    for (i,code) in enumerate(self._Codes):
        self._Score[i] = _score_code(code, C, self._Pegs, self._Guesses)


class Knuth(Game, ABC):
    '''
    Generalised implementation of Knuth's 5-guess algorithm to solve MM(n,k).
    The 5 guesses only apply to MM(4,6).
    '''
    _Codes: list = None
    _Guesses: list = None
    _Score = list()
    _Move = list()

    # List of all possible outcomes.
    _Pegs = None

    def get_input(self):
        '''
        Handels input for mastermind via the Knuth algorithm.

        Returns
        -------
        END GAME
        
        move: Next move to be played.

        '''
        'If game has ended, end the game.'
        if self.game_end:
            return
        
        'If not done yet, generate all possible combinations of answer pegs'
        if self._Pegs is None:
            self._Pegs = _generate_pegs(self.num_slots)

        '''
        First move and generate list of remaining codes and guesses, after
        that perform the minmaxing loop.
        '''
        if self.moves_used == 0:
            # Initialise a list with all possible codes and the list with remaining possible secret codes
            self._Codes = list(product(range(0, self.pin_amount), repeat=self.num_slots))
            self._Guesses = self._Codes.copy()

            # First move is always 0011
            move = (0, 0, 1, 1)
        else:
            # Generate the scores via minmax method
            _min_max(self)

            # Select the moves with the highest scores
            move_indices = np.where(self._Score == np.max(self._Score))[0]
            possible_moves = [self._Codes[i] for i in move_indices]

            # Select a remaining possible key whenever possible
            move = possible_moves[0]
            for m in possible_moves:
                if m in self._Guesses:
                    move = m
                    break
        
        # Print move for user's satisfaction
        print('Move ', self.moves_used + 1, ': ', move)

        # Remove selected move from possible codes and play said move
        self._Codes.remove(move)
        self._Move = move
        return list(move)

    def give_feedback(self, correct, semi_correct):
        print("Received feedback: ", correct, "blacks and", semi_correct, "whites")

        # Remove from the remaining possible codes, those codes who do not give the same response if the previous move
        # would be the code
        self._Guesses = [guess for guess in self._Guesses if (correct, semi_correct) == _check_input(guess, self._Move)]

    

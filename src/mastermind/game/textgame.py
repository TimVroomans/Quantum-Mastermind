from abc import ABC

from mastermind.game.algorithms.knuth77 import Knuth
from mastermind.game.algorithms.Buhrman import Buhrman
from mastermind.game.quantumgame import QuantumGame
from mastermind.game.classicalgame import ClassicalGame
from mastermind.game.quantumsolver import QuantumSolverGame
from mastermind.game.game import Game


def handle_input(input_string):
    pins = [int(num_string) for num_string in input_string.split(" ")]

    return pins


class TextGame(Game, ABC):

    def lost(self, sequence):
        print("You lost! The sequence was:", sequence)

    def won(self, moves_used, sequence):
        print("You won in", moves_used + 1, "moves! The sequence was indeed:", sequence)

    def get_input(self):
        print("Fill in a sequence of", self.num_slots, "numbers between 0 and", self.pin_amount - 1,
              "separated by spaces")
        while True:
            try:
                input_string = input()

                pins = handle_input(input_string)
                if len(pins) != self.num_slots:
                    raise ValueError
                return pins
            except ValueError:
                print("Please input a correct sequence like so: \"0 2 2 7\"")

    def give_feedback(self, correct, semi_correct):
        print(correct, "pins are in the correct position", semi_correct, "pins are correct but in the wrong position")


class TextClassical(TextGame, ClassicalGame):
    pass


class TextQuantum(TextGame, QuantumGame):
    pass


class TextKnuth(Knuth, TextGame, ClassicalGame):
    pass


class TextQnuth(Knuth, TextGame, QuantumGame):
    pass

class TextBuhrman(Buhrman, TextGame, QuantumSolverGame):
    pass

import tkinter as tk
from abc import ABC

from mastermind.game.classicalgame import ClassicalGame
from mastermind.game.quantumgame import QuantumGame

__author__ = "Maarten Lips"
__email__ = "m.p.h.lips@student.tudelft.nl"

from mastermind.game.game import Game

from mastermind.game.algorithms.knuth77 import Knuth
from mastermind.game.visual.enums.mode import Mode
from mastermind.game.visual.widgets import MainWindow, InfoBar, FeedbackWindow


class GameView(tk.Frame):
    _WINDOW_TITLE = "Mastermind"

    def __init__(self, parent: tk.Tk, **kwargs):
        super(GameView, self).__init__(parent, kwargs)
        parent.title(self._WINDOW_TITLE)

        self.classic_game = VisualClassic(self)
        self.knuth_game = ClassicVisualKnuth(self)
        self.quantum_game = VisualQuantum(self)
        self.qnuth_game = VisualQnuth(self)
        self.bv_game = VisualBV(self)

        self.main_window = MainWindow(self, self.classic_game, self.do_input)
        self.info_bar = InfoBar(self)
        self.feedback_windows = [FeedbackWindow(self.main_window) for _ in Mode.Classic.__class__]

        self.init_widgets()

        self.grid(row=0, column=0, rowspan=2, sticky="nsew")
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        self.focus_set()
        self.bind('<Return>', lambda event: self.main_window.input_window.submit())
        self.bind('m', self.info_bar.switch)
        super(GameView, self).__init__()

        self.last_input = None

    def do_input(self, int_list):
        mode = self.info_bar.mode

        if mode == Mode.Classic:
            self.last_input = int_list
            self.classic_game.do_input(int_list)
        elif mode == Mode.Knuth:
            int_list = self.knuth_game.get_input()
            self.last_input = int_list
            self.knuth_game.do_input(int_list)
        elif mode == Mode.Quantum:
            self.last_input = int_list
            self.quantum_game.do_input(int_list)
        elif mode == Mode.Qnuth:
            int_list = self.qnuth_game.get_input()
            self.last_input = int_list
            self.qnuth_game.do_input(int_list)
        elif mode == Mode.BernsteinVazirani:
            int_list = self.bv_game.get_input()
            self.last_input = int_list
            self.bv_game.do_input(int_list)

    def switch_mode(self, mode: Mode):
        mode = self.info_bar.mode
        if mode == Mode.Classic:
            game = self.classic_game
        elif mode == Mode.Knuth:
            game = self.knuth_game
        elif mode == Mode.Quantum:
            game = self.quantum_game
        elif mode == Mode.Qnuth:
            game = self.qnuth_game
        else:
            game = self.bv_game

        game.visualize_moves()
        feedback_window = self.feedback_windows[mode]
        self.main_window.feedback_window.grid_remove()
        self.main_window.feedback_window = feedback_window
        self.main_window.setup()

    def init_widgets(self):
        """
        Initialize the widgets
        """

        self.switch_mode(Mode.Classic)
        self.main_window.setup()
        self.info_bar.setup()


class VisualGame(Game, ABC):

    def __init__(self, game_view: GameView, ask_input=False):
        super(VisualGame, self).__init__(ask_input=ask_input)
        self.gameview = game_view

    def lost(self, sequence):
        self.gameview.main_window.give_feedback(sequence, "Answer", "")
        title = self.gameview.info_bar.title_label
        title.config(text="You lost!")
        title.grid(row=0, column=0, sticky='w')

    def won(self, moves_used, sequence):
        self.visualize_feedback(4, 0)
        title = self.gameview.info_bar.title_label
        title.config(text="You won!")
        title.grid(row=0, column=0, sticky='w')

    def give_feedback(self, correct, semi_correct):
        self.visualize_feedback(correct, semi_correct)

    def visualize_moves(self):
        title = self.gameview.info_bar.title_label
        title.config(text="Moves used: " + str(self.moves_used) + "/" + str(self.turns))
        title.grid(row=0, column=0, sticky='w')

    def visualize_feedback(self, correct, semi_correct):
        self.visualize_moves()
        self.gameview.main_window.give_feedback(self.gameview.last_input, correct, semi_correct)


class VisualClassic(VisualGame, ClassicalGame):
    def get_input(self):
        pass


class VisualKnuth(Knuth, VisualGame, ABC):
    def __init__(self, game_view: GameView):
        super(VisualKnuth, self).__init__(game_view, ask_input=False)

    def give_feedback(self, correct, semi_correct):
        super(VisualKnuth, self).give_feedback(correct, semi_correct)
        self.visualize_feedback(correct, semi_correct)


class ClassicVisualKnuth(ClassicalGame, VisualKnuth):
    pass


class VisualQnuth(VisualKnuth, QuantumGame):
    pass


class VisualQuantum(VisualGame, QuantumGame):
    def get_input(self):
        pass
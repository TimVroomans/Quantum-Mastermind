import tkinter as tk
from collections import Callable

from mastermind.game.game import Game
from mastermind.game.visual.enums.abstract_intenum import AbstractIntEnum
from mastermind.game.visual.enums.color import Color
from mastermind.game.visual.enums.input_type import InputType
from mastermind.game.visual.enums.mode import Mode


def switch(enum: AbstractIntEnum, button: tk.Button):
    enum = enum.get_next()
    button.config(text=enum.name)
    return enum


def switch_with_event(enum: AbstractIntEnum, button: tk.Button, event):
    if event.num == 1:
        enum = enum.get_next()
    elif event.num == 3:
        enum = enum.get_previous()
    else:
        enum = enum.get_next()
    button.config(text=enum.name)
    return enum


class Input:
    def __init__(self, parent: tk.Frame, num_slots):
        self.value = tk.IntVar()
        self.value.set(1)

        self.input_frame = tk.Frame(parent)

        self.entry = tk.Entry(self.input_frame)

        self.entry.bind('<Return>', lambda event: parent.submit())
        self.show_button_text = False
        self.input_buttons = []
        for i in range(num_slots):
            button = tk.Button(self.input_frame, width='3')
            self._config_button(button, Color.RED)
            button.bind('<Button-1>', self._switch_color(button))
            button.bind('<Button-3>', self._switch_color(button))
            self.input_buttons.append(button)

    def _config_button(self, input_button: tk.Button, color: Color):
        c_value = color.get_color_value()
        c_text = c_value
        if self.show_button_text:
            c_text = color.get_text_color()

        input_button.config(text=str(color.value), bg=c_value, fg=c_text,
                            activebackground=c_value, activeforeground=c_text)

    @staticmethod
    def _get_num_input(input_button: tk.Button):
        return int(input_button.cget('text'))

    def _next_color(self, input_button):
        def func():
            color = Color(self._get_num_input(input_button)).get_next()
            self._config_button(input_button, color)

        return func

    def _switch_color(self, input_button):
        def func(event):
            color = None
            if event.num == 1:
                color = Color(int(input_button.cget('text'))).get_next()
            elif event.num == 3:
                color = Color(int(input_button.cget('text'))).get_previous()
            self._config_button(input_button, color)

        return func

    def get_input(self):
        return [self._get_num_input(button) for button in self.input_buttons]

    def show_input(self, input_type: InputType):
        self.entry.grid_remove()
        for button in self.input_buttons:
            button.grid_remove()
        if input_type == input_type.Numbers:
            self.entry.grid(row=0, column=0, columnspan=4)
        elif input_type == input_type.Colors:
            self.show_button_text = False
            for (pos, button) in enumerate(self.input_buttons):
                button.grid(row=0, column=pos)
                self._config_button(button, Color(self._get_num_input(button)))
        elif input_type == input_type.Combo:
            self.show_button_text = True
            for (pos, button) in enumerate(self.input_buttons):
                button.grid(row=0, column=pos)
                self._config_button(button, Color(self._get_num_input(button)))


class InputWindow(tk.Frame):
    def __init__(self, parent: tk.Frame, num_slots, pin_amount, submit_input: Callable):
        super(InputWindow, self).__init__(parent)

        self.num_slots = num_slots
        self.pin_amount = pin_amount

        self.input_type = InputType.Colors
        self.submit_input = submit_input
        self.inputs = []
        self.add_input()
        self.change_input_button = tk.Button(self, text=self.input_type.name)
        self.change_input_button.bind('<Button-1>', self.switch)
        self.change_input_button.bind('<Button-3>', self.switch)
        self.submit_button = tk.Button(self, text="Submit", command=self.submit)

    def switch(self, event):
        self.input_type = switch_with_event(self.input_type, self.change_input_button, event)
        self.setup()

    def setup(self):
        """
        Packs the widget inside the frame
        """
        self.change_input_button.grid(row=0, column=0, sticky='w')
        self.submit_button.grid(row=0, column=1, sticky='e')

        for (i, inp) in enumerate(self.inputs):
            self.setup_input(inp, i + 1)

        self.grid(row=0, column=0, sticky='nw')

    def setup_input(self, inp: Input, index):
        inp.input_frame.grid(row=index + 1, column=0, columnspan=2, sticky='nw')
        inp.show_input(self.input_type)

    def add_input(self):
        inp = Input(self, self.num_slots)

        self.inputs += [inp]
        self.setup_input(inp, len(self.inputs))

    def submit(self):
        if len(self.inputs) > 0:
            if self.input_type == InputType.Numbers:
                pins = [int(num_string) for num_string in self.inputs[0].entry.get().split(" ")]
            else:
                pins = self.inputs[0].get_input()

            self.submit_input(pins)


class FeedbackWindow(tk.Canvas):

    def __init__(self, parent: tk.Frame, moves=10, *args, **kwargs):
        super(FeedbackWindow, self).__init__(parent, *args, **kwargs)
        self.feedback_amount = 0
        self.max_feedback = moves
        self.config(bg='black')

    def add_feedback(self, int_list, correct, semi_correct):
        size = self.winfo_height() / self.max_feedback - 1
        width = self.winfo_width()
        y1 = self.feedback_amount * size
        y2 = y1 + size

        self.create_rectangle((0, y1, width, y2), fill='grey')
        for (i, num) in enumerate(int_list):
            posx = i * size + 5
            color = Color(num)
            self.create_rectangle((posx, y1, posx + size, y2), fill=color.get_color_value())
            self.create_text((posx + size / 2, y1 + size / 2), fill=color.get_text_color(), text=str(num))
        self.create_text((width - 50, y1 + size / 2), fill='black', text=str(correct))
        self.create_text((width - 30, y1 + size / 2), fill='white', text=str(semi_correct))

        self.feedback_amount += 1


class MainWindow(tk.Frame):
    def __init__(self, parent: tk.Frame, game: Game, submit_input: Callable):
        super(MainWindow, self).__init__(parent)

        self.game = game

        self.input_window = InputWindow(self, game.num_slots, game.pin_amount, submit_input)
        self.feedback_window = FeedbackWindow(self)

    def setup(self):
        """
        Packs the widget inside the frame
        """
        self.input_window.setup()
        self.feedback_window.grid(row=0, column=2, columnspan=2, sticky='nsw')

        self.grid(row=0, column=0, sticky='nsew')

    def give_feedback(self, int_list, correct, semi_correct):
        self.feedback_window.add_feedback(int_list, correct, semi_correct)


class InfoBar(tk.Frame):
    def __init__(self, parent: tk.Frame):
        super(InfoBar, self).__init__(parent)
        self.title_label = tk.Label(self, text="Game Status")

        self.gameview = parent
        self.mode = Mode.Classic
        self.mode_button = tk.Button(self, text=self.mode.name)
        self.mode_button.bind('<Button-1>', self.switch)
        self.mode_button.bind('<Button-3>', self.switch)
        self.label = tk.Label(self, text="You lost!")

    def switch(self, event):
        self.mode = switch_with_event(self.mode, self.mode_button, event)
        self.gameview.switch_mode(self.mode)

    def setup(self):
        """
        Packs the widget inside the frame
        """
        self.mode_button.grid(row=0, column=1, columnspan=1, sticky="e")

        self.grid(row=1, column=0, sticky='ew')

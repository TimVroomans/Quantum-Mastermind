import tkinter as tk

from mastermind.game.textgame import TextClassical, TextKnuth, TextBuhrman, TextQnuth, TextQuantum
from mastermind.game.visual.visual_mastermind import GameView

def _choose_game():
    print("\n\nChoose what type of game you want:")
    print("1. Classical")
    print("2. Quantum")
    print("3. Knuth (Classical Algorithm)")
    print("4. Qnuth (Knuth vs Quantum)")
    print("5. Buhrman (Quantum Algorithm)")

    while True:
        try:
            game_type = int(input())
            if game_type == 1:
                TextClassical()
            elif game_type == 2:
                TextQuantum()
            elif game_type == 3:
                TextKnuth()
            elif game_type == 4:
                TextQnuth()
            elif game_type == 5:
                TextBuhrman()
            else:
                raise ValueError
            break
        except ValueError:
            print("Please fill in a number between 1 and 5")


def _choose_interface():
    print("\n\nChoose what type of interface you want:")
    print("1. Textual")
    print("2. Visual")
    while True:
        try:
            interface = int(input())
            if interface == 1:
                _choose_game()
            elif interface == 2:
                master = tk.Tk()
                GameView(master)
                master.mainloop()
            else:
                raise ValueError
            break
        except ValueError:
            print("Please fill in either '1' or '2'")


if __name__ == '__main__':
    _choose_interface()

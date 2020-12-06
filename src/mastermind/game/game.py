from abc import abstractmethod, ABC


class Game(ABC):

    def __init__(self, turns=10, num_slots=4, pin_amount=6, ask_input=True):
        self.turns = turns
        self.num_slots = num_slots
        self.pin_amount = pin_amount
        sequence = self.random_sequence()

        self.sequence = sequence
        self.total_moves = turns
        self.moves_used = 0
        self.game_end = False

        if ask_input:
            self._loop(sequence)

    def _loop(self, sequence):
        for i in range(self.turns):
            if self.do_move(sequence):
                self.total_moves = i
                break
            self.moves_used += 1
        if self.total_moves == self.turns:
            self.lost(sequence)
            self.game_end = True
        else:
            self.won(self.total_moves, sequence)
            self.game_end = True

    def do_input(self, int_list):
        if self.game_end:
            return

        self.moves_used += 1

        result = (correct, semi_correct) = self.check_input(int_list, self.sequence)
        if result == (self.num_slots, 0):
            self.won(self.moves_used, self.sequence)
            self.game_end = True
            return
        if self.moves_used == self.turns:
            self.lost(self.sequence)
            self.game_end = True
            return

        self.give_feedback(correct, semi_correct)

    def do_move(self, sequence):
        pins = self.get_input()
        result = (correct, semi_correct) = self.check_input(pins, sequence)
        self.give_feedback(correct, semi_correct)

        return result == (self.num_slots, 0)

    @abstractmethod
    def lost(self, sequence):
        pass

    @abstractmethod
    def won(self, moves_used, sequence):
        pass

    @abstractmethod
    def get_input(self):
        pass

    @abstractmethod
    def give_feedback(self, correct, semi_correct):
        pass

    @abstractmethod
    def check_input(self, int_list, sequence):
        pass

    @abstractmethod
    def random_sequence(self):
        pass

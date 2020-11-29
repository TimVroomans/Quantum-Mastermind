from .abstract_intenum import AbstractIntEnum


class Color(AbstractIntEnum):
    RED = 0
    BROWN = 1
    ORANGE = 2
    YELLOW = 3
    GREEN = 4
    CYAN = 5
    NAVY = 6
    MAGENTA = 7

    def get_color_value(self):
        values = ["#e6194B", "#9A6324", "#f58231", "#ffe119", "#3cb44b", "#42d4f4", "#000075", "#f032e6"]
        return values[self.value]

    def get_text_color(self) -> str:
        if self == Color.NAVY:
            return "white"
        return "black"

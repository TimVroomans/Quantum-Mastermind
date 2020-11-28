from enum import IntEnum


class AbstractIntEnum(IntEnum):

    def get_next(self):
        return self._get(self.value + 1)

    def get_previous(self):
        return self._get(self.value - 1)

    def _get(self, index):
        _list = self._list()
        return self.__new__(_list[index % len(_list)])

    def _list(self):
        return [enum.value for enum in self.__class__]

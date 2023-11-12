from MemoryDirection import MemoryDirection
from MemoryUnit import MemoryUnit
from typing import AnyStr, List


class RAM:

    memory_variables: List[MemoryUnit]
    next_memory_space: int

    def RAM(self):
        self.memory_variables = []
        self.next_memory_space = 0

    def reset(self):
        self.memory_variables = []
        self.next_memory_space = 0

    def get_memory_unit(self, space: int):
        pass

    def save_on_next_free(self):
        pass


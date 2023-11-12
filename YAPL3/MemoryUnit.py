from MemoryDirection import MemoryDirection
from typing import AnyStr


class MemoryUnit:
    direction: MemoryDirection
    space: AnyStr  # Class

    def __init__(self, direction, space):
        self.direction = direction
        self.space = space

    def __str__(self):
        return f"{self.direction}_{self.space}"


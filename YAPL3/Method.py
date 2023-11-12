from typing import AnyStr, List
from MemoryUnit import  MemoryUnit


class Method:
    name: AnyStr
    tdc_code: List
    content: List

    def __init__(self, name):
        self.name = name
        self.tdc_code = []

    def add_tdc_line(self, line):
        self.tdc_code.append(line)

    def set_content(self, content):
        self.content = content

    def get_instance(self, memory_unit: MemoryUnit):

        res = f"{memory_unit}_{self.name}:"
        line_prefix = "\n\t"
        for line in self.content:
            res += f"{line_prefix}{line}"
        return res

    def get_example(self):
        res = f"\n{self.name}:"
        line_prefix = "\n\t"
        for line in self.content:
            res += f"{line_prefix}{line}"
        return res


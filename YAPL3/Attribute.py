from typing import AnyStr, List
from MemoryUnit import MemoryUnit
import MIPS_CONSTANTS as MC


class Attribute:
    name: AnyStr
    attr_type: AnyStr
    additional_code: List
    value: AnyStr | None

    def __init__(self, name):
        self.name = name

    def get_value(self):
        if self.value is None:
            if self.attr_type in MC.defaults_values:
                return MC.defaults_values.get(self.attr_type)
            else:
                return None
        return self.value

    def get_instance(self, memory_unit: MemoryUnit):
        return f"{memory_unit}_{self.name}: {MC.type_of_data_on_mips.get(self.attr_type)} {self.get_value()}"

    def get_example(self):
        return f"{self.name}: {MC.type_of_data_on_mips.get(self.attr_type)} {self.get_value()}"

    def set_additional_code(self, additional_code):
        self.additional_code = additional_code

    def set_value(self, value):
        self.value = value

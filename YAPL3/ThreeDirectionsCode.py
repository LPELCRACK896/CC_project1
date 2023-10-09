from collections import namedtuple
from typing import List, Dict, Tuple, AnyStr
from Symbol import Symbol
from Scope import Scope
import os


class Operation:
    type_of_operation: str
    translation_operation_to_str: Dict[AnyStr, AnyStr]

    def __init__(self, type_of_operation):
        self.type_of_operation = type_of_operation
        self.translation_operation_to_str = \
            {
                "if": "if",
                "assign": "="
            }

    def __str__(self):
        if self.type_of_operation in self.translation_operation_to_str:
            return f"{self.translation_operation_to_str[self.type_of_operation]}"

        return f"{self.type_of_operation}"

class Direction:

    content: AnyStr | Symbol
    scopes: Dict[AnyStr, Scope]

    def __init__(self, content: AnyStr | Symbol, scopes: Dict[AnyStr, Scope]):
        self.content = content
        self.scopes = scopes

    def update_real_tag(self, real_tag: str):
        self.content = real_tag

    def replace_tag(self, new_tag: AnyStr):
        self.content = new_tag

    def is_reference(self):
        return isinstance(self.content, Symbol)

    def is_temporary_variable(self):
        return not self.is_reference()


class Register:
    tag: AnyStr
    first_direction: Direction | None
    second_direction: Direction | None
    third_direction: Direction  | None

    temporary_tag_count: int

    first_operation: Operation
    second_operation: Operation

    temporary_tag_equivalences: Dict[AnyStr, AnyStr]  # Type of waiting instruction: Temporary

    def __init__(self, first_direction, second_direction, third_direction, first_operation_alias: AnyStr, second_operation_alias: AnyStr):
        self.first_direction = first_direction
        self.second_direction = second_direction
        self.third_direction = third_direction

        self.first_operation = Operation(first_operation_alias)
        self.second_operation = Operation(second_operation_alias)

        self.temporary_tag_equivalences = {}
        self.temporary_tag_count = 1

    def __str__(self):
        if self.first_direction and self.second_direction and self.third_direction:
            return f"{self.first_direction} {self.first_operation}" \
                   f" {self.second_direction} {self.second_operation} {self.third_direction}"

        elif self.first_direction and self.second_direction:
            return f"{self.first_direction} {self.first_operation} {self.second_direction}"

        # Is possible any other variant???

    def create_temporary_tag(self, waiting_tag_reference):
        temporary_tag = f"TT{self.temporary_tag_count}"
        self.temporary_tag_equivalences[waiting_tag_reference] = temporary_tag
        self.temporary_tag_count += 1

    def listen_outside_tag(self, tag_reference: str, real_tag: str):
        if tag_reference in self.temporary_tag_equivalences:
            self.try_to_update_directions_tags(tag_reference, real_tag)
            self.temporary_tag_equivalences.pop(tag_reference)

    def try_to_update_directions_tags(self, tag_reference: str, real_tag: str):
        self.try_to_update_direction(self.first_direction, tag_reference, real_tag)
        self.try_to_update_direction(self.second_direction, tag_reference, real_tag)
        self.try_to_update_direction(self.third_direction, tag_reference, real_tag)

    @staticmethod
    def try_to_update_direction(direction: Direction, tag_reference: str, real_tag: str):
        if direction.content == tag_reference:
            direction.update_real_tag(real_tag)


class ThreeDirectionsCode:

    temp_counter: int
    label_counter: int
    code: List[Register]
    references: List[Tuple]

    scopes: Dict[AnyStr, Scope]

    def __init__(self, scopes: Dict[AnyStr, Scope]):

        self.scopes = scopes

        self.temp_var_count = 1
        self.label_counter = 1
        self.code = []

    def __str__(self):
        string_code = ""

        for register in self.code:
            string_code += f"{register}\n"

        return string_code

    def write_file(self, filename: AnyStr = "three_directions_code.txt"):
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"

        with open(input_file, 'w') as file:
            file.write(str(self))

    def add_register(self, register: Register):
        self.code.append(register)

    def relate_register_and_reference(self, reference: str, register: Register):
        pass

    def relate_register_and_item_from_registers(self, index=-1):
        pass

    def get_register(self, index):
        index = self.__normalize_index(index)
        if index < len(self.code):
            return None

        return self.code[index]

    def pop_register(self, index=0) -> Register | None:
        index = self.__normalize_index(index)
        if index >= len(self.code):
            return None

        return self.code.pop(index)

    def peek_register(self) -> Register:
        if self.code:
            return self.code[-1]

    def size(self):
        return len(self.code)

    def __normalize_index(self, index):
        if index < 0:
            new_index = self.size() - 1
            if new_index >= 0:
                return new_index  # Is equivalent index
            return self.size()  # Gives index to overflow
        return index  # No need normalization

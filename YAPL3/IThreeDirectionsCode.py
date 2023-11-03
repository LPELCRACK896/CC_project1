from typing import Dict, AnyStr, List, Tuple
from abc import ABC, abstractmethod
from Register import Register
from Symbol import Symbol
from Scope import Scope


class IThreeDirectionsCode:
    temp_counter: int
    label_counter: int
    code: List[Register]
    references: List[Tuple]

    scopes: Dict[AnyStr, Scope]
    content: Dict[AnyStr, Dict[AnyStr, Symbol]]
    sequential_symbols: List[Symbol]

    label_class_counter: int
    label_method_counter: int

    conditional_waiting_list: List[Symbol]
    waiting_list_subscriptions: Dict[AnyStr, List[Register]]

    while_start_labels = Dict[AnyStr, AnyStr]

    def __init__(self, scopes: Dict[AnyStr, Scope], content, sequential_symbols: List[Symbol]):

        self.scopes = scopes
        self.content = content
        self.sequential_symbols = sequential_symbols

        self.temp_var_count = 0

        self.label_counter = 0

        self.label_class_counter = 0
        self.label_method_counter = 0

        self.code = []

        self.conditional_waiting_list = []
        self.waiting_list_subscriptions = {}

        self.while_start_labels = {}

    def __str__(self):
        string_code = ""

        for register in self.code:
            string_code += f"{register}\n"

        return string_code

    def add_while_label(self, while_name: AnyStr, label_value: AnyStr):
        self.while_start_labels[while_name] = label_value

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def write_file(self, filename: AnyStr = "three_directions_code.tdc"):
        pass

    @abstractmethod
    def relate_register_and_reference(self, reference: str, register: Register):
        pass

    @abstractmethod
    def relate_register_and_item_from_registers(self, index=-1):
        pass

    @abstractmethod
    def add_pending_and_subscribe(self, temporal_tag: AnyStr, register: Register):
        pass

    @abstractmethod
    def get_next_label_count(self):
        pass

    @abstractmethod
    def get_next_class_label_count(self):
        pass

    @abstractmethod
    def get_next_method_label_count(self):
        pass

    def get_next_temp_variable(self) -> AnyStr:
        self.temp_var_count += 1
        return f"t{self.temp_var_count}"

    def add_register(self, register: Register):
        self.code.append(register)

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



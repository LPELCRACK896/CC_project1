from anytree import Node
from typing import List, Dict, Tuple, AnyStr
from Symbol import Symbol
from Scope import Scope
import os

from Register import Register
from Direction import Direction
from Operation import Operation

from NotedNode import create_noted_node

# Interface
from IThreeDirectionsCode import IThreeDirectionsCode


class ThreeDirectionsCode(IThreeDirectionsCode):

    opened_scopes: List[Scope]

    def __init__(self, scopes: Dict[AnyStr, Scope], content):
        super().__init__(scopes, content)
        self.opened_scopes = []

    def __str__(self):
        return super().__str__()

    def is_higher_or_equal_scope_levels(self, reference_scope: Scope, scope_to_compare: Scope):
        pass

    def __is_forbidden_scope(self, scope_id: str):
        return (
                scope_id == "global" or
                scope_id.startswith("global-Object(class)") or
                scope_id.startswith("global-IO(class)") or
                scope_id.startswith("global-String(class)")
        )

    def create_scope_register(self, action: str, scope_label: str, direction: Direction):

        register = Register(
            tag=scope_label,
            first_direction=direction
        )
        register.set_first_operation(Operation(action))
        self.add_register(register)
        pass

    def __open_scope(self, scope: Scope):
        if len(self.opened_scopes) == 0:
            self.create_scope_register(
                action="START",
                scope_label=self.__get_label_scope(scope),
                direction=Direction(f"{scope.scope_id}", self.scopes))
            self.opened_scopes.append(scope)
            return

        last_scope_added = self.opened_scopes[-1]
        if scope.has_higher_hierarchy(last_scope_added):
            self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(last_scope_added),
                direction=Direction(f"{last_scope_added.scope_id}", self.scopes))

            self.opened_scopes.pop()

        elif last_scope_added.parent == scope.parent:
            self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(last_scope_added),
                direction=Direction(f"{last_scope_added.scope_id}", self.scopes))

            self.opened_scopes.pop()

        self.create_scope_register(
                action="START",
                scope_label=self.__get_label_scope(scope),
                direction=Direction(f"{scope.scope_id}", self.scopes)
        )
        self.opened_scopes.append(scope)

    def get_next_label_count(self):
        self.label_counter += 1
        return self.label_counter

    def get_next_class_label_count(self):
        self.label_class_counter += 1
        return self.label_class_counter

    def get_next_method_label_count(self):
        self.label_method_counter += 1
        return self.label_method_counter

    def __get_label_scope(self, scope: Scope):
        scope_id = scope.scope_id

        if scope_id.endswith("(class)"):
            return f"CL{self.get_next_class_label_count()}"
        elif scope_id.endswith("(method)"):
            return f"MT{self.get_next_method_label_count()}"

        return f"S{self.get_next_label_count()}"

    def build(self):
        current_scope  = ""
        for scope_id, symbols in self.content.items():

            if self.__is_forbidden_scope(scope_id):
                continue # Saltamos

            self.__open_scope(self.scopes.get(scope_id))
            
            for symbol_name, symbol in symbols.items():
                ast_node: Node = symbol.node

                if ast_node is None:
                    continue

                noted_node = create_noted_node(ast_node, self.content, self.scopes, symbol)

                if noted_node is None:

                    """                    class_regis = Register()
                    self.add_register(class_regis)"""
                    continue

                noted_node.get_three_direction_code(self, 3)

    def write_file(self, filename: AnyStr = "three_directions_code.tdc"):
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"

        with open(input_file, 'w') as file:
            file.write(str(self))

    def relate_register_and_reference(self, reference: str, register: Register):
        pass

    def relate_register_and_item_from_registers(self, index=-1):
        pass

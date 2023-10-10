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

    def __init__(self, scopes: Dict[AnyStr, Scope], content):
        super().__init__(scopes, content)


    def __str__(self):
        return super().__str__()

    def build(self):
        current_scope  = ""
        def is_forbidden_scope(scope_id: str):
            return  (
                scope_id == "global" or
                scope_id.startswith("global-Object(class)") or
                scope_id.startswith("global-IO(class)") or
                scope_id.startswith("global-String(class)")
            )

        for scope_id, symbols in self.content.items():

            if is_forbidden_scope(scope_id):
                continue # Saltamos

            # Añadir registro inicio clase

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

            # Añadir registro fin clase

    def write_file(self, filename: AnyStr = "three_directions_code.tdc"):
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"

        with open(input_file, 'w') as file:
            file.write(str(self))

    def relate_register_and_reference(self, reference: str, register: Register):
        pass

    def relate_register_and_item_from_registers(self, index=-1):
        pass

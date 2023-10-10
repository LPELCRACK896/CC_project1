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

    opened_class_scopes: List[Scope]
    opened_method_scopes: List[Scope]
    opened_let_scopes: List[Scope]
    opened_scopes: List[Scope]

    def __init__(self, scopes: Dict[AnyStr, Scope], content, sequential_symbols: List[Symbol]):
        super().__init__(scopes, content, sequential_symbols)
        self.opened_scopes = []
        self.opened_class_scopes = []
        self.opened_method_scopes = []
        self.opened_let_scopes = []

    def __str__(self):
        return super().__str__()

    def is_higher_or_equal_scope_levels(self, reference_scope: Scope, scope_to_compare: Scope):
        pass

    def __is_forbidden_scope(self, scope_id: str, scope_name: str):
        return (
                scope_id.startswith("global-Object(class)") or
                scope_id.startswith("global-IO(class)") or
                scope_id.startswith("global-IO(class)-out_string(method)") or
                scope_id.startswith("global-IO(class)-out_int(method)") or 
                scope_id.startswith("global-String(class)") or 
                scope_id.startswith("global-String(class)-concat") or
                scope_id.startswith("global-String(class)-substr") or 
                (scope_id.startswith("global") and scope_name.startswith("Object")) or
                (scope_id.startswith("global") and scope_name.startswith("IO")) or
                (scope_id.startswith("global") and scope_name.startswith("Int")) or
                (scope_id.startswith("global") and scope_name.startswith("String")) or
                (scope_id.startswith("global") and scope_name.startswith("Bool"))
        )

    def create_scope_register(self, action: str, scope_label: str, direction: Direction):

        register = Register(
            tag=scope_label,
            first_direction=direction
        )
        register.set_first_operation(Operation(action))
        self.add_register(register)
        pass

    def create_blank_register(self):

        register = Register(
            tag=" ",
            first_direction=Direction(" ", self.scopes)
        )
        register.set_first_operation(Operation(" "))
        self.add_register(register)
        pass

    def __open_scope(self, scope: Scope):

        if scope.scope_id.endswith("(class)"):
            self.opened_class_scopes.append(scope)    

        if len(self.opened_scopes) == 0:
            self.create_scope_register(
                action="START",
                scope_label=self.__get_label_scope(scope),
                direction=Direction(f"{scope.scope_id}", self.scopes))
            self.opened_scopes.append(scope)
            return

        last_scope_added = self.opened_scopes[-1]
        if scope.has_higher_hierarchy(last_scope_added) or scope.has_same_hierarchy(last_scope_added):             
            self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(last_scope_added),
                direction=Direction(f"{last_scope_added.scope_id}", self.scopes))

            self.opened_scopes.pop()

        try: 
            method1 = last_scope_added.scope_id.split("-")[2] 
            method2 = scope.scope_id.split("-")[2]
            if method1 != method2:
                if last_scope_added.scope_id.split("-let"):
                    last_scope_added = self.opened_scopes.pop()
                    self.create_scope_register(
                        action="END",
                        scope_label=self.__get_label_scope(last_scope_added),
                        direction=Direction(f"{last_scope_added.scope_id}", self.scopes))

                    self.opened_scopes.pop()
        except:
            pass

        if len(self.opened_class_scopes) != 0 and scope.scope_id.endswith("(class)"): # fin de clase
            last_class_scope_added = self.opened_class_scopes.pop(0)
            if last_class_scope_added.scope_id != scope.scope_id:
                self.create_scope_register(
                    action="END",
                    scope_label=self.__get_label_scope(last_class_scope_added),
                    direction=Direction(f"{last_class_scope_added.scope_id}", self.scopes))

                self.create_blank_register()
            else:
                self.opened_class_scopes.append(last_class_scope_added)

        self.create_scope_register(
                action="START",
                scope_label=self.__get_label_scope(scope),
                direction=Direction(f"{scope.scope_id}", self.scopes)
        )
        self.opened_scopes.append(scope)

    def __re_open_scope_(self, scope: Scope, symbol_name: str, symbol_semantic_type: str):
        
        if len(self.opened_class_scopes) == 0 and scope.scope_id == "global": # en caso de ser clase y no haya clase abierta
            self.create_scope_register(
                action="START",
                scope_label=self.__get_label_scope(scope),
                direction=Direction(f"{symbol_name}", self.scopes))
            self.opened_class_scopes.append((scope, symbol_name))
            return        
        elif scope.scope_id == "global": # en caso de ser clase y exista clase en el stack
            last_class_opened, last_class_name = self.opened_class_scopes.pop()
            if symbol_name != last_class_name:
                if len(self.opened_method_scopes) != 0: # cerrar metodos pendientes
                    self.__close_opened_methods_scopes()
                self.create_scope_register(
                    action="END",
                    scope_label=self.__get_label_scope(last_class_opened),
                    direction=Direction(f"{last_class_name}", self.scopes))
                self.create_blank_register()

                self.create_scope_register(
                    action="START",
                    scope_label=self.__get_label_scope(scope),
                    direction=Direction(f"{symbol_name}", self.scopes))
                self.opened_class_scopes.append((scope, symbol_name))
                return
            
        if len(self.opened_method_scopes) == 0 and symbol_semantic_type == "method": # para metodos y que aun no existan metodos en el stack
            self.create_scope_register(
                action="START",
                scope_label=self.__get_label_method_scope(scope, symbol_semantic_type),
                direction=Direction(f"{symbol_name}", self.scopes))
            self.opened_method_scopes.append((scope, symbol_name, symbol_semantic_type))
            return  
        elif symbol_semantic_type == "method": # para metodos con un metodo anterior en el stack
            last_class_opened, last_class_name, last_class_semantic_type = self.opened_method_scopes.pop()
            if symbol_name != last_class_name:
                self.create_scope_register(
                    action="END",
                    scope_label=self.__get_label_method_scope(last_class_opened, last_class_semantic_type),
                    direction=Direction(f"{last_class_name}", self.scopes))

                self.create_scope_register(
                    action="START",
                    scope_label=self.__get_label_method_scope(scope, symbol_semantic_type),
                    direction=Direction(f"{symbol_name}", self.scopes))
                self.opened_method_scopes.append((scope, symbol_name, symbol_semantic_type))
                return
            
        if scope.scope_id.endswith("let)"): # para los lets 
            last_register = self.code[-1].first_direction
            if str(last_register) != str(f"{scope.scope_id.split("-")[2].split("(")[0]}-{scope.scope_id.split("-")[3].split("(")[0]}"):        
                self.create_scope_register(
                    action="START",
                    scope_label=self.__get_label_scope(scope),
                    direction=Direction(f"{scope.scope_id.split("-")[2].split("(")[0]}-{scope.scope_id.split("-")[3].split("(")[0]}", self.scopes))
                self.opened_let_scopes.append((scope))
                return 
        elif len(self.opened_let_scopes) != 0: # para cerrar los lets y sin mas scopes abiertos
            last_opened_scope = self.opened_let_scopes[-1]
            if not scope.scope_id.endswith(last_opened_scope.scope_id.split("-")[3]):
                self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(last_opened_scope),
                direction=Direction(f"{last_opened_scope.scope_id.split("-")[2].split("(")[0]}-{last_opened_scope.scope_id.split("-")[3].split("(")[0]}", self.scopes))
            self.opened_let_scopes.pop()
            return 

    def __close_opened_scopes(self):
        while self.opened_scopes:
            scope = self.opened_scopes.pop()
            self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(scope),
                direction=Direction(f"{scope.scope_id}", self.scopes))
            
    def __close_opened_class_scopes(self):
        scope, scope_name = self.opened_class_scopes.pop()
        self.create_scope_register(
            action="END",
            scope_label=self.__get_label_scope(scope),
            direction=Direction(f"{scope_name}", self.scopes))
        
    def __close_opened_methods_scopes(self):
        scope, scope_name, semantic_type = self.opened_method_scopes.pop()
        self.create_scope_register(
            action="END",
            scope_label=self.__get_label_method_scope(scope, semantic_type),
            direction=Direction(f"{scope_name}", self.scopes))

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

        if scope_id.endswith("global"):
            return f"CL{self.get_next_class_label_count()}"

        elif scope_id.endswith("blank"):
            return f" "

        return f"S{self.get_next_label_count()}"
    
    def __get_label_method_scope(self, scope: Scope, semantic_type: str):
        scope_id = scope.scope_id

        if semantic_type == "method":
            return f"MT{self.get_next_method_label_count()}"
        elif scope_id.endswith("blank"):
            return f" "

        return f"S{self.get_next_label_count()}"

    def build(self):
        self.code = []
        current_scope = ""
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
                    continue

                noted_node.get_three_direction_code(self, 3)

        self.__close_opened_scopes()

    def new_build(self):
        self.code = []
        self.create_blank_register()
        for symbol in self.sequential_symbols:
            scope_id = symbol.scope
            symbol_name = symbol.name
            symbol_semantic_type = symbol.semantic_type

            if self.__is_forbidden_scope(scope_id, symbol_name):
                continue

            self.__re_open_scope_(self.scopes.get(scope_id), symbol_name, symbol_semantic_type)
            # Re - implement -> Opening scopes
            ast_node: Node = symbol.node

            if ast_node is None:
                continue

            noted_node = create_noted_node(ast_node, self.content, self.scopes, symbol)

            if noted_node is None:
                continue

            noted_node.get_three_direction_code(self, 3)

        self.__close_opened_class_scopes()

    def write_file(self, filename: AnyStr = "three_directions_code.tdc"):
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"

        with open(input_file, 'w') as file:
            file.write(str(self))

    def relate_register_and_reference(self, reference: str, register: Register):
        pass

    def relate_register_and_item_from_registers(self, index=-1):
        pass

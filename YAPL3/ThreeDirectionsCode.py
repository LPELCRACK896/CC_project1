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
    opened_if_scopes: List[Scope]
    opened_scopes: List[Scope]

    conditional_waiting_list: List[AnyStr]
    waiting_list_subscriptions: Dict[AnyStr, List[Register]]

    def __init__(self, scopes: Dict[AnyStr, Scope], content, sequential_symbols: List[Symbol]):
        super().__init__(scopes, content, sequential_symbols)
        self.opened_scopes = []
        self.opened_class_scopes = []
        self.opened_method_scopes = []
        self.opened_let_scopes = []
        self.opened_if_scopes = []
        self.conditional_waiting_list = []

    def __str__(self):
        return super().__str__()

    def new_build(self):
        self.code = []
        for symbol in self.sequential_symbols:
            scope_id = symbol.scope
            symbol_name = symbol.name
            symbol_semantic_type = symbol.semantic_type

            if self.__is_forbidden_scope(scope_id, symbol_name):
                continue

            self.conditional_listener(symbol)
            self.__re_open_scope_(self.scopes.get(scope_id), symbol_name, symbol_semantic_type)

            ast_node: Node = symbol.node

            if ast_node is None:
                continue

            noted_node = create_noted_node(ast_node, self.content, self.scopes, symbol)

            if noted_node is None:
                continue


            noted_node.get_three_direction_code(self, 3)

        self.__close_opened_class_scopes()

        for i, register in enumerate(self.code):
            if str(register.first_direction).startswith("(newMain).main()"):
                self.code.pop(i)

    def is_higher_or_equal_scope_levels(self, reference_scope: Scope, scope_to_compare: Scope):
        pass

    @staticmethod
    def __is_forbidden_scope(scope_id: str, scope_name: str):
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
            if str(last_register) != str(f"{scope.scope_id.split('-')[2].split('(')[0]}-{scope.scope_id.split('-')[3].split('(')[0]}"):
                self.create_scope_register(
                    action="START",
                    scope_label=self.__get_label_scope(scope),
                    direction=Direction(f"{scope.scope_id.split('-')[2].split('(')[0]}-{scope.scope_id.split('-')[3].split('(')[0]}", self.scopes)
                )
                self.opened_let_scopes.append((scope))
                return
        elif len(self.opened_let_scopes) != 0: # para cerrar los lets y sin mas scopes abiertos
            last_opened_scope = self.opened_let_scopes[-1]
            if not scope.scope_id.endswith(last_opened_scope.scope_id.split("-")[3]):
                self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(last_opened_scope),
                    direction=Direction(
                        f'{last_opened_scope.scope_id.split("-")[2].split("(")[0]}-{last_opened_scope.scope_id.split("-")[3].split("(")[0]}',
                        self.scopes)
                )
                self.opened_let_scopes.pop()
            return

        if scope.scope_id.endswith("if)"): # para los ifs
            if not  scope.scope_id.split("-")[3].startswith("ELSE"):
                self.create_scope_register(
                    action="START",
                    scope_label=self.__get_label_scope(scope),
                    direction=Direction(
                        f'{scope.scope_id.split("-")[2].split("(")[0]}-{scope.scope_id.split("-")[3].split("(")[0]}',
                        self.scopes))
                self.opened_if_scopes.append((scope))
                return
            else:
                last_opened_scope = self.opened_if_scopes[-1]
                self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(last_opened_scope),
                    direction=Direction(
                        f'{last_opened_scope.scope_id.split("-")[2].split("(")[0]}-{last_opened_scope.scope_id.split("-")[3].split("(")[0]}',
                        self.scopes)
                )
                self.opened_if_scopes.pop()

                self.create_scope_register(
                    action="START",
                    scope_label=self.__get_label_scope(scope),
                    direction=Direction(
                        f'{scope.scope_id.split("-")[2].split("(")[0]}-{scope.scope_id.split("-")[3].split("(")[0]}',
                        self.scopes))
                self.opened_if_scopes.append((scope))
                return
        elif len(self.opened_if_scopes) != 0: # para cerrar los ifs 
            last_opened_scope = self.opened_if_scopes[-1]
            if not scope.scope_id.endswith(last_opened_scope.scope_id.split("-")[3]):
                self.create_scope_register(
                action="END",
                scope_label=self.__get_label_scope(last_opened_scope),
                    direction=Direction(
                        f'{last_opened_scope.scope_id.split("-")[2].split("(")[0]}-{last_opened_scope.scope_id.split("-")[3].split("(")[0]}',
                        self.scopes)
                )
                self.opened_if_scopes.pop()
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

    def conditional_listener(self, symbol: Symbol):
        if not self.conditional_waiting_list:
            return
        last_waiting: AnyStr = self.conditional_waiting_list[-1]
        if last_waiting.endswith("if"):
            self.conditional_listener_if(symbol)
        elif last_waiting.endswith("else"):
            self.conditional_listener_else(symbol)
        else:
            self.conditional_listener_while(symbol)

    def conditional_listener_while(self, symbol: Symbol):
        if not self.conditional_waiting_list:
            return
        last_waiting: AnyStr = self.conditional_waiting_list[-1]
        if f"WHILE({last_waiting})" in symbol.scope:
            return
        pass

    def conditional_listener_if(self, symbol: Symbol):
        if not self.conditional_waiting_list:
            return
        if_waiting: AnyStr = self.conditional_waiting_list[-1]

        if f"IF({if_waiting})" in symbol.scope:
            return

        else_id = if_waiting.split("i")[0]
        else_temp_tag = f"{else_id}else"
        else_direction = Direction(else_temp_tag, self.scopes)
        goto = Operation("GOTO")
        else_reg = Register("", else_direction)
        else_reg.set_first_operation(goto)

        self.add_register(else_reg)

        real_tag = f"L{self.get_next_label_count()}"
        self.notify_subscribers(if_waiting, real_tag)

        if_goto_direction = Direction(real_tag, self.scopes)
        label_dir = Direction("LABEL", self.scopes)

        real_register = Register(real_tag, label_dir)

        self.add_register(real_register)

        self.add_pending_and_subscribe(else_temp_tag, else_reg)

    def conditional_listener_else(self, symbol: Symbol):
        if not self.conditional_waiting_list:
            return
        last_waiting: AnyStr = self.conditional_waiting_list[-1]

        if f"ELSE({last_waiting})" in symbol.scope:
            return
        pass

    def notify_subscribers(self, subscription_item: AnyStr, tag_replacement: AnyStr):
        if not (subscription_item in self.waiting_list_subscriptions
                and subscription_item in self.conditional_waiting_list):
            return

        registers_subscribed = self.waiting_list_subscriptions[subscription_item]
        temporal_tag = subscription_item

        for register in registers_subscribed:
            register.update_directions_tag(temporal_tag, tag_replacement)

    def add_pending_and_subscribe(self, temporal_tag: AnyStr, register: Register):
        if temporal_tag not in self.conditional_waiting_list:
            self.conditional_waiting_list.append(temporal_tag)

        self.subscribe_register_to_waiting_item(register, temporal_tag)

    def subscribe_register_to_waiting_item(self, register: Register, item: AnyStr):
        if item not in self.conditional_waiting_list:
            return

        if item in self.waiting_list_subscriptions:
            self.waiting_list_subscriptions[item].append(register)

        self.waiting_list_subscriptions[item] = [register]

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

    def write_file(self, filename: AnyStr = "three_directions_code.tdc"):
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"

        with open(input_file, 'w') as file:
            file.write(str(self))

    @staticmethod
    def get_id_from_if (if_name):
        return if_name.split("i")[0]

    @staticmethod
    def get_id_from_while (if_name):
        return if_name.split("w")[0]

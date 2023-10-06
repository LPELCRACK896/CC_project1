from abc import abstractmethod
from typing import Dict, AnyStr, List

from Symbol import Symbol
from anytree import Node
from Scope import Scope
from SemanticCommon import SemanticError

import node_structures as ns


class NotedNode:
    node_type: str
    children: list
    node: Node

    needs_symbol: bool
    needs_context: bool
    need_scopes: bool

    scopes: Dict[AnyStr, Scope] | None = None
    symbol: Symbol | None = None
    context: Dict[AnyStr, Dict[AnyStr, Symbol]] | None = None

    raised_errors: Dict[AnyStr, List[SemanticError]]
    # raised_warnings: Dict[AnyStr, List[SemanticError]]

    def __init__(self, node: Node):
        self.node = node
        self.node_type = node.name
        self.children = node.children
        self.needs_context = False
        self.need_scopes = False
        self.needs_symbol = False
        self.raised_errors = {}

    def add_context(self, context: Dict[AnyStr, Dict[AnyStr, Symbol]]):
        self.context = context

    def add_scopes(self, scopes: Dict[AnyStr, Scope]):
        self.scopes = scopes

    def add_symbol(self, symbol):
        self.symbol = symbol

    def get_symbol(self) -> Symbol | None:
        return self.symbol

    def has_symbol(self) -> bool:
        return isinstance(self.symbol, Symbol)

    def has_context(self) -> bool:
        return isinstance(self.context, dict)

    def has_scopes(self) -> bool:
        return isinstance(self.scopes, dict)

    def add_error(self, error_type: str, error: SemanticError):
        if error_type in self.raised_errors:
            if error not in self.raised_errors[error_type]:
                self.raised_errors[error_type].append(error)
        else:
            self.raised_errors[error_type] = [error]

    def extend_errors(self, other_raised_errors: Dict[AnyStr, List[SemanticError]]):
        for error_type, errors in other_raised_errors:
            for error in errors:
                self.add_error(error_type, error)

    @abstractmethod
    def get_previous_declaration(self, name: str):
        pass

    @abstractmethod
    def get_value(self) -> str | None:
        pass

    @abstractmethod
    def get_type(self) -> str | None:
        pass

    @abstractmethod
    def get_value_type(self) -> str | None:
        pass

    @abstractmethod
    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        pass


class BasicNotedNode(NotedNode):

    def __init__(self, node: Node):
        super().__init__(node)

    def get_value(self) -> str | None:
        return self.children[0].name

    def get_previous_declaration(self, name: str):
        pass

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        return self.raised_errors

    @abstractmethod
    def get_type(self) -> str | None:
        pass

    @abstractmethod
    def get_value_type(self) -> str | None:
        pass


class IntegerNotedNode(BasicNotedNode):

    def __init__(self, node: Node):
        super().__init__(node)

    def get_type(self) -> str | None:
        return "Int"

    def get_value_type(self) -> str | None:
        return "Int"


class StringNotedNote(BasicNotedNode):

    def __init__(self, node: Node):
        super().__init__(node)

    def get_type(self) -> str | None:
        return "String"

    def get_value_type(self) -> str | None:
        return "String"


class BooleanNotedNode(BasicNotedNode):

    def __init__(self, node: Node):
        super().__init__(node)

    def get_type(self) -> str | None:
        return "Bool"

    def get_value_type(self) -> str | None:
        return "Bool"


class AssignationNotedNote(NotedNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.needs_symbol = True
        self.needs_context = True
        self.need_scopes = True

    def get_previous_declaration(self, name: str):
        symbols_scope = self.scopes.get(self.symbol.scope)

        symbol_declaration = search_symbol_by_name(symbols_scope, name)

        if symbol_declaration is None:
            self.add_error("Undeclared variable::",
                           SemanticError(
                               name="Undeclared variable::",
                               details=f"Assignation tried to use undeclared variable {name}",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))

        return symbol_declaration

    def get_type(self) -> str | None:
        name = self.children[0].name

        symbol_declaration = self.get_previous_declaration(name)
        if symbol_declaration is None:
            #   Error handled in get_previous_declaration()
            return None

        if symbol_declaration.semantic_type == "expression" and symbol_declaration.node is not None:
            nn_declaration = create_noted_node(symbol_declaration.node, self.context, self.scopes, symbol_declaration)
            nn_type = nn_declaration.get_type()
            self.extend_errors(nn_declaration.run_tests())
            return nn_type

        return symbol_declaration.data_type

    def get_value(self) -> str | None:
        symbols_scope = self.scopes.get(self.symbol.scope)
        nn_value = create_noted_node(self.children[2], self.context, self.scopes, None)
        if nn_value is None:
            self.add_error("Invalid expression::",
                           SemanticError(
                               name="Invalid expression::",
                               details=f"Assignation tried to get value from {self.children[2]}",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))
            return None

        nn_value.run_tests()
        nn_value_value = nn_value.get_value()
        self.extend_errors(nn_value.raised_errors)

        return nn_value_value

    def get_value_type(self) -> str | None:
        nn_value = create_noted_node(self.children[2], self.context, self.scopes, None)
        if nn_value is None:
            #   Error handled in get_value()
            return None

        return nn_value.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        symbols_scope = self.scopes.get(self.symbol.scope)

        var_value_type = self.get_value_type()
        var_expected_type = self.get_type()

        if var_expected_type is None:
            self.add_error("In-existing class referenced::",
                           SemanticError(
                               name="In-existing class referenced::",
                               details=f"Assignation got variable with in-existing type declared.",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))

        if var_value_type is None:
            self.add_error("In-existing class referenced::",
                           SemanticError(
                               name="In-existing class referenced::",
                               details=f"Assignation got variable with in-existing type received.",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))

        if var_value_type is not None and var_expected_type is not None:

            valid_expected_type = verify_existing_type(var_expected_type, self.scopes)
            valid_value_type = verify_existing_type(var_value_type, self.scopes)

            if not valid_expected_type:
                self.add_error("In-existing class referenced::",
                               SemanticError(
                                   name="In-existing class referenced::",
                                   details=f"Assignation got variable "
                                           f"with in-existing type received {var_expected_type}",
                                   symbol=self.symbol,
                                   scope=symbols_scope,
                                   line=self.symbol.start_line
                               ))

            if not valid_value_type:
                self.add_error("In-existing class referenced::",
                               SemanticError(
                                   name="In-existing class referenced::",
                                   details=f"Assignation got variable with in-existing type expected {var_value_type}.",
                                   symbol=self.symbol,
                                   scope=symbols_scope,
                                   line=self.symbol.start_line
                               ))

            if valid_expected_type and valid_value_type:
                if not verify_matching_type(var_expected_type, var_value_type, self.scopes):
                    self.add_error("Incoherence types::",
                                   SemanticError(
                                       name="Incoherence types::",
                                       details=f"On assignation expected type {var_expected_type}"
                                               f" does not match the received type {var_value_type}",
                                       symbol=self.symbol,
                                       scope=symbols_scope,
                                       line=self.symbol.start_line
                                   ))

        return self.raised_errors


class AttributeNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_previous_declaration(self, name: str):
        return self.symbol

    def get_value(self) -> str | None:
        symbols_scope = self.scopes.get(self.symbol.scope)
        structure_type = ns.verify_node_structure_attribute(self.node)
        if structure_type != 2:
            return None
        nn_value = create_noted_node(self.children[4], self.context, self.scopes, None)
        if nn_value is None:
            self.add_error("Invalid expression::",
                           SemanticError(
                               name="Invalid expression::",
                               details=f"Attribute assignation tried to get value from {self.children[4]}",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))
            return None
        nn_value_value = nn_value.get_value()
        self.extend_errors(nn_value.run_tests())
        return nn_value_value

    def get_type(self) -> str | None:
        return self.children[2].children[0].name

    def get_value_type(self) -> str | None:
        structure_type = ns.verify_node_structure_attribute(self.node)
        if structure_type != 2:
            return None
        nn_value = create_noted_node(self.children[4], self.context, self.scopes, None)
        if nn_value is None:
            #   Error handled in get_value()
            return None
        return nn_value.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        symbols_scope = self.scopes.get(self.symbol.scope)

        var_value_type = self.get_value_type()
        var_expected_type = self.get_type()

        if var_value_type is not None and var_expected_type is not None:
            coherent_types = verify_matching_type(var_value_type, var_expected_type, self.scopes)
            if not coherent_types:
                self.add_error("Incoherence types::",
                               SemanticError(
                                   name="Incoherence types::",
                                   details=f"On attribute assignation expected type {var_expected_type}"
                                           f" does not match the received type {var_value_type}",
                                   symbol=self.symbol,
                                   scope=symbols_scope,
                                   line=self.symbol.start_line
                               ))

        return self.raised_errors


class NewObjectNotedNode(NotedNode):

    def __init__(self, nodes):
        super().__init__(nodes)
        self.need_scopes = True
        self.needs_context = True

    def get_value(self) -> str | None:
        return "new " + self.children[1].name

    def get_type(self) -> str | None:
        return self.children[1]

    def get_value_type(self) -> str | None:
        return self.children[1]

    def get_previous_declaration(self, name: str):
        if not verify_existing_type(name, self.scopes):
            self.add_error("Undeclared class::",
                           SemanticError(
                               name="Undeclared class::",
                               details=f"new operator tried to create object from undefined {name}",
                               symbol=self.symbol,
                               scope=self.scopes.get("global"),
                               line=self.symbol.start_line
                           ))
            return None
        global_scope = self.scopes.get("global")
        return global_scope.get_all_classees().get(name)

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_type()
        self.get_value_type()
        self.get_value()
        self.get_previous_declaration(self.children[1].name)
        return self.raised_errors


def create_noted_node(node: Node,
                      context: Dict[AnyStr, Dict[AnyStr, Symbol]],
                      scopes: Dict[AnyStr, Scope],
                      symbol: Symbol | None
                      ) -> NotedNode | None:
    index_type_node = ns.identify_node(node)

    noted_node: NotedNode | None = None

    if index_type_node == -1:
        print("INTERNAL ERROR: ERROR AL IDENTIFICAR EXPR")
        return None

    type_of_expr = ns.expressions[index_type_node]

    if type_of_expr == "assignment":
        noted_node = AssignationNotedNote(node)
    elif type_of_expr == "integer":
        noted_node = IntegerNotedNode(node)
    elif type_of_expr == "string":
        noted_node = StringNotedNote(node)
    elif type_of_expr == "boolean_true":
        noted_node = BooleanNotedNode(node)
    elif type_of_expr == "boolean_false":
        noted_node = BooleanNotedNode(node)
    elif type_of_expr == "attribute":
        noted_node = AttributeNotedNode(node)
    elif type_of_expr == "object_creation":
        noted_node = NewObjectNotedNode(node)
    elif type_of_expr == "dynamic_dispatch":
        pass
    elif type_of_expr == "static_dispatch":
        pass
    elif type_of_expr == "function_call":
        pass
    elif type_of_expr == "conditional":
        pass
    elif type_of_expr == "loop":
        pass
    elif type_of_expr == "block":
        pass
    elif type_of_expr == "let_in":
        pass
    elif type_of_expr == "isvoid":
        pass
    elif type_of_expr == "not":
        pass
    elif type_of_expr == "bitwise_not":
        pass
    elif type_of_expr == "arithmetic_or_comparison":
        pass
    elif type_of_expr == "parenthesized_expr":
        pass
    elif type_of_expr == "identifier":
        pass
    else:
        print(f"Tipo de expresión no reconocido: {type_of_expr}")

    if noted_node is not None:
        if noted_node.need_scopes:
            noted_node.add_scopes(scopes)

        if noted_node.needs_context:
            noted_node.add_context(context)

        if noted_node.needs_symbol:
            noted_node.add_symbol(symbol)

    return noted_node


"""
AUXILIARY FUNCTIONS
"""


def search_symbol_by_name(searching_scope: Scope, name: str) -> Symbol | None:

    result = searching_scope.search_content(name)
    not_found = result is None

    if not_found:
        next_scope = searching_scope.parent
        if next_scope is None:
            return None

        return search_symbol_by_name(next_scope, name)

    return result


def verify_existing_type(type_name: str, scopes: Dict[AnyStr, Scope]) -> bool:

    basic_types = ["Int", "String", "Bool", "Object", "IO"]

    if type_name in basic_types:
        return True

    # It's a created class
    global_scope = scopes.get("global")
    classes = global_scope.get_all_classees()

    return type_name in classes


def verify_matching_type(expected_type: str, received_type: str, scopes: Dict[AnyStr, Scope]) -> bool:

    if expected_type == received_type:
        return True

    if not verify_existing_type(expected_type, scopes) or  not verify_existing_type(received_type, scopes):
        return False

    global_scope = scopes.get("global")
    classes = global_scope.get_all_classees()

    current_class = received_type
    equivalent_classes = []

    while current_class != "Object":
        equivalent_classes.append(current_class)
        current_class_symbol: Symbol = classes.get(current_class)
        current_class = current_class_symbol.data_type

    if expected_type in equivalent_classes:
        return True



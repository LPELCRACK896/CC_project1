from abc import abstractmethod
from typing import Dict, AnyStr, List, Tuple

from Symbol import Symbol
from anytree import Node
from Scope import Scope
from SemanticCommon import SemanticError

import node_structures as ns

"""
USES TRANSLATION BASED ON SYNTAX LOGIC
Consider attributes
- type
- value
- value_type
- declaration
- alias
"""


class NotedNode:
    """

    Use symbol just as scope reference

    Attributes
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

    """
    node_type: str
    children: List[Node]
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
        for error_type, errors in other_raised_errors.items():
            for error in errors:
                self.add_error(error_type, error)

    def _is_valid_type(self, type_alias):
        symbols_scope = self.scopes.get(self.symbol.scope)
        if not verify_existing_type(type_alias, self.scopes):
            self.add_error(
                "Invalid Type::",
                SemanticError(
                    name="Invalid type::",
                    details=f"Type '{type_alias}' is not defined",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return False

        return True

    def get_default_value_from_typo(self):
        typo = self.get_type()
        if typo == "Int":
            return "0"
        elif typo == "Bool":
            return "false"
        elif typo == "String":
            return ""

        return None

    @abstractmethod
    def get_alias(self):
        pass

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

    def get_alias(self):
        return None

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
        nn_value = create_noted_node(self.children[2], self.context, self.scopes, self.symbol)
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
        nn_value = create_noted_node(self.children[2], self.context, self.scopes, self.symbol)
        if nn_value is None:
            #   Error handled in get_value()
            return None

        return nn_value.get_type()

    def get_alias(self):
        pass

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

    def get_alias(self):
        return self.children[0].name

    def get_value(self) -> str | None:
        symbols_scope = self.scopes.get(self.symbol.scope)
        structure_type = ns.verify_node_structure_attribute(self.node)
        if structure_type != 2:
            return None
        nn_value = create_noted_node(self.children[4], self.context, self.scopes, self.symbol)
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
        attr_type = self.children[2].children[0].name
        symbols_scope = self.scopes.get(self.symbol.scope)
        if not verify_existing_type(attr_type, self.scopes):
            self.add_error(
                "Invalid type declared on attribute::",
                SemanticError(
                    name="Invalid type declared on attribute::",
                    details=f"Variable declared (ln {self.symbol.start_line}) has invalid type '{attr_type}'"
                            f"is not recognized in file. Make sure to either set primitive type or own class.",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None
        return attr_type

    def get_value_type(self) -> str | None:
        structure_type = ns.verify_node_structure_attribute(self.node)
        if structure_type != 2:
            return None
        nn_value = create_noted_node(self.children[4], self.context, self.scopes, self.symbol)
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
        self.needs_symbol = True

    def get_value(self) -> str | None:
        default_res = self.get_default_value_from_typo()
        if default_res is not None:
            return default_res
        return "new " + self.children[1].name

    def get_alias(self):
        return "new " + self.children[1].name

    def get_type(self) -> str | None:
        return to_string_node(self.children[1])

    def get_value_type(self) -> str | None:
        return to_string_node(self.children[1])

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
        ttype = self.get_type()
        self.get_value_type()
        self.get_value()
        self.get_previous_declaration(to_string_node(self.children[1]))
        return self.raised_errors


class ParenthesisNotedNode(NotedNode):
    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_previous_declaration(self, name: str):
        return None

    def get_alias(self):
        return " ".join([leave.name for leave in self.node.leaves])

    def __get_contained_nn(self):
        return create_noted_node(self.children[1], self.context, self.scopes, self.symbol)

    def __validate_content(self):
        nn_content_exp = self.__get_contained_nn()
        if nn_content_exp is None:
            symbols_scope = self.scopes.get(self.symbol.scope)
            self.add_error("Invalid parenthesis content::",
                           SemanticError(
                               name="Invalid parenthesis content::",
                               details=f"Parenthesis couldn't get value or type from {self.children[1].name}",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line)
                           )
        return nn_content_exp

    def get_value(self) -> str | None:
        content = self.__get_contained_nn()
        if content is None:
            return None
        self.extend_errors(content.run_tests())
        content_value = content.get_value_type()

        return content_value  # Might be null but error would be handled in the called noted node

    def get_type(self) -> str | None:
        content = self.__get_contained_nn()
        if content is None:
            return None
        self.extend_errors(content.run_tests())
        content_value = content.get_type()

        return content_value  # Might be null but error would be handled in the called noted node

    def get_value_type(self) -> str | None:
        return self.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_value_type()
        self.get_value()
        self.get_type()

        return self.raised_errors


class IdentifierNotedNode(NotedNode):
    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_previous_declaration(self, name: str):
        symbols_scope = self.scopes.get(self.symbol.scope)
        result = search_symbol_by_name(symbols_scope, name)
        if result is None:
            self.add_error(
                "Undeclared variable::",
                SemanticError(
                    name="Undeclared variable::",
                    details=f"Variable '{name}' hasn't being declared",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

        if not (result.semantic_type == "attr"
                or result.semantic_type == "expression" and result.type_of_expression == "declaration_assignation"):
            self.add_error(
                "Invalid variable declaration::",
                SemanticError(
                    name="Invalid variable declaration::",
                    details=f"Variable {name} hasn't being declared either as attribute or in an accessible let block",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

            return None

        return result

    def get_value(self) -> str | None:
        name = self.get_alias()
        declaration = self.get_previous_declaration(name)
        symbols_scope = self.scopes.get(self.symbol.scope)

        if declaration is None:
            self.add_error(
                "Undeclared variable value::",
                SemanticError(
                    name="Undeclared variable value::",
                    details=f"Cannot get value from invalid or in-existing declaration from variable {name}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        node_attr = declaration.node
        nn_node_declaration = create_noted_node(node_attr, self.context, self.scopes, self.symbol)

        if nn_node_declaration is None:
            self.add_error(
                "Inappropriate declaration::",
                SemanticError(
                    name="Inappropriate declaration::",
                    details=f"Although variable seem doesnt correspond to any "
                            f"recognized pattern from{to_string_node(node_attr)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        self.extend_errors(nn_node_declaration.run_tests())
        declaration_value = nn_node_declaration.get_value()

        if declaration_value is None:
            # Add code to recognize path to this point, and it was assigned

            self.add_error(
                "WARNING No value found::",
                SemanticError(
                    name="WARNING No value found::",
                    details=f"Although variable seem to be declared it doesn't seem to has value",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        return declaration_value

    def get_type(self) -> str | None:
        name = self.get_alias()
        symbols_scope = self.scopes.get(self.symbol.scope)
        declaration_symbol = self.get_previous_declaration(name)

        if declaration_symbol is None:
            self.add_error(
                "Undeclared variable type::",
                SemanticError(
                    name="Undeclared variable type::",
                    details=f"Cannot get type from invalid or in-existing declaration from variable {name}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        declared_type = declaration_symbol.data_type

        if declared_type is None:
            self.add_error(
                "No type found on declaration::",
                SemanticError(
                    name="No type found on declaration::",
                    details=f"Although variable seem to be declared (ln {declaration_symbol.start_line})"
                            f" it doesn't seem to have a type",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        if not verify_existing_type(declared_type, self.scopes):
            self.add_error(
                "Unable to use invalid type declared::",
                SemanticError(
                    name="Unable to use invalid type declared::",
                    details=f"Variable declared (ln {declaration_symbol.start_line}) has invalid type '{declared_type}'"
                            f"is not recognized in file. Make sure to either set primitive type or own class.",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        return declared_type

    def get_value_type(self) -> str | None:
        return self.get_type()

    def get_alias(self):
        return self.children[0].name

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_previous_declaration(self.get_alias())

        return self.raised_errors


class DispatchNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def _get_instance(self, instance_referenced: Node) -> NotedNode | None:
        symbols_scope = self.scopes.get(self.symbol.scope)
        nn_instance_referenced = create_noted_node(instance_referenced, self.context, self.scopes, self.symbol)

        if nn_instance_referenced is None:
            self.add_error(
                "Invalid instance call::",
                SemanticError(
                    name="Invalid instance call::",
                    details=f"On method call, cannot get instance class from {to_string_node(instance_referenced)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

        self.extend_errors(nn_instance_referenced.run_tests())
        return nn_instance_referenced

    def _get_symbol_class(self, instance_referenced: Node) -> Symbol | None:
        nn_instance = self._get_instance(instance_referenced)
        symbols_scope = self.scopes.get(self.symbol.scope)

        if nn_instance is None:
            return None

        class_referenced = nn_instance.get_type()

        if class_referenced is None:
            self.add_error(
                "Invalid instance call::",
                SemanticError(
                    name="Invalid instance call::",
                    details=f"On method call, cannot get instance type from {to_string_node(nn_instance.node)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        symbol_class = search_class_symbol(class_referenced, self.scopes)

        if symbol_class is None:
            self.add_error(
                "Invalid instance call class::",
                SemanticError(
                    name="Invalid instance call class::",
                    details=f"On method call, cannot find class referenced called {class_referenced}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

        return symbol_class

    def _get_symbol_method(self, symbol_class: Symbol, method_name: str) -> Symbol | None:
        symbols_scope = self.scopes.get(self.symbol.scope)

        next_ancestor = symbol_class
        symbol_method = None

        while next_ancestor is not None and symbol_method is None:
            symbol_method = get_symbol_method(method_name, next_ancestor, self.scopes)

            if symbol_method is None:
                next_ancestor = get_symbol_class(next_ancestor.data_type, self.scopes)

        if symbol_method is None:
            self.add_error(
                "Invalid instance call::",
                SemanticError(
                    name="Invalid instance call::",
                    details=f"On method call, cannot find method referenced called {method_name} of {symbol_class.name}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        return symbol_method

    def _get_method_return_type(self, symbol_class: Symbol, symbol_method: Symbol):
        self_type = symbol_class.name

        return_type = symbol_method.data_type

        if return_type.upper() == "SELF_TYPE":
            return self_type

        if not verify_existing_type(return_type, self.scopes):
            self.add_error(
                "Undeclared class::",
                SemanticError(
                    name="Undeclared class::",
                    details=f"Method call found invalid firm with return type {return_type}",
                    symbol=self.symbol,
                    scope=self.scopes.get("global"),
                    line=self.symbol.start_line
                ))
            return None

        return return_type

    def _get_method_parameters(self, symbol_class: Symbol, symbol_method: Symbol):
        self_type = symbol_class.name

        parameters = symbol_method.parameters

        updated_parameters = []

        for parameter_name, parameter_type in parameters:
            updated_parameter_type = parameter_type if parameter_type.upper() != "SELF_TYPE" else self_type
            self._is_valid_type(updated_parameter_type)
            updated_parameters.append((parameter_name, updated_parameter_type))

        return updated_parameters

    def _compare_parameter(self, firm_parameter: tuple, received_parameter: Node, parameter_position: int):
        symbols_scope = self.scopes.get(self.symbol.scope)

        firm_param_name = firm_parameter[0]
        firm_param_type = firm_parameter[1]

        nn_expr_parameter = create_noted_node(received_parameter, self.context, self.scopes, self.symbol)
        if nn_expr_parameter is None:
            self.add_error(
                "Bad parameter::",
                SemanticError(
                    name="Bad parameter::",
                    details=f"Method call cannot get proper parameter from ({parameter_position})"
                            f" from expression {to_string_node(received_parameter)}. Expected type {firm_param_type} "
                            f"for param '{firm_param_name}' (No. {parameter_position})",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return False
        self.extend_errors(nn_expr_parameter.run_tests())
        received_param_type = nn_expr_parameter.get_type()

        if received_param_type is None:
            self.add_error(
                "Bad parameter::",
                SemanticError(
                    name="Bad parameter::",
                    details=f"Method call cannot get parameter type ({parameter_position})"
                            f" from expression {to_string_node(received_parameter)}. Expected type {firm_param_type} "
                            f"for param '{firm_param_name}' (No. {parameter_position})",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return False

        types_match = verify_matching_type(firm_param_type, received_param_type, self.scopes)

        if not types_match:
            self.add_error(
                "Bad Parameter type::",
                SemanticError(
                    name="Bad Parameter type::",
                    details=f"Method call got {to_string_node(received_parameter)} with type {received_param_type}. "
                            f"Expected {firm_param_type} type as parameter {firm_param_name} (No.{parameter_position})",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                ))

        return types_match

    def _compare_parameters(self, firm_parameters: List[Tuple], received_parameters: List[Node]):
        symbols_scope = self.scopes.get(self.symbol.scope)

        if len(firm_parameters) != len(received_parameters):
            self.add_error(
                "Unmatch count parameter firm::",
                SemanticError(
                    name="Unmatch count parameter firm::",
                    details=f"On method call parameters count does not match. expected: {len(firm_parameters)})"
                            f"  gotten ({len(received_parameters)})",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return False

        valid_param_type = True
        for num_parameter, (expr, firm_param) in enumerate(zip(received_parameters, firm_parameters)):
            valid_param_type = self._compare_parameter(firm_param, expr, num_parameter) and valid_param_type

        return valid_param_type
    
    def _deconstruct_given_parameter(self, position_open_parenthesis: int, position_closing_parenthesis: int):
        parenthesis_content = self.children[position_open_parenthesis+1:position_closing_parenthesis]
        return [item for item in parenthesis_content if item.name != ","]

    def get_alias(self):
        return to_string_node(self.node)
        

    @abstractmethod
    def get_previous_declaration(self, name: str):
        pass

    @abstractmethod
    def get_value(self) -> str | None:
        pass

    @abstractmethod
    def get_type(self) -> str | None:
        pass

    def get_value_type(self) -> str | None:
        return self.get_type()

    @abstractmethod
    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        pass


class DynamicDispatchNotedNode(DispatchNotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_alias(self):
        pass

    def get_previous_declaration(self, name: str):
        pass

    def get_value(self) -> str | None:
        pass

    def get_type(self) -> str | None:
        pass

    def get_value_type(self) -> str | None:
        pass

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        pass


class StaticDispatchNotedNode(DispatchNotedNode):
    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_previous_declaration(self, name: str):
        return None

    def get_value(self) -> str | None:
        return self.get_default_value_from_typo()

    def get_type(self) -> str | None:
        instance_expr = self.children[0]
        instance = self._get_instance(instance_expr)

        if instance is None:
            return None

        symbol_class = self._get_symbol_class(instance_expr)

        if symbol_class is None:
            return None

        method_name = self.children[2].name
        symbol_method = self._get_symbol_method(symbol_class, method_name)

        if symbol_method is None:
            return None

        firm_return = self._get_method_return_type(symbol_class, symbol_method)
        firm_params = self._get_method_parameters(symbol_class, symbol_method)

        params_used_in_call = self._deconstruct_given_parameter(3, -1)

        self._compare_parameters(firm_params, params_used_in_call)

        return firm_return

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_type()
        return self.raised_errors


class IsVoidNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_alias(self):
        return " ".join([leave.name for leave in self.node.leaves])

    def get_previous_declaration(self, name: str):
        return None

    def get_value(self) -> str | None:
        isvoid_value = self.get_value_type() == "void"
        return (str(isvoid_value)).lower()

    def get_type(self) -> str | None:
        return "Bool"

    def get_value_type(self) -> str | None:
        expr_to_evaluate = self.children[1]
        nn_expr_to_evaluate = create_noted_node(expr_to_evaluate, self.context, self.scopes, self.symbol)
        symbols_scope = self.scopes.get(self.symbol.scope)

        if nn_expr_to_evaluate is None:
            self.add_error("Invalid expression::",
                           SemanticError(
                               name="Invalid expression::",
                               details=f"isvoid operator couldn't get value from {self.children[2]}",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))
            return None

        self.extend_errors(nn_expr_to_evaluate.run_tests())
        expr_to_evaluate_type = nn_expr_to_evaluate.get_type()
        return expr_to_evaluate_type

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_value()
        return self.raised_errors


class NotOperatorNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_alias(self):
        return " ".join([leave.name for leave in self.node.leaves])

    def get_previous_declaration(self, name: str):
        return None

    def get_value(self) -> str | None:

        symbols_scope = self.scopes.get(self.symbol.scope)
        exp_to_deny = self.children[1]
        nn_exp_to_deny = create_noted_node(exp_to_deny, self.context, self.scopes, self.symbol)
        exp_type = self.get_value_type()

        if exp_type != "Bool":
            self.add_error(
                "Unable to apply not operator::",
                SemanticError(
                    name="Unable to apply not operator::",
                    details=f"not operator cannot be applied to type '{to_string_node(exp_to_deny)}'"
                            f"only Bool",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        exp_value = nn_exp_to_deny.get_value()

        if exp_value is None:
            self.add_error(
                "Unable to get value from expression::",
                SemanticError(
                    name="Unable to get value from expression::",
                    details=f"not operator couldn't get any value from '{to_string_node(exp_to_deny)}'",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        if exp_value.lower() not in ["true", "false"]:
            self.add_error(
                "Unable to get value from expression::",
                SemanticError(
                    name="Unable to get value from expression::",
                    details=f"not got unexpected value from '{to_string_node(exp_to_deny)}'"
                            f"only Bool",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        current_value = exp_value.lower()

        if current_value == "true":
            return "false"
        return "true"

    def get_type(self) -> str | None:
        return "Bool"

    def get_value_type(self) -> str | None:
        exp_to_deny = self.children[1]
        nn_exp_to_deny = create_noted_node(exp_to_deny, self.context, self.scopes, self.symbol)
        symbols_scope = self.scopes.get(self.symbol.scope)

        if nn_exp_to_deny is None:
            self.add_error(
                "Invalid expression::",
                SemanticError(
                    name="Invalid expression::",
                    details=f"not operator couldn't get valid expression from {to_string_node(exp_to_deny)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

            return None

        exp_type = nn_exp_to_deny.get_type()
        self.extend_errors(nn_exp_to_deny.run_tests())

        if exp_type is None:
            self.add_error(
                "Unable to get expression type::",
                SemanticError(
                    name="Unable to get expression type::",
                    details=f"not operator couldn't get type from expression: {to_string_node(exp_to_deny)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        return exp_type

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_value()
        return self.raised_errors


class BlockNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_alias(self):
        return to_string_node(self.node)

    def get_previous_declaration(self, name: str):
        return None

    def __get_last_item(self):
        last_exp = self.children[-2]
        nn_last_exp = create_noted_node(last_exp, self.context, self.scopes, self.symbol)
        symbols_scope = self.scopes.get(self.symbol.scope)
        if nn_last_exp is None:
            self.add_error(
                "Invalid expression::",
                SemanticError(
                    name="Invalid expression::",
                    details=f"On block cannot get proper value from last item {to_string_node(last_exp)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        return nn_last_exp

    def get_value(self) -> str | None:
        nn_last_exp = self.__get_last_item()
        if nn_last_exp is None:
            return None

        self.extend_errors(nn_last_exp.run_tests())
        return nn_last_exp.get_value()

    def get_type(self) -> str | None:
        nn_last_exp = self.__get_last_item()
        if nn_last_exp is None:
            return None
        self.extend_errors(nn_last_exp.run_tests())
        return nn_last_exp.get_type()

    def get_value_type(self) -> str | None:
        return self.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_value()
        self.get_type()

        return self.raised_errors


class BitWiseNotNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_alias(self):
        return to_string_node(self.node)

    def get_previous_declaration(self, name: str):
        return None

    def __get_nn_value_to_revert(self):
        value_to_revert = self.children[1]
        symbols_scope = self.scopes.get(self.symbol.scope)
        nn_value_to_revert = create_noted_node(value_to_revert, self.context, self.scopes, self.symbol)
        if nn_value_to_revert is None:
            self.add_error(
                "Invalid value to revert::",
                SemanticError(
                    name="Invalid value to revert::",
                    details=f"Cannot revert value from expression: {to_string_node(value_to_revert)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        self.extend_errors(nn_value_to_revert.run_tests())
        return nn_value_to_revert

    def get_value(self) -> str | None:
        symbols_scope = self.scopes.get(self.symbol.scope)
        n_type = self.get_type()

        if n_type is None:
            return None

        nn_value_to_revert = self.__get_nn_value_to_revert()

        if nn_value_to_revert is None:
            return None

        self.extend_errors(nn_value_to_revert.run_tests())
        value = nn_value_to_revert.get_value()

        if value is None:
            self.add_error(
                "Invalid value to revert::",
                SemanticError(
                    name="Invalid value to revert::",
                    details=f"Cannot revert value from expression: {to_string_node(nn_value_to_revert.node)}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None
        if value == "0":
            return value

        if value.startswith("-"):
            return value[1:]
        return f"-{value}"

    def get_type(self) -> str | None:
        symbols_scope = self.scopes.get(self.symbol.scope)
        value_to_revert_type = self.get_value_type()

        if value_to_revert_type is None:
            return None

        if value_to_revert_type != "Int":
            self.add_error(
                "Invalid type to revert::",
                SemanticError(
                    name="Invalid value to revert bw::",
                    details=f"Cannot revert ~ type: {value_to_revert_type}, only Int",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        return "Int"

    def get_value_type(self) -> str | None:
        symbols_scope = self.scopes.get(self.symbol.scope)
        nn_value_to_revert = self.__get_nn_value_to_revert()

        if nn_value_to_revert is None:
            return None

        value_to_revert_type = nn_value_to_revert.get_type()

        if value_to_revert_type is None:
            self.add_error(
                "Invalid expression to revert bw::",
                SemanticError(
                    name="Invalid expression to revert bw::",
                    details=f"Cannot revert value using ~ from expression: {to_string_node(nn_value_to_revert.node)}."
                            f"Unidentified type.",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

        return value_to_revert_type

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_value()
        return self.raised_errors


def create_noted_node(node: Node,
                      context: Dict[AnyStr, Dict[AnyStr, Symbol]],
                      scopes: Dict[AnyStr, Scope],
                      symbol: Symbol | None
                      ) -> NotedNode | None:
    index_type_node = ns.identify_node(node)

    noted_node: NotedNode | None = None

    if index_type_node == -1:
        print("UNABLE TO IDENTIFY NODE AND CREATE NOTED NODE")
        return None

    type_of_expr = ns.expressions[index_type_node]
    if type_of_expr == "assignment":  # 1
        noted_node = AssignationNotedNote(node)
    elif type_of_expr == "integer":  # 2
        noted_node = IntegerNotedNode(node)
    elif type_of_expr == "string":  # 3
        noted_node = StringNotedNote(node)
    elif type_of_expr == "boolean_true":  # 4
        noted_node = BooleanNotedNode(node)
    elif type_of_expr == "boolean_false":  # 5
        noted_node = BooleanNotedNode(node)
    elif type_of_expr == "attribute":  # 6
        noted_node = AttributeNotedNode(node)
    elif type_of_expr == "object_creation":  # 7
        noted_node = NewObjectNotedNode(node)
    elif type_of_expr == "parenthesized_expr":  # 8
        noted_node = ParenthesisNotedNode(node)
    elif type_of_expr == "dynamic_dispatch":  # 9
        noted_node = DynamicDispatchNotedNode(node)
    elif type_of_expr == "identifier":  # 10
        noted_node = IdentifierNotedNode(node)
    elif type_of_expr == "isvoid":  # 11
        noted_node = IsVoidNotedNode(node)
    elif type_of_expr == "not":  # 12
        noted_node = NotOperatorNotedNode(node)
    elif type_of_expr == "block":  # 14
        noted_node = BlockNotedNode(node)
    elif type_of_expr == "bitwise_not":  # 13
        noted_node = BitWiseNotNotedNode(node)
    elif type_of_expr == "static_dispatch":  # 15
        noted_node = StaticDispatchNotedNode(node)
    elif type_of_expr == "function_call":  # 16
        pass
    elif type_of_expr == "conditional":  # 17
        pass
    elif type_of_expr == "loop":  # 18
        pass
    elif type_of_expr == "let_in":  # 19
        pass

    elif type_of_expr == "arithmetic_or_comparison":  # 20
        pass

    else:
        print(f"Unrecognized expression: {type_of_expr}")

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

def search_class_symbol(class_name, scopes):
    global_scope = scopes.get("global")
    classes = global_scope.get_all_classees()
    if class_name in classes:
        return classes[class_name]
    return None

def verify_inheritance(parent_class: str, child_class: str, scopes: Dict[AnyStr, Scope]) -> bool:
    return verify_matching_type(parent_class, child_class, scopes)


def verify_existing_class(class_name: str, scopes: Dict[AnyStr, Scope]):
    global_scope = scopes.get("global")
    return class_name in global_scope.get_all_classees()


def verify_existing_type(type_name: str, scopes: Dict[AnyStr, Scope]) -> bool:
    basic_types = ["Int", "String", "Bool", "Object", "IO"]

    if type_name in basic_types:
        return True

    # It's a created class
    return verify_existing_class(type_name, scopes)


def verify_matching_type(expected_type: str, received_type: str, scopes: Dict[AnyStr, Scope]) -> bool:
    if expected_type == received_type:
        return True

    if not verify_existing_type(expected_type, scopes) or not verify_existing_type(received_type, scopes):
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

    return False


def get_symbol_class(class_name, scopes: Dict[AnyStr, Scope]) -> Symbol | None:
    global_scope = scopes.get("global")
    classes = global_scope.get_all_classees()
    if class_name not in classes:
        return None

    return classes.get(class_name)


def get_symbol_method(method_name: str, class_symbol: Symbol, scopes: Dict[AnyStr, Scope]) -> Symbol | None:
    scope_name = class_symbol.construct_scope_name()

    if scope_name not in scopes:
        return None

    class_scope: Scope = scopes.get(scope_name)
    methods = class_scope.get_all_methods()

    if method_name not in methods:
        return None

    return methods.get(method_name)


def add_error_to_local(local_errors: Dict[AnyStr, List[SemanticError]], error_type: str, error: SemanticError):
    if error_type in local_errors:
        if error not in local_errors[error_type]:
            local_errors[error_type].append(error)
    else:
        local_errors[error_type] = [error]

    return local_errors


def merge_errors(local_errors: Dict[AnyStr, List[SemanticError]], other_errors: Dict[AnyStr, List[SemanticError]]) -> \
        Dict[AnyStr, SemanticError]:
    for err_type, errors in other_errors.items():
        for error in errors:
            local_errors = add_error_to_local(local_errors, err_type, error)

    return local_errors


def to_string_node(exp: Node) -> str:
    return "".join([leave.name for leave in exp.leaves])



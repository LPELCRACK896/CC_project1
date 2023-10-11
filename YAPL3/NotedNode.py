from abc import abstractmethod
from typing import Dict, AnyStr, List, Tuple

from Symbol import Symbol
from anytree import Node
from Scope import Scope
from SemanticCommon import SemanticError

from IThreeDirectionsCode import IThreeDirectionsCode
from Direction import Direction
from Register import Register
from Operation import Operation

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
    name: str

    needs_symbol: bool
    needs_context: bool
    need_scopes: bool

    scopes: Dict[AnyStr, Scope] | None = None
    symbol: Symbol | None = None
    context: Dict[AnyStr, Dict[AnyStr, Symbol]] | None = None

    symbols_scope: Scope

    raised_errors: Dict[AnyStr, List[SemanticError]]

    def __init__(self, node: Node):
        self.node = node
        self.node_type = node.name
        self.children = node.children
        self.needs_context = False
        self.need_scopes = False
        self.needs_symbol = False
        self.raised_errors = {}

    def __try_to_initialize_symbol_scope(self):
        if self.scopes is not None and self.symbol is not None:
            self.symbols_scope = self.scopes.get(self.symbol.scope)

    def add_context(self, context: Dict[AnyStr, Dict[AnyStr, Symbol]]):
        self.context = context

    def add_scopes(self, scopes: Dict[AnyStr, Scope]):
        self.scopes = scopes
        self.__try_to_initialize_symbol_scope()

    def add_symbol(self, symbol):
        self.symbol = symbol
        self.__try_to_initialize_symbol_scope()

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

    def _create_sub_noted_node(self, node: Node, symbol: Symbol):
        symbols_scope = self.scopes.get(symbol.scope)

        nn_node = create_noted_node(node, self.context, self.scopes, symbol)

        if nn_node is None:
            self.add_error("Invalid expression::",
                           SemanticError(
                               name="Invalid expression::",
                               details=f"f{self.name} was unable to get expression from {to_string_node(node)}",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))
            return None

        self.extend_errors(nn_node.run_tests())
        return nn_node

    def _type_verifier(self, typo_received):
        valid_type = verify_existing_type(typo_received, self.scopes)
        if not valid_type:
            symbols_scope = self.scopes.get(self.symbol.scope)
            self.add_error(
                "Un-existing type::",
                SemanticError(
                    name="Un-existing type::",
                    details=f"On {self.name} got un-existing type: {typo_received}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        return valid_type

    def get_default_value_from_typo(self):
        typo = self.get_type()
        if typo == "Int":
            return "0"
        elif typo == "Bool":
            return "false"
        elif typo == "String":
            return ""

        return None

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

    def _get_variable_declaration(self, variable_name):
        variable_declaration = search_declaration(variable_name, self.symbol, self.scopes, "variable")

        if variable_declaration is None:
            self.add_error("Undeclared variable::",
                           SemanticError(
                               name="Undeclared variable::",
                               details=f"{self.name} tried to use undeclared variable {variable_name}",
                               symbol=self.symbol,
                               scope=self.symbols_scope,
                               line=self.symbol.start_line
                           ))

        return variable_declaration

    def _get_method_declaration(self, method_name) -> Symbol | None:
        method_declaration = search_declaration(method_name, self.symbol, self.scopes, "method")

        if method_declaration is None:
            self.add_error("Undeclared method::",
                           SemanticError(
                               name="Undeclared variable::",
                               details=f"{self.name} tried to use inaccessible method {method_name}",
                               symbol=self.symbol,
                               scope=self.symbols_scope,
                               line=self.symbol.start_line
                           ))

        return method_declaration

    @abstractmethod
    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        pass

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
        self.need_scopes = True

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        if must_create_register:
            next_tag = f"L{tdc.get_next_label_count()}"
            direction = Direction(self.get_value(), self.scopes)

            register = Register(next_tag, direction)

            operation = Operation(None)
            register.set_first_operation(operation)

            tdc.add_register(register)

        return self.get_value()

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
        self.name = "Integer value"

    def get_type(self) -> str | None:
        return "Int"

    def get_value_type(self) -> str | None:
        return "Int"


class StringNotedNote(BasicNotedNode):

    def __init__(self, node: Node):
        super().__init__(node)
        self.name = "String value"

    def get_type(self) -> str | None:
        return "String"

    def get_value_type(self) -> str | None:
        return "String"


class BooleanNotedNode(BasicNotedNode):

    def __init__(self, node: Node):
        super().__init__(node)
        self.name = "Boolean value"

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
        self.name = "Assignation"

    def tdc_create_sub_register(self, tdc: IThreeDirectionsCode, tag: AnyStr, symbol_direction: Direction,
                                value_direction: Direction) -> AnyStr:

        temp_var = tdc.get_next_temp_variable()

        first_direction = Direction(temp_var, self.scopes)
        first_operation = Operation("=")
        second_direction = symbol_direction
        second_operation = Operation("assign")
        third_direction = value_direction

        register = Register(tag, first_direction)

        register.set_first_operation(first_operation)
        register.set_second_direction(second_direction)

        register.set_second_operation(second_operation)
        register.set_third_direction(third_direction)

        tdc.add_register(register)

        return temp_var

    @staticmethod
    def tdc_create_main_register(tdc: IThreeDirectionsCode, tag: AnyStr, symbol_direction: Direction,
                                 value_direction: Direction):
        first_direction = symbol_direction
        first_operation = Operation("assign")
        second_direction = value_direction

        register = Register(tag, first_direction)

        register.set_first_operation(first_operation)
        register.set_second_direction(second_direction)

        tdc.add_register(register)

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        symbol_declaration: Symbol = self.get_previous_declaration(self.get_alias())
        symbol_direction_str: AnyStr = symbol_declaration.as_direction_stringify()

        value_assigned: Node = self.children[2]
        noted_node_value_assigned: NotedNode = self._create_sub_noted_node(value_assigned, self.symbol)

        value_direction_str = noted_node_value_assigned.get_three_direction_code(tdc, 1, False)

        tag = f"L{tdc.get_next_label_count()}"
        symbol_direction = Direction(symbol_direction_str, self.scopes)
        value_direction = Direction(value_direction_str, self.scopes)

        if num_directions_available != 3:
            temporary_var = self.tdc_create_sub_register(tdc, tag, symbol_direction, value_direction)
            return temporary_var

        self.tdc_create_main_register(tdc, tag, symbol_direction, value_direction)
        return ""





        pass
        #print(name_local)

    def get_previous_declaration(self, symbol_name: str):
        return self._get_variable_declaration(symbol_name)

    def get_type(self) -> str | None:

        attr_name = self.get_alias()

        symbol_declaration = self._get_variable_declaration(attr_name)

        if symbol_declaration is None:
            return None

        nn_declaration = self._create_sub_noted_node(symbol_declaration.node, symbol_declaration)

        if nn_declaration is None:
            return None

        return nn_declaration.get_type()

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
        return self.children[0].name

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
        self.name = "Attribute"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

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

        value = self.get_value()
        var_value_type = self.get_value_type()
        var_expected_type = self.get_type()

        if var_value_type is not None and var_expected_type is not None:
            coherent_types = verify_matching_type(var_expected_type, var_value_type, self.scopes)
            if not coherent_types:
                if var_value_type == "Int" and var_expected_type == "Bool":
                    value = int(value)
                    if value != 0 and value != 1:
                        self.add_error("Incoherence types::",
                                SemanticError(
                                    name="Incoherence types::",
                                    details=f"On attribute assignation expected type {var_expected_type}"
                                            f" does not match the received type {var_value_type} and not posible to cast",
                                    symbol=self.symbol,
                                    scope=symbols_scope,
                                    line=self.symbol.start_line
                                ))    
                else:
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
        self.name = "Object creation"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):

        instance = self.get_type()
        tag = f"L{tdc.get_next_label_count()}"

        class_reference_direction = Direction(instance, self.scopes)
        create_operation = Operation("NEW")

        if not must_create_register:  # Is being called from other, so it needs temporary_variable
            temporary_variable = tdc.get_next_temp_variable()

            temporary_variable_direction = Direction(temporary_variable, self.scopes)

            first_operation = Operation("=")

            register: Register = Register(tag, temporary_variable_direction)

            register.set_first_operation(first_operation)
            register.set_second_operation(create_operation)
            register.set_second_direction(class_reference_direction)
            tdc.add_register(register)

            return temporary_variable

        register: Register = Register(tag, class_reference_direction)
        register.set_first_operation(create_operation)
        tdc.add_register(register)
        return ""

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
        return global_scope.get_all_classes().get(name)

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
        self.name = "Parenthesis expression"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return self.__get_contained_nn().get_three_direction_code(tdc, num_directions_available, must_create_register)

    def get_previous_declaration(self, name: str):
        return None

    def get_alias(self):
        return to_string_node(self.node)

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
        return self.get_default_value_from_typo()

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
        self.name = "Identifier"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        symbol_declaration: Symbol = self.get_previous_declaration(self.get_alias())

        symbol_direction = Direction(symbol_declaration.as_direction_stringify(), self.scopes)

        if must_create_register:
            next_tag = f"L{tdc.get_next_label_count()}"

            register = Register(next_tag, symbol_direction)

            operation = Operation(None)
            register.set_first_operation(operation)

            tdc.add_register(register)

        return symbol_declaration.as_direction_stringify()

    def get_previous_declaration(self, name: str):
        symbols_scope = self.scopes.get(self.symbol.scope)
        result = search_symbol_by_name(symbols_scope, name)
        declaration = search_declaration(name, self.symbol, self.scopes, "variable")
        if declaration is None:
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

        return declaration

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
                    details=f"On method call, can't find method referenced called {method_name} of {symbol_class.name}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        return symbol_method

    def _get_method_parameters(self, symbol_class: Symbol, symbol_method: Symbol):
        self_type = symbol_class.name

        parameters = symbol_method.parameters

        updated_parameters = []

        for parameter_name, parameter_type in parameters:
            updated_parameter_type = parameter_type if parameter_type.upper() != "SELF_TYPE" else self_type
            self._type_verifier(updated_parameter_type)
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
                    details=f"Method call cannot get proper parameter from ({parameter_position + 1})"
                            f" from expression {to_string_node(received_parameter)}. Expected type {firm_param_type} "
                            f"for param '{firm_param_name}' (No. {parameter_position + 1})",
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

    def _deconstruct_given_parameters(self, position_open_parenthesis: int, position_closing_parenthesis: int):
        parenthesis_content = self.children[position_open_parenthesis + 1:position_closing_parenthesis]
        return [item for item in parenthesis_content if item.name != ","]

    def get_alias(self):
        return to_string_node(self.node)

    def get_value_type(self) -> str | None:
        return self.get_type()

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
    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        pass


class DynamicDispatchNotedNode(DispatchNotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True
        self.name = "Parent call method"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

    def get_alias(self):
        return to_string_node(self.node)

    def get_previous_declaration(self, name: str):
        return None

    def get_value(self) -> str | None:
        return self.get_default_value_from_typo()

    def _exist_type(self, type_name):
        symbols_scope = self.scopes.get(self.symbol.scope)
        do_exist_type = verify_existing_type(type_name, self.scopes)
        if not do_exist_type:
            self.add_error(
                "In-existing class::",
                SemanticError(
                    name="In-existing class::",
                    details=f"On method call, references in-existing class: {type_name}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        return do_exist_type

    def verifies_inheritance(self, parent_name, child_name):
        is_valid_inheritance = verify_inheritance(parent_name, child_name, self.scopes)
        if not is_valid_inheritance:
            symbols_scope = self.scopes.get(self.symbol.scope)
            self.add_error("Invalid inheritance relation::",
                           SemanticError(
                               name="Invalid inheritance relation::",
                               details=f"@ method call found no valid relation between {parent_name}, {child_name}."
                                       f". {child_name} should inherits directly or indirectly from {parent_name}",
                               symbol=self.symbol,
                               scope=symbols_scope,
                               line=self.symbol.start_line
                           ))
        return is_valid_inheritance

    def get_type(self) -> str | None:
        instance_expr = self.children[0]
        instance = self._get_instance(instance_expr)

        if instance is None:
            return None

        child_name_type = instance.get_type()
        if child_name_type is None:
            return None

        parent_name_type = self.children[2].name

        parent_ref_exist = self._exist_type(parent_name_type)
        child_ref_exist = self._exist_type(child_name_type)
        if not (parent_ref_exist and child_ref_exist):
            return None

        if not self.verifies_inheritance(parent_name_type, child_name_type):
            return None

        symbol_parent_class = get_symbol_class(parent_name_type, self.scopes)
        if symbol_parent_class is None:
            return None
        method_name = self.children[4].name
        symbol_method = self._get_symbol_method(symbol_parent_class, method_name)

        if symbol_method is None:
            return None

        firm_return = self._get_method_return_type(symbol_parent_class, symbol_method)
        firm_params = self._get_method_parameters(symbol_parent_class, symbol_method)

        params_used_in_call = self._deconstruct_given_parameters(5, -1)

        self._compare_parameters(firm_params, params_used_in_call)

        return firm_return

    def get_value_type(self) -> str | None:
        return self.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_type()
        return self.raised_errors


class StaticDispatchNotedNode(DispatchNotedNode):
    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True
        self.name = "Object call method"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

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

        params_used_in_call = self._deconstruct_given_parameters(3, -1)

        self._compare_parameters(firm_params, params_used_in_call)

        return firm_return

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_type()
        return self.raised_errors


class FunctionCallDispatchNotedNode(DispatchNotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True
        self.name = "Local method call"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

    def get_previous_declaration(self, name: str):
        return None

    def __get_current_class_symbol(self):
        symbols_scope = self.scopes.get(self.symbol.scope)

        symbol_class = get_class_symbol(self.symbol, self.scopes)

        if symbol_class is None:
            method_name = self.children[0].name
            self.add_error(
                "Local method call out any class::",
                SemanticError(
                    name="Local method call out any class::",
                    details=f"Local method call {method_name} is being called from out of any class",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        return symbol_class

    def get_value(self) -> str | None:
        return self.get_default_value_from_typo()

    def get_type(self) -> str | None:

        method_name = self.children[0].name

        symbol_class = self.__get_current_class_symbol()

        if symbol_class is None:
            return None

        symbol_method = self._get_symbol_method(symbol_class, method_name)

        if symbol_method is None:
            return None

        firm_return = self._get_method_return_type(symbol_class, symbol_method)
        firm_params = self._get_method_parameters(symbol_class, symbol_method)

        params_used_in_call = self._deconstruct_given_parameters(1, -1)

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
        self.name = "isvoid operation"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

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

        self.name = "'not' operation"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

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
        self.name = "Block"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

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
        self.name = "Bitwise operation (~)"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

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


class NoContentNoTypeNoteNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)

    def get_alias(self):
        to_string_node(self.node)

    def get_previous_declaration(self, name: str):
        return None

    def get_value(self) -> str | None:
        return None

    def get_type(self) -> str | None:
        return "void"

    def get_value_type(self) -> str | None:
        return "void"

    @abstractmethod
    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        pass


class ConditionNotedNode(NoContentNoTypeNoteNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def is_valid_condition(self, node: Node):
        nn_condition = self._create_sub_noted_node(node, self.symbol)

        if nn_condition is None:
            return None

        nn_condition_type = nn_condition.get_type()
        if nn_condition_type is None:
            return None

        is_valid_condition = nn_condition_type == "Bool"

        if not is_valid_condition:
            self.add_error(
                "Inappropriate expression as condition::",
                SemanticError(
                    name="Inappropriate expression as condition::",
                    details=f"Condition ({self.name}) must have bool type. Cannot get bool from: {to_string_node(node)}.",
                    symbol=self.symbol,
                    scope=self.symbols_scope,
                    line=self.symbol.start_line
                )
            )

        return is_valid_condition

    @abstractmethod
    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        pass


class IfConditionalNotedNode(ConditionNotedNode):
    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True
        self.name = "if condition"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        condition_node = self.children[1]
        self.is_valid_condition(condition_node)
        return self.raised_errors


class LoopNotedNode(ConditionNotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.name = "while loop"

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        condition_node = self.children[1]
        self.is_valid_condition(condition_node)
        return self.raised_errors


class LetNotedNode(NoContentNoTypeNoteNode):
    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        return self.raised_errors


class ArithmeticLogicNotedNode(NotedNode):
    arithmetic_operators: list = ['+', '-', '*', '/']
    comparer_operators: list = ['<', '<=', '=', '>=', '>']
    type_of_operation: str
    operation: str

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

        self.operation = self.children[1].name

        self.type_of_operation = "arithmetic" if self.operation in self.arithmetic_operators else "comparer"

    def get_alias(self):
        return to_string_node(self.node)

    def get_previous_declaration(self, name: str):
        return None

    def create_item_node(self, item_node: Node):
        symbols_scope = self.scopes.get(self.symbol.scope)

        nn_item = create_noted_node(item_node, self.context, self.scopes, self.symbol)
        if nn_item is None:
            self.add_error(
                "Unable to get valid expression::",
                SemanticError(
                    name="Unable to get valid expression::",
                    details=f"Cannot get proper expr in arithmetic or logical operation from: {to_string_node(item_node)}.",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        self.extend_errors(nn_item.run_tests())
        return nn_item

    def get_item_value(self, nn_item: NotedNode):
        symbols_scope = self.scopes.get(self.symbol.scope)

        item_type = self.get_item_type(nn_item)

        if item_type is None:
            return None

        item_value = nn_item.get_value()
        if item_value is None:
            self.add_error(
                "Unable to get value::",
                SemanticError(
                    name="Unable to get value::",
                    details=f"Can't get value from: {to_string_node(nn_item.node)}.",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

        return item_value

    def get_item_type(self, nn_item: NotedNode):
        symbols_scope = self.scopes.get(self.symbol.scope)

        item_type = nn_item.get_type()

        if item_type is None:
            self.add_error(
                "Unable to get type::",
                SemanticError(
                    name="Unable to get type::",
                    details=f"Can't get type from: {to_string_node(nn_item.node)}.",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        if item_type != "Int":
            self.add_error(
                "Invalid type in operations::",
                SemanticError(
                    name="Invalid type in operations::",
                    details=f"Cannot use the operator {self.operation} with type: {item_type}. Only Int",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        return item_type

    def operate(self, item_1_value, item_2_value):
        symbols_scope = self.scopes.get(self.symbol.scope)

        if self.type_of_operation == "arithmetic":
            if self.operation == "+":
                return str(int(item_1_value) + int(item_2_value))
            elif self.operation == "*":
                return str(int(int(item_1_value) * int(item_2_value)))
            elif self.operation == "-":
                return str(int(item_1_value) - int(item_2_value))
            elif self.operation == "/":
                divisor = int(item_2_value)
                if divisor == 0:
                    self.add_error(
                        "Zero division::",
                        SemanticError(
                            name="Zero division::",
                            details=f"Operation {item_1_value}/{item_2_value}, goes into a division by zero",
                            symbol=self.symbol,
                            scope=symbols_scope,
                            line=self.symbol.start_line
                        )
                    )
                    return None
                return str(int(int(item_1_value) / int(item_2_value)))

        #  Order
        if self.operation == "=":
            return (str(int(item_1_value) == int(item_2_value))).lower()
        elif self.operation == "<=":
            return (str(int(item_1_value) <= int(item_2_value))).lower()
        elif self.operation == ">=":
            return (str(int(item_1_value) >= int(item_2_value))).lower()
        elif self.operation == ">":
            return (str(int(item_1_value) > int(item_2_value))).lower()
        elif self.operation == "<":
            return (str(int(item_1_value) < int(item_2_value))).lower()

    def get_value(self) -> str | None:
        item_1 = self.children[0]
        item_2 = self.children[-1]

        nn_item_1 = self.create_item_node(item_1)
        nn_item_2 = self.create_item_node(item_2)

        if nn_item_1 is None or nn_item_2 is None:
            return None

        item_1_value = self.get_item_value(nn_item_1)
        item_2_value = self.get_item_value(nn_item_2)

        if item_1_value is None or item_2_value is None:
            return None

        result = self.operate(item_1_value, item_2_value)

        return result

    def get_type(self) -> str | None:
        value = self.get_value()

        if value is None:
            return None

        if self.type_of_operation == "comparer":
            return "Bool"

        return "Int"

    def get_value_type(self) -> str | None:
        return self.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_value()
        return self.raised_errors


class ReturnStatementNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True
        self.name = "Return statement"

    def get_alias(self):
        return to_string_node(self.node)

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

    def __get_get_symbol_class(self):
        scope_name = self.symbol.scope

        symbols_scope = self.scopes.get(scope_name)

        scope_parts = scope_name.split("-")
        class_name = scope_parts[-2]

        method_name = scope_parts[-1]

        if not class_name.endswith("(class)"):
            self.add_error(
                "Method out of class::",
                SemanticError(
                    name="Method out of class::",
                    details=f"Method {method_name} was found out of class scope, and found {class_name} instead",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        class_name = class_name.split(maxsplit=1, sep="(", )[0]
        symbol_class = get_symbol_class(class_name, self.scopes)

        if symbol_class is None:
            self.add_error(
                "Class unfounded::",
                SemanticError(
                    name="Class unfounded::",
                    details=f"Class {class_name} wasn't reference can't be found",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
        return symbol_class

    def __from_scope_gets_symbol_method(self):
        scope_name = self.symbol.scope
        symbols_scope = self.scopes.get(scope_name)

        scope_parts = scope_name.split("-")

        method_name = scope_parts[-1]
        class_name = scope_parts[-2]

        if not method_name.endswith("(method)"):
            self.add_error(
                "Return statement out of method::",
                SemanticError(
                    name="Return statement out of method::",
                    details=f"Return statement {self.get_alias()} found out of method: {scope_name}",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )
            return None

        method_name = method_name.split(maxsplit=1, sep="(", )[0]

        symbol_class = self.__get_get_symbol_class()

        if symbol_class is None:
            return None

        symbol_method = get_symbol_method(method_name, symbol_class, self.scopes)

        if symbol_method is None:
            self.add_error(
                "Unfounded method::",
                SemanticError(
                    name="Unfounded method::",
                    details=f"Method {method_name} couldn't be found in {class_name}.",
                    symbol=self.symbol,
                    scope=symbols_scope,
                    line=self.symbol.start_line
                )
            )

        return symbol_method

    def __get_value_and_type(self) -> Tuple[AnyStr, AnyStr] | Tuple[None, None]:
        return_exp = self.children[1]

        nn_return_exp = self._create_sub_noted_node(return_exp, self.symbol)

        if nn_return_exp is None:
            return None, None

        return nn_return_exp.get_value(), nn_return_exp.get_type()

    def verify_firm_return(self) -> None | bool:

        symbol_class = self.__get_get_symbol_class()

        if symbol_class is None:
            return None

        symbol_method = self.__from_scope_gets_symbol_method()

        if symbol_method is None:
            return None

        firm_return_type = self._get_method_return_type(symbol_class, symbol_method)

        if firm_return_type is None:
            return None

        return_type = self.get_type()

        if return_type is None:
            return None

        is_valid = verify_matching_type(firm_return_type, return_type, self.scopes)

        return is_valid

    def get_previous_declaration(self, name: str):
        return None

    def get_value(self) -> str | None:
        return self.__get_value_and_type()[0]

    def get_type(self) -> str | None:
        return self.__get_value_and_type()[1]

    def get_value_type(self) -> str | None:
        return self.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.verify_firm_return()

        return self.raised_errors


class MethodNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True
        self.name = "Method firm"

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

    def get_alias(self):
        return to_string_node(self.children[0])

    def get_previous_declaration(self, name: str):
        return None

    def get_value(self) -> str | None:
        return self.get_default_value_from_typo()

    def get_type(self) -> str | None:
        typo_received = to_string_node(self.children[5])

        if not self._type_verifier(typo_received):
            return None

        return typo_received

    def get_value_type(self) -> str | None:
        return self.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_type()
        return self.raised_errors


class FormalNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    """
    NO NEED IMPLEMENTATION
    """
    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

    def get_alias(self):
        return to_string_node(self.children[0])

    def get_previous_declaration(self, name: str):
        return self.symbol

    def get_value(self) -> str | None:
        return self.get_default_value_from_typo()

    def get_type(self) -> str | None:
        typo_received = to_string_node(self.children[2])

        if not self._type_verifier(typo_received):
            return None

        return typo_received

    def get_value_type(self) -> str | None:
        return self.get_type()

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.get_type()
        return self.raised_errors


class LetVariableNotedNode(NotedNode):

    def __init__(self, node):
        super().__init__(node)
        self.needs_symbol = True
        self.need_scopes = True
        self.needs_context = True

    def get_three_direction_code(self, tdc: IThreeDirectionsCode, num_directions_available: int,
                                 must_create_register=True):
        return "NI"

    def get_alias(self):
        pass

    def get_previous_declaration(self, name: str):
        pass

    def get_value(self) -> str | None:
        if len(self.children)<3:
            return self.get_default_value_from_typo()
        value_node = self._create_sub_noted_node(self.children[2], self.symbol)
        if value_node is None:
            return None
        return value_node.get_value()

    def get_type(self) -> str | None:
        typo = to_string_node(self.children[1])
        if not self._type_verifier(typo):
            return None
        return to_string_node(self.children[1])

    def get_value_type(self) -> str | None:
        if len(self.children)<3:
            return self.get_type()

        value_node = self._create_sub_noted_node(self.children[2], self.symbol)
        if value_node is None:
            return None

        typo = value_node.get_type()
        if not self._type_verifier(typo):
            return None

        return typo

    def test_type_coherence(self):
        if len(self.children)<3:
            return
        expected_type = self.get_type()
        received_type = self.get_value_type()

        if expected_type is None or received_type is None:
            return

        if not verify_matching_type(expected_type, received_type, self.scopes):
            self.add_error(
                "Un-matching types::",
                SemanticError(
                    name="Un-matching types::",
                    details=f"Variable declaration was expecting {expected_type}(or equivalent)"
                            f" but got {received_type} instead.",
                    symbol=self.symbol,
                    scope=self.symbols_scope,
                    line=self.symbol.start_line
                )
            )
        return

    def run_tests(self) -> Dict[AnyStr, List[SemanticError]]:
        self.test_type_coherence()
        return self.raised_errors


def create_noted_node(node: Node,
                      context: Dict[AnyStr, Dict[AnyStr, Symbol]],
                      scopes: Dict[AnyStr, Scope],
                      symbol: Symbol | None
                      ) -> NotedNode | None:
    index_type_node = ns.identify_node(node)

    noted_node: NotedNode | None = None

    if index_type_node == -1:
        return None

    type_of_expr = ns.expressions[index_type_node]
    if type_of_expr == "assignment":  # 1
        noted_node = AssignationNotedNote(node)  # TDC -> IMPLEMENTED
    elif type_of_expr == "integer":  # 2
        noted_node = IntegerNotedNode(node)  # TDC -> IMPLEMENTED
    elif type_of_expr == "string":  # 3
        noted_node = StringNotedNote(node)  # TDC -> IMPLEMENTED
    elif type_of_expr == "boolean_true":
        noted_node = BooleanNotedNode(node)  # TDC -> IMPLEMENTED
    elif type_of_expr == "boolean_false":
        noted_node = BooleanNotedNode(node)  # TDC -> IMPLEMENTED
    elif type_of_expr == "attribute":
        noted_node = AttributeNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "object_creation":
        noted_node = NewObjectNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "parenthesized_expr":
        noted_node = ParenthesisNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "dynamic_dispatch":
        noted_node = DynamicDispatchNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "identifier":
        noted_node = IdentifierNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "isvoid":
        noted_node = IsVoidNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "not":
        noted_node = NotOperatorNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "block":
        noted_node = BlockNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "bitwise_not":
        noted_node = BitWiseNotNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "static_dispatch":
        noted_node = StaticDispatchNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "function_call":
        noted_node = FunctionCallDispatchNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "conditional":
        noted_node = IfConditionalNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "loop":
        noted_node = LoopNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "let_in":
        noted_node = LetNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "arithmetic_or_comparison":
        noted_node = ArithmeticLogicNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "func_return":
        noted_node = ReturnStatementNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "method":
        noted_node = MethodNotedNode(node)  # TDC -> UNIMPLEMENTED
    elif type_of_expr == "formal":
        noted_node = FormalNotedNode(node)  # TDC -> DONE
    elif type_of_expr == "declaration_assignation":
        noted_node = LetVariableNotedNode(node)
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


def search_declaration(identifier: str,
                       starting_point_symbol: Symbol,
                       scopes: Dict[AnyStr, Scope],
                       semantic_type_target: str = "variable"):

    symbols_scope = scopes.get(starting_point_symbol.scope)
    # Local results
    variables = symbols_scope.get_declarations(semantic_type_target)

    if identifier in variables:
        return variables[identifier]

    # Check parent attributes
    symbol_class = get_class_symbol(starting_point_symbol, scopes)

    if symbol_class is None:
        return None

    next_class = symbol_class
    declaration = None

    while next_class is not None and declaration is None:
        scope_id = next_class.construct_scope_name()
        if scope_id in scopes:
            class_scope = scopes.get(scope_id)
            class_attributes = class_scope.get_declarations(semantic_type_target)
            if identifier in class_attributes:
                declaration = class_attributes[identifier]
            else:
                next_class = next_class.data_type
                if next_class is not None:
                    next_class = get_symbol_class(next_class, scopes)
        else:
            next_class = None

    return declaration


def get_class_symbol(starting_point_symbol: Symbol, scopes: Dict[AnyStr, Scope]) -> Symbol | None:
    symbols_scope = scopes.get(starting_point_symbol.scope)
    scope_id = symbols_scope.scope_id

    scopes_name = scope_id.split("-")
    scopes_name.reverse()

    item_scope = ""
    found_class_scope_id = False
    while len(scopes_name) != 0 and not found_class_scope_id:
        item_scope = scopes_name.pop(0)
        found_class_scope_id = item_scope.endswith("(class)")

    if not found_class_scope_id:
        return None

    class_name = item_scope.split(maxsplit=1, sep="(")[0]
    symbol_class = get_symbol_class(class_name, scopes)

    return symbol_class


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
    classes = global_scope.get_all_classes()
    if class_name in classes:
        return classes[class_name]
    return None


def verify_inheritance(parent_class: str, child_class: str, scopes: Dict[AnyStr, Scope]) -> bool:
    return verify_matching_type(parent_class, child_class, scopes)


def verify_existing_class(class_name: str, scopes: Dict[AnyStr, Scope]):
    global_scope = scopes.get("global")
    classes = global_scope.get_all_classes()
    return class_name in classes


def verify_existing_type(type_name: str, scopes: Dict[AnyStr, Scope]) -> bool:
    basic_types = ["Int", "String", "Bool", "Object", "IO"]

    if type_name in basic_types:
        return True

    # It's a created class
    return verify_existing_class(type_name, scopes)


def verify_matching_type(expected_type: str, received_type: str, scopes: Dict[AnyStr, Scope]) -> bool:
    if expected_type == received_type or expected_type=="Object":
        return True

    if not (verify_existing_type(expected_type, scopes) and verify_existing_type(received_type, scopes)):
        return False

    global_scope = scopes.get("global")
    classes = global_scope.get_all_classes()

    current_class = received_type
    equivalent_classes = ["Object"]

    while current_class != "Object":
        equivalent_classes.append(current_class)
        current_class_symbol: Symbol = classes.get(current_class)
        if current_class_symbol is None:
            current_class = "Object"  # Jumps to object in case there is no valid parent
        else:
            current_class = current_class_symbol.data_type

    if expected_type in equivalent_classes:
        return True

    return False


def get_symbol_class(class_name, scopes: Dict[AnyStr, Scope]) -> Symbol | None:
    global_scope = scopes.get("global")
    classes = global_scope.get_all_classes()
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


def to_string_node(exp: Node) -> str:
    return "".join([leave.name for leave in exp.leaves])

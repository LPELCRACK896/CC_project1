from dataclasses import dataclass, field
from collections import defaultdict
from prettytable import PrettyTable
from typing import List, Dict, AnyStr
from anytree import Node
from NotedNode import NotedNode
from Symbol import Symbol
from Scope import Scope
from SemanticCommon import *
from typing import List, Dict
from ThreeDirectionsCode import ThreeDirectionsCode, Register, Direction

import node_structures as ns
from NotedNode import create_noted_node


class SymbolTable:

    sequential_symbols: List[Symbol]
    def __init__(self, root):
        """Método constructor

        Args:
            root (anytree.Node): Nodo raiz del árbol de análisis sintáctico generado por anytree para la gramática. 
        """
        self.content = defaultdict(dict)   # {<scope_id>: {symbol_name: Symbol}} >>  Diccionario con clave el id_scope y valor un diccionario con simbolos (diccionario interno, identificador de simbolo como clave; Objeto Simbolo como valor)
        self.construction_errors: Dict[str: List[SemanticError]] = {}
        self.global_scope = Scope(parent=None,
                                  scope_id="global")  # La tabla de simbolos de inicializa con un scope global en el que se almacenan simbolos que no esten debajo de otros scopes creados.
        self.scopes = {"global": self.global_scope}  # {<scope_id>: Scope} >> Scopes de la tabla almacenados en dicionarios que tiene por clave su identificador y su objeto por valor.
        self.sequential_symbols = []

        self.build_symbol_table(node=root, current_scope=self.global_scope,
                                current_line=self.__build_basic_classes())  # Construye recursivamente la tabla de simbolos

        pass

    def __str__(self) -> str:
        """Crea una version bonita y para consola de la tabla. 

        Returns:
            str: Tabla estetica. 
        """
        table = PrettyTable()
        table.field_names = ["Scope", "Name", "Semantic Type", "Value", "Memory bytes", "Data node_type", "S.Index",
                             "E.Index", "S.Line", "E.Line", "Exp. Type"]
        for scope_id, symbols in self.content.items():
            for symbol_name, symbol in symbols.items():
                table.add_row([scope_id, symbol_name, symbol.semantic_type,
                               self.get_expression_to_str(symbol.value) if symbol.value else symbol.value,
                               symbol.bytes_memory_size, symbol.data_type, symbol.start_index, symbol.end_index,
                               symbol.start_line, symbol.end_line, symbol.type_of_expression])
        return str(table)

    def to_string_sequential_symbols(self) -> str:
        table = PrettyTable()
        table.field_names = ["Scope", "Name", "Semantic Type", "Value", "Memory bytes", "Data node_type", "S.Index",
                             "E.Index", "S.Line", "E.Line", "Exp. Type"]
        for symbol in self.sequential_symbols:
            table.add_row([symbol.scope, symbol.name, symbol.semantic_type,
                           self.get_expression_to_str(symbol.value) if symbol.value else symbol.value,
                           symbol.bytes_memory_size, symbol.data_type, symbol.start_index, symbol.end_index,
                           symbol.start_line, symbol.end_line, symbol.type_of_expression])

        return str(table)

    """
    START
    BUILDERS
    """
    def build_symbol_table(self, node, current_scope=None, current_line=0) -> int:
        """Construye la tabla de simbolos. Al encontrar metodos o clases inicializa Scopes y llama recursivamente sobre los hijos de ese nodo.

        Args:
            node (anytree.Node): Nodo el cual se deasea ubicar en tabla de simbolos.
            current_scope (scope_actual, optional): En el cual se desea estableceer el nodo. Defaults to None.
        """

        if node.name == "program":

            for child in node.children:
                current_line = self.build_symbol_table(child, current_scope, current_line + 1)
            return current_line

        if node.name == "classDef":
            current_line = self.build_symbol_class(node=node, current_scope=current_scope,
                                                   current_line=current_line + 1)
            return current_line

        if node.name == "method":
            current_line = self.build_symbol_method(node, current_scope, current_line + 1)
            return current_line

        if node.name == "attr":
            current_line = self.build_symbol_attribute(node, current_scope, current_line + 1)
            return current_line

        if node.name == "func_return":
            current_line = self.build_symbol_return(node=node, current_scope=current_scope,
                                                    current_line=current_line + 1)
            return current_line

        if node.name == "formals":
            current_line = self.build_symbol_formals(node=node, current_scope=current_scope,
                                                     current_line=current_line + 1)
            return current_line
        if node.name == "expr":
            result = ns.identify_node(node)
            if result == -1:
                print("ERORR AL IDENTIFICAR EXPR")
                return current_line

            type_of_expr = ns.expressions[result]

            if type_of_expr == "conditional":
                return self.build_symbol_expr_if(node=node, current_scope=current_scope, current_line=current_line + 1)
            elif type_of_expr == "assignment":
                return self.build_symbol_expr_assignation(node=node, current_scope=current_scope,
                                                          current_line=current_line + 1)
            elif type_of_expr == "dynamic_dispatch":
                return self.build_symbol_expr_parent_method_call(node=node, current_scope=current_scope,
                                                                 current_line=current_line + 1)
            elif type_of_expr == "function_call":
                return self.build_symbol_expr_local_method_call(node=node, current_scope=current_scope,
                                                                current_line=current_line + 1)
            elif type_of_expr == "loop":
                return self.build_symbol_expr_while(node=node, current_scope=current_scope,
                                                    current_line=current_line + 1)
            elif type_of_expr == "block":
                for node_expr in node.children:
                    if node.name != "{" and node.name != "}" and node.name != ";":
                        current_line += self.build_symbol_table(node=node_expr, current_scope=current_scope,
                                                                current_line=current_line + 1)
                return current_line
            elif type_of_expr == "let_in":
                return self.build_symbol_expr_let(node=node, current_scope=current_scope, current_line=current_line + 1)
            elif type_of_expr == "static_dispatch":
                return self.build_symbol_expr_obj_method_call(node=node, current_scope=current_scope,
                                                              current_line=current_line + 1)
            elif type_of_expr == "object_creation":
                return self.build_symbol_expr_new_object(node=node, current_scope=current_scope,
                                                         current_line=current_line + 1)
            elif type_of_expr == "isvoid":
                return self.build_symbol_expr_is_void(node=node, current_scope=current_scope, current_line=current_line)
            elif type_of_expr == "parenthesized_expr":
                for node_expr in node.children:
                    if node.name != "(" and node.name != ")":
                        current_line += self.build_symbol_table(node=node_expr, current_scope=current_scope,
                                                                current_line=current_line + 1)
                return current_line
            elif type_of_expr == "not":
                return self.build_symbol_not_bool(node=node, current_scope=current_scope, current_line=current_line + 1)
            elif type_of_expr == "bitwise_not":
                return self.build_symbol_not_int(node=node, current_scope=current_scope, current_line=current_line + 1)
            elif type_of_expr == "arithmetic_or_comparison":
                return self.build_symbol_expr_operation(node=node, current_scope=current_scope,
                                                        current_line=current_line + 1) + 1
            elif type_of_expr in ["identifier", "integer", "string", "boolean_true", "boolean_false"]:
                return self.build_symbol_simple_expression(node=node, current_scope=current_scope,
                                                           current_line=current_line)
            return current_line
        for child in node.children:
            current_line = self.build_symbol_table(child, current_scope, current_line=current_line + 1)

        return current_line + 1

    def build_symbol_class(self, node: Node, current_scope: Scope, current_line: int) -> int:
        parent_class = "Object"
        children = node.children
        if len(children) > 4:
            if children[2].name == 'inherits':
                if children[3].name == "node_type":
                    parent_class = children[3].children[0].name
                else:
                    parent_class = children[3].name

        class_name = node.children[1].name
        class_symbol = self.insert(
            name=class_name,
            data_type=parent_class,
            semantic_type="class",
            node=node, value=None,
            default_value=None,
            start_index=current_line,
            scope=current_scope,
            can_inherate=True,
            start_line=node.start_line,
            end_line=node.end_line
        )

        current_scope = self.start_scope(parent_scope=current_scope,
                                         scope_id=f'{current_scope.scope_id}-{class_name}(class)')

        for child in node.children:
            current_line = self.build_symbol_table(child, current_scope, current_line=current_line + 1)

        class_symbol.end_index = current_line
        current_scope = current_scope.get_parent()

        return current_line

    def build_symbol_method(self, node: Node, current_scope: Scope, current_line: int) -> int:
        method_name = node.children[0].name
        method_return_type = node.children[5].children[0].name
        full_signature = method_return_type
        method_scope_id = f"{current_scope.scope_id}-{method_name}(method)"

        method_scope = self.start_scope(parent_scope=current_scope, scope_id=method_scope_id)
        parameters = self.__get_parameters_from_method(node)
        parameters = parameters if isinstance(parameters, list) else []

        method_symbol = self.insert(
            name=method_name,
            semantic_type="method",
            data_type=full_signature,
            node=node,
            default_value=None,
            value=None,
            start_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            parameters=parameters,
            is_function=True,
            parameter_passing_method="reference"
        )

        for child in node.children:
            current_line = self.build_symbol_table(child, method_scope, current_line=current_line + 1)
        method_symbol.end_index = current_line
        current_scope = method_scope.get_parent()

        return current_line

    def build_symbol_attribute(self, node, current_scope, current_line) -> int:

        attribute_form = ns.verify_node_structure_attribute(node)
        if attribute_form == -1:
            print(f"WARNING: UNABLE TO CREATE ATTRIBUTE IN LINE {node.start_line}. INVALID FORM")
            return current_line
        children = node.children
        attr_name = children[0].name
        attr_type = children[2].children[0].name
        attr_value = children[-2] if attribute_form == 2 else None
        default_value = None

        if attr_type == "Bool":
            default_value = "false"
        elif attr_type == "String":
            default_value = ""
        elif attr_type == "Int":
            default_value = 0

        symbol = self.insert(
            name=attr_name,
            data_type=attr_type,
            semantic_type="attr",
            node=node, value=attr_value,
            default_value=default_value,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=False,
            parameters=[],
            parameter_passing_method=None)


        return current_line

    def build_symbol_expr_if(self, node: Node, current_scope: Scope, current_line: int) -> int:

        if_symbol = self.insert(
            name=f"{current_line}if",
            semantic_type="expression",
            data_type="block",
            node=node,
            default_value=None,
            value=node.children[1],
            start_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            parameters=[],
            is_function=True,
            type_of_expression="if"
        )

        noted_node = create_noted_node(node, self.content, self.scopes, if_symbol)
        errors = noted_node.run_tests()

        if_line = current_line
        if_scope = self.start_scope(parent_scope=current_scope, scope_id=f"{current_scope.scope_id}-IF({if_line}if)")
        if_content = node.children[3]
        # If content
        current_line = self.build_symbol_table(if_content, if_scope, current_line=current_line + 1)
        else_scope = self.start_scope(parent_scope=current_scope.parent,
                                      scope_id=f"{current_scope.scope_id}-ELSE({if_line}if)")
        else_content = node.children[5]
        current_line = self.build_symbol_table(else_content, else_scope, current_line=current_line + 1)

        if_symbol.end_index = current_line

        return current_line

    def build_symbol_expr_while(self, node: Node, current_scope: Scope, current_line: int) -> int:
        while_symbol = self.insert(
            name=f"{current_line}while",
            semantic_type="expression",
            data_type="Object",
            node=node,
            default_value=None,
            value=node.children[1],
            start_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            parameters=[],
            is_function=False,
            type_of_expression="while"

        )

        while_line = current_line

        bool_node = node.children[1]
        exp_node = node.children[3]
        # Pendiende registrar en algun punto estos valores en la tabla

        current_line += 2

        while_symbol.end_index = current_line

        return current_line

    def build_symbol_expr_assignation(self, node: Node, current_scope: Scope, current_line: int) -> int:

        expression_string = self.get_expression_to_str(node)
        symbol = self.insert(
            name=expression_string,
            data_type=None,
            semantic_type="expression",
            value=node.children[2],
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="assignation"

        )

        noted_node = create_noted_node(node, self.content, self.scopes, symbol)
        noted_node.run_tests()
        valor = noted_node.get_value()
        tipo_del_valor = noted_node.get_value_type()

        return current_line

    def build_symbol_expr_parent_method_call(self, node: Node, current_scope: Scope, current_line: int) -> int:
        symbol = self.insert(
            name=self.get_expression_to_str(node),
            data_type=None,
            semantic_type="expression",
            value=node,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="parent_call_method"
        )

        return current_line

    def build_symbol_expr_local_method_call(self, node: Node, current_scope: Scope, current_line: int) -> int:
        symbol = self.insert(
            name=self.get_expression_to_str(node),
            data_type=None,
            semantic_type="expression",
            value=node,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="local_call_method"
        )


        return current_line

    def build_symbol_expr_obj_method_call(self, node: Node, current_scope: Scope, current_line: int) -> int:
        symbol = self.insert(
            name=self.get_expression_to_str(node),
            data_type=None,
            semantic_type="expression",
            value=node,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="external_method_call"
        )

        return current_line

    def build_symbol_expr_let(self, node: Node, current_scope: Scope, current_line: int) -> int:
        let_scope = self.start_scope(parent_scope=current_scope,
                                     scope_id=f"{current_scope.scope_id}-let({current_line}let)")
        total_variables = ns.verify_node_structure_let(node)
        if total_variables == -1:
            # Error on let block structure
            return current_line

        variables, expr_to_evaluate, error = ns.decompose_let_expr(node)

        if error:
            # Error on getting let content
            return current_line

        for let_variable in variables:
            self.build_symbol_let_variable(node=let_variable.value, current_scope=let_scope, current_line=current_line, node_id=let_variable.var_id, tipo=let_variable.var_type)

        self.build_symbol_table(node=expr_to_evaluate, current_scope=let_scope, current_line=current_line)

        let_symbol = self.insert(
            name=self.get_expression_to_str(node),
            data_type=None,
            semantic_type="expression",
            value=node,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="let"
        )
        return current_line

    def build_symbol_let_variable(self, node: Node, current_scope: Scope, current_line: int, node_id: str,tipo: Node) -> int:
        value = ns.to_string_node(node.children[2]) if len(node.children)>2 else None

        self.insert(
            name=node_id,
            data_type=ns.to_string_node(tipo),
            semantic_type="expression",
            value=value,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="declaration_assignation"
        )

        return current_line

    def build_symbol_expr_new_object(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node)
        self.insert(
            name=" ".join(items),
            data_type=items[1],
            semantic_type="expression",
            value=node,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="object_incialization"
        )
        return current_line

    def build_symbol_expr_is_void(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node)
        self.insert(
            name=" ".join(items),
            data_type="Bool",
            semantic_type="expression",
            value=node,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="isvoid"
        )
        return current_line

    def build_symbol_expr_operation(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node)
        data_type = "Int"  # Hot fix must remove
        symbol = self.insert(
            name=" ".join(items),
            data_type=data_type,
            semantic_type="expression",
            value=node,
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="operation"
        )

        return current_line

    def build_symbol_simple_expression(self, node: Node, current_scope: Scope, current_line: int) -> int:
        content: str = str(node.children[0].name)
        d_type = "Int" if content.isnumeric() else "String" if content.startswith('\'') else "Bool"
        self.insert(
            name=content,
            data_type=d_type,
            semantic_type="expression",
            value=node.children[0],
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="simple_item"
        )

        return current_line

    def build_symbol_return(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node.children[1])
        data_type = "Int"  # Hot fix must remove
        symbol = self.insert(
            name=f"{current_line}return " + " ".join(items),
            data_type=data_type,
            semantic_type="func_return",
            value=node.children[1],
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression=None
        )

        return current_line

    def build_symbol_formals(self, node: Node, current_scope: Scope, current_line: int) -> int:

        for formal in node.children:
            if formal.name == "formal":
                current_line += 1
                formal_id = formal.children[0]
                formal_type = formal.children[2].children[0]
                symbol = self.insert(
                    name=formal_id.name,
                    data_type=formal_type.name,
                    semantic_type="formal",
                    value=None,
                    default_value=None,
                    start_index=current_line,
                    end_index=current_line,
                    start_line=node.start_line,
                    end_line=node.end_line,
                    scope=current_scope,
                    is_function=None,
                    parameters=None,
                    parameter_passing_method=None,
                    node=formal,
                    type_of_expression=None
                )


        return current_line

    def build_symbol_not_int(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node.children[1])
        symbol = self.insert(
            name=f"({current_line}) ~ " + " ".join(items),
            data_type="Int",
            semantic_type="expression",
            value=node.children[1],
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="unitary"
        )

        return current_line

    def build_symbol_not_bool(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node.children[1])
        symbol = self.insert(
            name=f"({current_line})not " + " ".join(items),
            data_type="Bool",
            semantic_type="expression",
            value=node.children[1],
            default_value=None,
            start_index=current_line,
            end_index=current_line,
            start_line=node.start_line,
            end_line=node.end_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node,
            type_of_expression="unitary"
        )

        return current_line
    """
    INTERNAL PROCESS
    """
    def __build_basic_classes(self) -> int:
        current_index = 1
        # Object
        self.insert(name="Object", data_type=None, semantic_type="class", can_inherate=True, scope=self.global_scope,
                    value=None, default_value=None, start_index=current_index, end_index=current_index)
        object_scope = self.start_scope(self.global_scope, scope_id=f"{self.global_scope.scope_id}-Object(class)")
        current_index += 1
        # abort()
        self.insert(name="abort", data_type="Object", semantic_type="method", can_inherate=None, scope=object_scope,
                    value=None, default_value=None, parameters=[], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1

        # Add more lines to consider methods content

        # type_name()

        self.insert(name="type_name", data_type="String", semantic_type="method", can_inherate=None, scope=object_scope,
                    value=None, default_value=None, parameters=[], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1

        # Add more lines to consider methods content

        # copy()
        self.insert(name="copy", data_type="SELF_TYPE", semantic_type="method", can_inherate=None, scope=object_scope,
                    value=None, default_value=None, parameters=[], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1

        # Add more lines to consider methods content

        # IO
        self.insert(name="IO", data_type="Object", semantic_type="class", can_inherate=True, value=None,
                    default_value=None, start_index=current_index, end_index=current_index)
        current_index += 1
        IO_scope = self.start_scope(self.global_scope, scope_id=f"{self.global_scope.scope_id}-IO(class)")
        # out_string(x: String) : SELF_TYPE
        self.insert(name="out_string", data_type="SELF_TYPE", semantic_type="method", can_inherate=None, scope=IO_scope,
                    value=None, default_value=None, parameters=[("x", "String")], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1
        io_out_string_scope = self.start_scope(IO_scope, f"{IO_scope.scope_id}-out_string(method)")
        self.insert(name="x", data_type="String", semantic_type="formal", can_inherate=None, scope=io_out_string_scope,
                    value=None, default_value="", parameters=None, start_index=current_index, end_index=current_index)
        current_index += 1
        # out_int(x: Int): SELF_TYPE
        self.insert(name="out_int", data_type="SELF_TYPE", semantic_type="method", can_inherate=None, scope=IO_scope,
                    value=None, default_value=None, parameters=[("x", "Int")], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1
        io_out_int_scope = self.start_scope(IO_scope, f"{IO_scope.scope_id}-out_int(method)")
        self.insert(name="x", data_type="Int", semantic_type="formal", can_inherate=None, scope=io_out_int_scope,
                    value=None, default_value=0, parameters=None, parameter_passing_method=None,
                    start_index=current_index, end_index=current_index)
        current_index += 1
        # in_string() : String
        self.insert(name="in_string", data_type="String", semantic_type="method", can_inherate=None, scope=IO_scope,
                    value=None, default_value="", parameters=[], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1
        # in_int(): Int
        self.insert(name="in_int", data_type="Int", semantic_type="method", can_inherate=None, scope=IO_scope,
                    value=None, default_value=0, parameters=[], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1
        # Int
        self.insert(name="Int", data_type="Object", semantic_type="class", can_inherate=False, value=None,
                    default_value=0, scope=self.global_scope, start_index=current_index, end_index=current_index)
        current_index += 1
        int_scope = self.start_scope(parent_scope=self.global_scope,
                                     scope_id=f"{self.global_scope.scope_id}-Int(class)")
        # String
        self.insert(name="String", data_type="Object", semantic_type="class", can_inherate=False, value=None,
                    default_value="", scope=self.global_scope, start_index=current_index, end_index=current_index)
        current_index += 1
        string_scope = self.start_scope(self.global_scope, f"{self.global_scope.scope_id}-String(class)")

        # length() : Int
        self.insert(name="length", data_type="Int", semantic_type="method", can_inherate=None, scope=string_scope,
                    value=None, default_value=0, parameters=[], parameter_passing_method="value",
                    start_index=current_index, end_index=current_index)
        current_index += 1
        # concat(s: String) :String
        self.insert(name="concat", data_type="String", semantic_type="method", can_inherate=None, scope=string_scope,
                    value=None, default_value="", parameters=[("s", "String")], start_index=current_index,
                    end_index=current_index)
        current_index += 1
        string_concat_scope = self.start_scope(string_scope, f"{string_scope.scope_id}-concat")
        self.insert(name="s", data_type="String", semantic_type="formal", can_inherate=None, scope=string_concat_scope,
                    value=None, default_value="", start_index=current_index, end_index=current_index)
        current_index += 1
        # substr(i: Int, l: Int) : String
        self.insert(name="substr", data_type="String", semantic_type="method", can_inherate=None, scope=string_scope,
                    value=None, default_value=0, parameters=[("i", "Int"), ("l", "Int")],
                    parameter_passing_method="value", start_index=current_index, end_index=current_index)
        current_index += 1
        string_substr_scope = self.start_scope(string_scope, f"{string_scope.scope_id}-substr")
        self.insert(name="i", data_type="Int", semantic_type="formal", can_inherate=None, scope=string_substr_scope,
                    value=None, default_value=0, parameters=None, parameter_passing_method=None,
                    start_index=current_index, end_index=current_index)
        current_index += 1
        self.insert(name="l", data_type="Int", semantic_type="formal", can_inherate=None, scope=string_substr_scope,
                    value=None, default_value=0, parameters=None, parameter_passing_method=None,
                    start_index=current_index, end_index=current_index)
        current_index += 1
        # Bool
        bool_scope = self.start_scope(parent_scope=self.global_scope,
                                      scope_id=f"{self.global_scope.scope_id}-Bool(class)")
        self.insert(name="Bool", data_type="Object", semantic_type="class", can_inherate=False, value=None,
                    default_value=False, scope=self.global_scope, start_index=current_index, end_index=current_index)
        current_index += 1

        return current_index

    """
    START 
    OPERATIONS
    """
    def add_error(self, error_type: str, error: SemanticError):
        if error_type in self.construction_errors:
            if error not in self.construction_errors[error_type]:
                self.construction_errors[error_type].append(error)
        else:
            self.construction_errors[error_type] = [error]

    def extend_errors(self, other_raised_errors: Dict[AnyStr, List[SemanticError]]):
        for error_type, errors in other_raised_errors.items():
            for error in errors:
                self.add_error(error_type, error)

    def get_symbol_scope(self, symbol: Symbol) -> Scope:
        name = symbol.construct_scope_name()
        if not name:
            return
        if name in self.scopes:
            return self.scopes.get(name)
        print("Couldn't find symbol in scope.")
        return None

    def delete_content(self, name: str, scope: Scope = None) -> bool:
        """Utilizando el nombre del simbolo eliminar toda referencia del simbolo en el objeto.

        Args:
            name (str): Nombre del símbolo.
            scope (Scope, optional): Objeto scope en el que se espera encontrar el simbolo. Defaults to None.

        Returns:
            bool: Indica si la operación se realizó con éxito. True si se elimino, False si no lo encontro en el scope.
        """
        scope: Scope = self.check_or_get_default_scope(scope)
        if name in self.content[scope.scope_id]:
            del self.content[scope.scope_id][name]
            scope.delete_content(name)
            return True
        return False

    def insert(self, name, data_type, semantic_type, value, default_value, start_index=None, end_index=None,
               start_line=-1, end_line=0, scope=None, is_function=False, parameters=[], parameter_passing_method=None,
               node=None, can_inherate=False, type_of_expression=None):
        """Inerta un simbolo a la tabla.

        Args:
            name (str): Nombre de simbolo
            data_type (str): Tipo de dato del simbolo (Int, Float... etc.)
            semantic_type (str): Tipo semantico (atributo, metodo o clase... etc. )
            value (any): Valor del simbolo
            line (int, optional): Linea en la que se "creo" el simbolo. Defaults to None.
            scope (Scope, optional): Scope al que se desea insertar. Defaults to None -> Global scope.
            is_function (bool, optional): Indica si el simbolo es funcion. Defaults to False.
            parameters (list, optional): listado de parametros. Defaults to [].
            parameter_passing_method (_type_, optional): Metodo por el cual se pasan los parametros (referencia o valor). Defaults to None.
        """
        scope = self.check_or_get_default_scope(scope)
        symbol = Symbol(
            name=name,
            value=value,
            node=node,
            default_value=default_value,
            data_type=data_type,
            semantic_type=semantic_type,
            start_index=start_index,
            end_index=end_index,
            start_line=start_line,
            end_line=end_line,
            scope=scope.scope_id,
            is_function=is_function,
            parameters=parameters,
            parameter_passing_method=parameter_passing_method,
            can_inherate=can_inherate,
            type_of_expression=type_of_expression
        )

        symbol, error = scope.add_content(symbol)

        if error:
            semanticErr = SemanticError(name=error.name, details=error.details, symbol=error.symbol, scope=error.scope,
                                        line=error.line)
            if semanticErr.name in self.construction_errors:
                self.construction_errors[semanticErr.name].append(semanticErr)
            else:
                self.construction_errors[semanticErr.name] = [semanticErr]
        self.content[scope.scope_id][symbol.name] = symbol
        self.sequential_symbols.append(symbol)
        return symbol

    def search(self, name, scope=None):
        """Busca por nombre el símbolo en la tabla partiendo de un scope. En caso de encontrarlo en el actual expande la busqueda al padre.

        Args:
            name (str): _description_
            scope (Scope, optional): Scope sobre el que se espera encontrar . Defaults to None.

        Returns:
            Symbol: El simbolo buscado con todos su atributos.
        """
        scope: Scope = self.check_or_get_default_scope(scope)
        item: Symbol = None
        found_item = False
        while not found_item and scope != None:
            item = scope.search_content(name)
            if item is None:
                scope = scope.get_parent()
            else:
                found_item = True

        return item

    def start_scope(self, parent_scope=None, scope_id=None):
        """Incializa un scope en el objeto.

        Args:
            parent_scope (Scope, optional): Scope padre. Defaults to None-> Global.
            scope_id (str, optional): Identificador de este nuevo scope. Defaults to None.

        Returns:
            Scope: El nuevo scope creado
        """
        new_scope = Scope(parent=parent_scope, scope_id=scope_id)
        self.scopes[scope_id] = new_scope
        return new_scope

    def check_or_get_default_scope(self, scope: Scope):
        """Revisa la validez de un scope y en caso no lo sea, devuelve el global para ser utilizado.

        Args:
            scope (Scope): Scope que se desea comprobar validez/utilizar.

        Returns:
            Scope: Un Scope valido, ya sea el original (de ser válido), o el global por default.
        """
        if scope is None:
            return self.global_scope

        if scope.scope_id not in self.scopes:
            return self.global_scope
        return scope

    def add_error(self, key_error: str, error: SemanticError):
        if key_error in self.construction_errors:
            self.construction_errors = self.construction_errors[key_error]

    def extend_errors(self, error_dict: Dict[AnyStr, List[SemanticError]]):

        for type_err, errors in error_dict.items():
            if type_err in self.construction_errors:
                self.construction_errors[type_err].extend(errors)
            else:
                self.construction_errors[type_err] = errors

    @staticmethod
    def get_expression_to_str(expr_node: Node) -> str:
        """Convierte Nodos de anytree con nombre expr en su valor to string deconstruyendo el valor de sus hijos.

        Args:
            expr_node (anytree.Node): Nodo base que referencia a demas nodos parte de la expresion.

        Returns:
            str: Version to string del nodo.
        """
        if isinstance(expr_node, Node):
            children = expr_node.children
            if expr_node.name == "expr":
                content = []
                for child in children:
                    content.append(SymbolTable.get_expression_to_str(child))
                return "".join(content)

            return expr_node.name
        else:
            return expr_node

    @staticmethod
    def get_expression_to_list(expr_node: Node) -> str:
        """Convierte Nodos de anytree con nombre expr en su valor to string deconstruyendo el valor de sus hijos.

        Args:
            expr_node (anytree.Node): Nodo base que referencia a demas nodos parte de la expresion.

        Returns:
            str: Version to string del nodo.
        """
        if isinstance(expr_node, Node):
            children = expr_node.children
            if expr_node.name == "expr":
                content = []
                for child in children:
                    content.extend(SymbolTable.get_expression_to_list(child))
                return content

            return [str(expr_node.name)]
        else:
            return [str(expr_node)]

    @staticmethod
    def __get_parameters_from_method(method_node: Node) -> List[tuple]:
        """Partiendo del nodo metodo, obtiene sus parametros.

        Args:
            method_node (anytree.Node): Nodo metodo.

        Returns:
            List[set]: [(id_parametro: Tipo)]; Listado de tuplas con el id del parametro y su tipo
        """
        formals_node = method_node.children[2]
        parameters = []
        for child in formals_node.children:
            if child.name == "formal":
                parameter_parts = []
                for part in child.children:
                    if part.name != ":":
                        if part.name == "node_type" or part.name == "type":
                            parameter_type = part.children[0].name
                            parameter_parts.append(parameter_type)
                        else:
                            parameter_parts.append(part.name)
                parameters.append(tuple(parameter_parts))

        return parameters

    """
    MEMORY USAGE
    """
    @staticmethod
    def est__symbol_has_scope(symbol: Symbol):
        return (
                symbol.semantic_type == "class" or
                symbol.semantic_type == "method"
        )

    @staticmethod
    def est__symbol_is_basic(symbol: Symbol):
        return (
                (symbol.semantic_type == "class" and symbol.name == "Object") or
                (symbol.semantic_type == "class" and symbol.name == "IO") or
                (symbol.semantic_type == "class" and symbol.name == "Int") or
                (symbol.semantic_type == "class" and symbol.name == "String") or
                (symbol.semantic_type == "class" and symbol.name == "Bool") or
                (symbol.scope.startswith("global-Object(class)")) or
                (symbol.scope.startswith("global-IO(class)")) or
                (symbol.scope.startswith("global-String(class)"))
        )

    def estimate_symbol_table_memory_usage(self):
        total_usage = 0  # Might not be precise since it
        for scope_id, symbols in self.content.items():
            for symbol_name, symbol in symbols.items():
                symbol_mem = self.estimate_symbol_memory_usage(symbol)
                total_usage += symbol_mem if symbol_mem is not None else 0
        return total_usage

    def estimate_symbol_memory_usage(self, symbol: Symbol):
        if self.est__symbol_is_basic(symbol):  # Basic class that has no code and will be added directly into assembler.
            symbol.set_bytes_memory_size(None)  # So it has no memory estimated in symbol table.
            return None
        else:
            if self.est__symbol_has_scope(symbol):
                mem_size = self.scoped_calculate_memory_size(symbol)
                symbol.set_bytes_memory_size(mem_size)
                return mem_size
            mem_size = symbol.simple_calculate_memory_size()
            symbol.set_bytes_memory_size(mem_size)
            return mem_size

    def scoped_calculate_memory_size(self, symbol):
        scope_name = symbol.construct_scope_name()
        if scope_name is None:
            print(f"{symbol} no tiene nomre de scope valido")
            return 0
        if scope_name not in self.scopes:
            print(f"{symbol}({scope_name}) no se encuentra en tabla de simbolos")
            return 0
        scope: Scope = self.scopes.get(scope_name)
        content = scope.content
        total_cost = 0
        for symbol_name, symbol in content.items():
            cost = self.estimate_symbol_memory_usage(symbol)
            if cost is not None and isinstance(cost, int):
                total_cost += cost
        return total_cost

    """
    SEMANTIC TESTS
    """
    def check_inheritance_chain(self, class_name) -> tuple:
        classes = self.global_scope.get_all_classes()
        if class_name not in classes:
            msg = f"OutOfScope: {class_name} not defined in global scope"
            return msg, True, [class_name], class_name

        class_chain = [class_name]
        class_object: Symbol = classes.get(class_name)

        while class_object.name != "Object":

            next_class = class_object.data_type

            if next_class not in classes:
                class_chain.append(next_class)
                return f"InhertanceMissingFather: Missing parent class reference of class \"{class_object.data_type}\", called \"{next_class}\"", True, class_chain, class_object.name

            next_class_object: Symbol = classes.get(next_class)

            if next_class in class_chain:
                class_chain.append(next_class)
                return f"InhertanceRecursive: Found circular reference on {next_class} class.", True, class_chain, next_class

            if not next_class_object.can_inherate:
                class_chain.append(next_class)
                return f"NotAllowedInhertance: Class {class_object.name} cannot inherate from {next_class} special class.", True, class_chain, class_object.name

            class_chain.append(next_class)
            class_object = next_class_object

        return "", False, class_chain, None

    def run_semantic_tests_using_noted_nodes(self):
        for scope_name, scope_content in self.content.items():
            for symbol_name, symbol in scope_content.items():
                node = symbol.node
                if node is not None:
                    noted_node = create_noted_node(node, self.content, self.scopes, symbol)

                    if noted_node is not None:
                        self.extend_errors(noted_node.run_tests())

        return self.construction_errors

    def run_tests(self):
        self.run_semantic_tests_using_noted_nodes()

        return self.construction_errors


    def get_main_method_symbol(self):
        pass

    def get_three_directions_code(self):
        tdc = ThreeDirectionsCode(self.scopes, self.content, self.sequential_symbols)
        tdc.build()
        # tdc.new_build()
        return tdc

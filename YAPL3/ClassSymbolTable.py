from dataclasses import dataclass, field
from collections import defaultdict
from prettytable import PrettyTable
from typing import List, Dict
from anytree import Node

from Symbol import Symbol
from Scope import Scope
from SemanticCommon import *
from typing import List, Dict


class SymbolTable:
    def __init__(self, root):
        """Método constructor

        Args:
            root (anytree.Node): Nodo raiz del árbol de análisis sintáctico generado por anytree para la gramática. 
        """
        self.content = defaultdict(
            dict)  # {<scope_id>: {symbol_name: Symbol}} >>  Diccionario con clave el id_scope y valor un diccionario con simbolos (diccionario interno, identificador de simbolo como clave; Objeto Simbolo como valor)
        self.construction_errors: Dict[str: List[SemanticError]] = {}
        self.global_scope = Scope(parent=None,
                                  scope_id="global")  # La tabla de simbolos de inicializa con un scope global en el que se almacenan simbolos que no esten debajo de otros scopes creados.
        self.scopes = {
            "global": self.global_scope}  # {<scope_id>: Scope} >> Scopes de la tabla almacenados en dicionarios que tiene por clave su identificador y su objeto por valor.
        self.build_symbol_table(node=root, current_scope=self.global_scope,
                                current_line=self.__build_basic_classes())  # Construye recursivamente la tabla de simbolos

    def __str__(self) -> str:
        """Crea una version bonita y para consola de la tabla. 

        Returns:
            str: Tabla estetica. 
        """
        table = PrettyTable()
        table.field_names = ["Scope", "Name", "Semantic Type", "Value", "Memory bytes", "Data type", "S.Index",
                             "E.Index", "S.Line", "E.Line", "Exp. Type"]
        for scope_id, symbols in self.content.items():
            for symbol_name, symbol in symbols.items():
                table.add_row([scope_id, symbol_name, symbol.semantic_type,
                               self.get_expression_to_str(symbol.value) if symbol.value else symbol.value,
                               symbol.bytes_memory_size, symbol.data_type, symbol.start_index, symbol.end_index,
                               symbol.start_line, symbol.end_line, symbol.type_of_expression])
        return str(table)

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
            current_line = self.class_build_symbol(node=node, current_scope=current_scope,
                                                   current_line=current_line + 1)
            return current_line

        if node.name == "method":
            current_line = self.method_build_symbol(node, current_scope, current_line + 1)
            return current_line

        if node.name == "attr":
            current_line = self.attribute_build_symbol(node, current_scope, current_line + 1)
            return current_line

        if node.name == "func_return":
            current_line = self.return_build_symbol(node=node, current_scope=current_scope,
                                                    current_line=current_line + 1)
            return current_line

        if node.name == "formals":
            current_line = self.formals_build_symbol(node=node, current_scope=current_scope,
                                                     current_line=current_line + 1)
            return current_line
        if node.name == "expr":
            # If statment >>> 'if' bool_value  'then' expr 'else' expr 'fi'
            if node.children:
                if node.children[0].name == "if":
                    current_line = self.if_expr_build_symbol(node=node, current_scope=current_scope,
                                                             current_line=current_line + 1)
                    return current_line
                    # Attribute assignation >>> ID '<-' expr
            if node.children:
                if len(node.children) > 1:
                    if node.children[1].name == "<-":
                        current_line = self.attribute_assignation_build_expr_symbol(node=node,
                                                                                    current_scope=current_scope,
                                                                                    current_line=current_line + 1)
                        return current_line
            # Parent Class method >>> expr '@' type '.' ID '(' expr (',' expr)* ')'
            if node.children:
                if len(node.children) > 1:
                    if node.children[1].name == "@":
                        current_line = self.parent_method_call_expr_symbol(node=node, current_scope=current_scope,
                                                                           current_line=current_line + 1)
                        return current_line
            # Local method call  >>> ID '(' expr (',' expr)* ')'
            if node.children:
                if len(node.children) > 1:
                    if node.children[1].name == "(":
                        current_line = self.local_method_call_expr_call(node=node, current_scope=current_scope,
                                                                        current_line=current_line + 1)
                        return current_line
                        # While loop >>>'while' bool_value'loop' expr 'pool'
            if node.children:
                if node.children[0].name == "while":
                    current_line = self.while_exp_build_symbol(node=node, current_scope=current_scope,
                                                               current_line=current_line + 1)
                    return current_line
            # Key embedded  expr >>> '{' expr (';' expr)* '}'
            if node.children:
                if node.children[0].name == "{":
                    for node_expr in node.children:
                        if node.name != "{" and node.name != "}" and node.name != ";":
                            current_line += self.build_symbol_table(node=node_expr, current_scope=current_scope,
                                                                    current_line=current_line + 1)

                    return current_line
                    # Let statement >>> 'let' ID ':' type ('<-' expr)? (',' ID ':' type ('<-' expr)?)* 'in' expr
            if node.children:
                if node.children[0].name == "let":
                    current_line = self.let_expression_build_symbol(node=node, current_scope=current_scope,
                                                                    current_line=current_line + 1)
                    return current_line
                elif node.children[0].children:
                    if node.children[0].children[0].name == "let":
                        current_line = self.let_expression_build_symbol(node=node.children[0],
                                                                        current_scope=current_scope,
                                                                        current_line=current_line + 1)
                        return current_line
                        # External method call >>> expr '.' ID '(' expr (',' expr)* ')'
            if node.children:
                if len(node.children) > 1:
                    if node.children[1].name == ".":
                        current_line = self.external_method_call_build_symbol(node=node, current_scope=current_scope,
                                                                              current_line=current_line + 1)
                        return current_line
            # NEW Object >>> 'new' classDef
            if node.children:
                if node.children[0].name == "new":
                    current_line = self.new_object_expression_build_symbol(node=node, current_scope=current_scope,
                                                                           current_line=current_line + 1)

                    return current_line
            # Is-void statement 'is-void' expr
            if node.children:
                if node.children[0].name == "isvoid":
                    current_line = self.is_void_expression_build_symbol(node=node, current_scope=current_scope,
                                                                        current_line=current_line)
                    return current_line
                    # '(' expr ')'
            if node.children:
                if node.children[0].name == "(":
                    for node_expr in node.children:
                        if node.name != "(" and node.name != ")":
                            current_line += self.build_symbol_table(node=node_expr, current_scope=current_scope,
                                                                    current_line=current_line + 1)

                    return current_line
                    # 'not' expr
            if node.children:
                if node.children[0].name == "not":
                    current_line = self.not_bool_build_symbol(node=node, current_scope=current_scope,
                                                              current_line=current_line + 1)
                    return current_line
            # '~' expr
            if node.children:
                if node.children[0].name == "~":
                    current_line = self.not_int_build_symbol(node=node, current_scope=current_scope,
                                                             current_line=current_line + 1)
                    return current_line
            # op=OP expr  
            if node.children:
                if len(node.children) > 1:
                    current_line = self.operation_expression_build_symbol(node=node, current_scope=current_scope,
                                                                          current_line=current_line + 1)
                    return current_line + 1
            # ID | INT | STRING | RW_FALSE | RW_TRUE | 
            if node.children:
                if len(node.children) == 1:
                    current_line = self.simple_expression_build_symbol(node=node, current_scope=current_scope,
                                                                       current_line=current_line)
                    return current_line

            return current_line
        for child in node.children:
            current_line = self.build_symbol_table(child, current_scope, current_line=current_line + 1)

        return current_line + 1

    def class_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        parent_class = "Object"
        children = node.children
        if len(children) > 4:
            if children[2].name == 'inherits':
                if children[3].name == "type":
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

    def method_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
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

    def attribute_build_symbol(self, node, current_scope, current_line) -> int:
        children = node.children
        attr_name = children[0].name
        attr_type = children[2].children[0].name
        attr_value = children[-2] if len(children) > 4 else None
        default_value = None

        if attr_type == "Bool":
            default_value = "false"
        elif attr_type == "String":
            default_value = ""
        elif attr_type == "Int":
            default_value = 0

        self.insert(
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
        if attr_value:
            current_line = self.build_symbol_table(node=attr_value, current_scope=current_scope,
                                                   current_line=current_line + 1)
        return current_line

    def if_expr_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:

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

    def while_exp_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
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

    def attribute_assignation_build_expr_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        expression_string = self.get_expression_to_str(node)
        self.insert(
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
            node=node
        )

        current_line = self.build_symbol_table(node=node.children[2], current_scope=current_scope,
                                               current_line=current_line + 1)

        return current_line

    def parent_method_call_expr_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        self.insert(
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

    def local_method_call_expr_call(self, node: Node, current_scope: Scope, current_line: int) -> int:
        self.insert(
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

    def external_method_call_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        self.insert(
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

    def let_expression_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:

        let_scope = self.start_scope(parent_scope=current_scope,
                                     scope_id=f"{current_scope.scope_id}-let({current_line}let)")

        let_content = list(node.children)
        found_in = False

        item: Node = let_content.pop(0)

        let_value = None

        while not found_in:

            if item.name == "in":
                let_value = let_content.pop(0)
                found_in = True
                current_line += 1

            elif item.name != "," and item.name != ":" and item.name != "<-" and item.name != "let":
                valor = None
                tipo = None

                next_item = item
                while let_content and next_item.name != "type":
                    next_item = let_content.pop(0)

                tipo = next_item.children[0]

                next_item = let_content.pop(0)

                if next_item.name == "<-":
                    valor = let_content.pop(0)

                current_line += 1
                self.variable_declaration_assignation(node=valor, current_scope=let_scope, current_line=current_line,
                                                      ID=item.name, tipo=tipo.name)

                item = let_content.pop(0)
            else:
                item = let_content.pop(0)

        let_symbol = self.insert(
            name=self.get_expression_to_str(node),
            data_type=None,
            semantic_type="expression",
            value=let_value,
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

    def variable_declaration_assignation(self, node: Node, current_scope: Scope, current_line: int, ID: str,
                                         tipo: str) -> int:
        self.insert(
            name=ID,
            data_type=tipo,
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
            type_of_expression="declaration_assignation"
        )
        return current_line

    def new_object_expression_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
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

    def is_void_expression_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
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

    def operation_expression_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node)
        data_type = "Int"  # Hot fix must remove
        # ^^ Assumes that all operations means arithmetic operation. FIX to identify bool operations!!
        self.insert(
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

    def simple_expression_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
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

    def return_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node.children[1])
        data_type = "Int"  # Hot fix must remove
        self.insert(
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

    def formals_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:

        for formal in node.children:
            if formal.name == "formal":
                current_line += 1
                formal_id = formal.children[0]
                formal_type = formal.children[2].children[0]
                self.insert(
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

    def not_int_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node.children[1])
        self.insert(
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

    def not_bool_build_symbol(self, node: Node, current_scope: Scope, current_line: int) -> int:
        items = self.get_expression_to_list(node.children[1])
        self.insert(
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
            if item == None:
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
        total_usage = 0  # Might not me precise since it
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

    def check_inheritance_chain(self, class_name) -> tuple:
        classes = self.global_scope.get_all_classees()
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

    # Pending implement methods content
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

    def evaluate_expr(self, exp_node: Node, scope: Scope, feed_back: list):
        # If statment >>> 'if' bool_value  'then' expr 'else' expr 'fi'
        if exp_node.children:
            if exp_node.children[0].name == "if":
                feed_back.append(
                    SemanticError(
                        name="IF evaluation:: ",
                        details="Cannot set a value of an if to an identifier.",
                        symbol=None,
                        scope=scope,
                        line=None
                    )
                )
                return None, "void"
        # Attribute assignation >>> ID '<-' expr
        if exp_node.children:
            if len(exp_node.children) > 1:
                if exp_node.children[1].name == "<-":
                    ID = exp_node.children[0]
                    expression = exp_node.children[2]
                    content, last_scope_search = scope.search_availabilty_of_content(ID)

                    type_gotted = None
                    if not content:
                        feed_back.append(
                            SemanticError(
                                name="Undeclared variable evaluation:: ",
                                details=f"Cannot use undeclared identifier.\"{ID}\"",
                                symbol=None,
                                scope=scope,
                                line=None
                            )
                        )
                        return (None, "void")
                    type_expected = SymbolTable.check_existing_type()
                    if type_expected not in self.global_scope.get_all_classees():
                        feed_back.append(
                            SemanticError(
                                name="Declared on unexsisting type::",
                                details=f"Cannot use undeclared type.\"{type_expected}\"",
                                symbol=None,
                                scope=scope,
                                line=None
                            )
                        )
                        return None, "void"

        # Parent Class method >>> expr '@' type '.' ID '(' expr (',' expr)* ')'
        if exp_node.children:
            if len(exp_node.children) > 1:
                if exp_node.children[1].name == "@":
                    pass
        # Local method call  >>> ID '(' expr (',' expr)* ')'
        if exp_node.children:
            if len(exp_node.children) > 1:
                if exp_node.children[1].name == "(":
                    pass
        # While loop >>>'while' bool_value'loop' expr 'pool'
        if exp_node.children:
            if exp_node.children[0].name == "while":
                pass
        # Key embedded  expr >>> '{' expr (';' expr)* '}'
        if exp_node.children:
            if exp_node.children[0].name == "{":
                pass
        # Let statement >>> 'let' ID ':' type ('<-' expr)? (',' ID ':' type ('<-' expr)?)* 'in' expr
        if exp_node.children:
            if exp_node.children[0].name == "let":
                pass
            elif exp_node.children[0].children:
                if exp_node.children[0].children[0].name == "let":
                    pass
        # External method call >>> expr '.' ID '(' expr (',' expr)* ')'
        if exp_node.children:
            if len(exp_node.children) > 1:
                if exp_node.children[1].name == ".":
                    pass
        # NEW Object >>> 'new' classDef
        if exp_node.children:
            if exp_node.children[0].name == "new":
                pass
        # Is-void statement 'is-void' expr
        if exp_node.children:
            if exp_node.children[0].name == "isvoid":
                pass
        # '(' expr ')'
        if exp_node.children:
            if exp_node.children[0].name == "(":
                for node_expr in exp_node.children:
                    if exp_node.name != "(" and exp_node.name != ")":
                        pass
            pass
        # 'not' expr
        if exp_node.children:
            if exp_node.children[0] == "not":
                pass
        # '~' expr
        if exp_node.children:
            if exp_node.children[0].name == "~":
                pass
        # op=OP expr  
        if exp_node.children:
            if len(exp_node.children) > 1:
                pass
        # ID | INT | STRING | RW_FALSE | RW_TRUE | 
        if exp_node.children:
            if len(exp_node.children) == 1:
                pass

        pass

    def __get_parameters_from_method(self, method_node: Node) -> List[tuple]:
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
                        if part.name == "type":
                            parameter_type = part.children[0].name
                            parameter_parts.append(parameter_type)
                        else:
                            parameter_parts.append(part.name)
                parameters.append(tuple(parameter_parts))
        return parameters

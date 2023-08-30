from dataclasses import dataclass, field
from collections import defaultdict
from prettytable import PrettyTable
from typing import List, Dict
from anytree import Node

from Symbol import Symbol
from Scope import Scope


class SymbolTable:
    def __init__(self, root):
        """Método constructor

        Args:
            root (anytree.Node): Nodo raiz del árbol de análisis sintáctico generado por anytree para la gramática. 
        """
        self.content = defaultdict(dict)  # {<scope_id>: {symbol_name: Symbol}} >>  Diccionario con clave el id_scope y valor un diccionario con simbolos (diccionario interno, identificador de simbolo como clave; Objeto Simbolo como valor)
        self.global_scope = Scope(parent=None, scope_id = "global") # La tabla de simbolos de inicializa con un scope global en el que se almacenan simbolos que no esten debajo de otros scopes creados. 
        self.scopes = { "global": self.global_scope } # {<scope_id>: Scope} >> Scopes de la tabla almacenados en dicionarios que tiene por clave su identificador y su objeto por valor. 
        self.addition_classes = self.__build_basic_classes()
        self.build_symbol_table(root, current_scope=self.global_scope) # Construye recursivamente la tabla de simbolos
        
    def __str__(self)-> str:
        """Crea una version bonita y para consola de la tabla. 

        Returns:
            str: Tabla estetica. 
        """
        table = PrettyTable()
        table.field_names = ["Scope", "Name", "Semantic Type", "Value", "Deafult Value", "Data type",  "S. line", "F. Line"]
        for scope_id,  symbols in self.content.items():
            for symbol_name, symbol in symbols.items():
                table.add_row([scope_id, symbol_name, symbol.semantic_type, self.get_expresion_to_str(symbol.value) if symbol.value else symbol.value, symbol.default_value,symbol.data_type, symbol.start_line, symbol.finish_line])
        return str(table)

    def build_symbol_table(self, node, current_scope = None, current_line = 0) -> int:
        """Construye la tabla de simbolos. Al encontrar metodos o clases inicializa Scopes y llama recursivamente sobre los hijos de ese nodo.

        Args:
            node (anytree.Node): Nodo el cual se deasea ubicar en tabla de simbolos.
            current_scope (scope_actual, optional): En el cual se desea estableceer el nodo. Defaults to None.
        """
        if node.name == "program":
            for child in node.children:
                current_line = self.build_symbol_table(child, current_scope, current_line+1)
            return current_line

        if node.name == "classDef":
            current_line = self.class_build_symbol(node=node, current_scope=current_scope, current_line=current_line+1)
            return current_line

        if node.name == "method":
            current_line = self.method_build_symbol(node, current_scope, current_line+1)
            return current_line

        if node.name == "attr": 
            current_line = self.attribute_build_symbol(node, current_scope, current_line+1)
            return current_line
        
        if node.name == "func_return":
            return current_line + 1
        
        if node.name == "formals":
            return current_line +1 
        if node.name == "expr":
            # If statment >>> 'if' bool_value  'then' expr 'else' expr 'fi'
            if node.children:
                if node.children[0].name == "if":
                    current_line = self.if_expr_build_symbol(node=node, current_scope=current_scope, current_line=current_line+1)
                    return current_line 
            # Attribute assignation >>> ID '<-' expr
            if node.children:
                if len(node.children)>1:
                    if node.children[1].name=="<-":
                        current_line = self.attribute_asignation_build_expr_symbol(node = node, current_scope=current_scope, current_line=current_line+1)
                        return current_line
            # Parent Class method >>> expr '@' type '.' ID '(' expr (',' expr)* ')'
            if node.children:
                if len(node.children)>1:
                    if node.children[1].name=="@":
                        current_line = self.parent_method_call_expr_symbol(node = node, current_scope=current_line, current_line=current_line+1)
                        return current_line
            # Local method call  >>> ID '(' expr (',' expr)* ')'
            if node.children:
                if len(node.children)>1:
                    if node.children[1].name=="(":
                        return current_line 
            # While bucle >>>'while' bool_value'loop' expr 'pool'
            if node.children:
                if node.children[0].name == "while":
                    current_line = self.while_exp_build_symbol(node=node, current_scope=current_scope, current_line=current_line)
                    return current_line
            # Key embeded  expr >>> '{' expr (';' expr)* '}'
            if node.children:
                if node.children[0].name == "{":
                    return current_line 
            # Let statment >>> 'let' ID ':' type ('<-' expr)? (',' ID ':' type ('<-' expr)?)* 'in' expr
            if node.children:
                if node.children[0].name == "let":
                    return current_line 
            # External method call >>> expr '.' ID '(' expr (',' expr)* ')'
            if node.children:
                if len(node.children)>1:
                    if node.children[1].name==".":
                        return current_line
            # NEW Object >>> 'new' classDef
            if node.children:
                if node.children[0].name == "new":
                    return current_line +1 
            # Isvoid statment 'isvoid' expr
            if node.children:
                if node.children[0].name == "isvoid":
                    return current_line +1
            # '(' expr ')'
            if node.children:
                if node.children[0].name == "(":
                    return current_line +1
            # Comparation expression expr op=OP expr
            '''
                Implementar
            '''
            return current_line 

        for child in node.children:
            current_line = self.build_symbol_table(child, current_scope, current_line=current_line+1)
        
        return current_line + 1

    def class_build_symbol(self, node: Node, current_scope: Scope , current_line: int)-> int:
        parent_class = "Object"
        children = node.children
        if len(children)>4:
            if children[2].name == 'inherits':
                parent_class = children[3].name

        class_name = node.children[1].name
        class_symbol = self.insert(name = class_name, data_type = parent_class, semantic_type="class", node=node,value=None, default_value=None,start_line = current_line, scope = current_scope, can_inherate=True)

        current_scope = self.start_scope(parent_scope=current_scope, scope_id=f'{current_scope.scope_id}-{class_name}(class)')


        for child in node.children:
            current_line = self.build_symbol_table(child, current_scope, current_line=current_line + 1)

        class_symbol.finish_line = current_line
        current_scope = current_scope.get_parent()

        return current_line

    def method_build_symbol(self, node: Node, current_scope: Scope, current_line: int)-> int:
        method_name = node.children[0].name
        method_return_type = node.children[5].children[0].name
        full_signature = method_return_type
        method_scope_id = f"{current_scope.scope_id}-{method_name}(method)"

        method_scope = self.start_scope(parent_scope=current_scope, scope_id=method_scope_id)
        parameters = self.__get_parameters_from_method(node)
        parameters = parameters if isinstance(parameters, list) else []

        method_symbol = self.insert(
            name = method_name,
            semantic_type="method",
            data_type = full_signature,
            node=node,
            default_value=None,
            value=None, 
            start_line=current_line, 
            scope = current_scope, 
            parameters=parameters, 
            is_function=True,
            parameter_passing_method="reference")

        for child in node.children:
            current_line = self.build_symbol_table(child, method_scope, current_line=current_line+1)
        method_symbol.finish_line = current_line
        current_scope = method_scope.get_parent()

        return current_line

    def attribute_build_symbol(self, node, current_scope, current_line)-> int:
        children = node.children
        attr_name = children[0].name
        attr_type = children[2].children[0].name
        attr_value =  children[-2] if len(children)>4 else None
        default_value = None

        if attr_type == "Bool":
            default_value = "false"
        elif attr_type == "String":
            default_value = ""
        elif attr_type == "Int":
            default_value = 0

        self.insert(name = attr_name, data_type=attr_type, semantic_type="attr" ,node =node, value=attr_value, default_value = default_value, start_line=current_line, finish_line=current_line,scope=current_scope, is_function=False, parameters=[], parameter_passing_method=None)

        return current_line

    def if_expr_build_symbol(self, node: Node, current_scope: Scope, current_line: int)-> int:
        
        if_symbol = self.insert(
            name = f"{current_line}if", 
            semantic_type = "expression", 
            data_type = "block", 
            node = node, 
            default_value = None,
            value = node.children[1],
            start_line = current_line,
            scope = current_scope,
            parameters=[],
            is_function=True)

        if_line = current_line
        if_scope = self.start_scope(parent_scope=current_scope, scope_id=f"{current_scope.scope_id}-IF({if_line}if)")
        if_content = node.children[3]
        # If content
        current_line = self.build_symbol_table(if_content, if_scope, current_line=current_line+1)
        else_scope = self.start_scope(parent_scope=current_scope.parent, scope_id=f"{current_scope.scope_id}-ELSE({if_line}if)")
        else_content = node.children[5]
        current_line = self.build_symbol_table(else_content, else_scope, current_line=current_line+1)

        if_symbol.finish_line = current_line 

        return current_line

    def while_exp_build_symbol(self, node: Node, current_scope: Scope, current_line: int)-> int:
        while_symbol = self.insert(
            name = f"{current_line}while", 
            semantic_type = "expression", 
            data_type = "Object", 
            node = node, 
            default_value = None,
            value = node.children[1],
            start_line = current_line,
            scope = current_scope,
            parameters=[],
            is_function=False) 
        
        while_line = current_line

        bool_node = node.children[1]
        exp_node = node.children[3]
        # Pendiende registrar en algun punto estos valores en la tabla

        current_line += 2

        while_symbol.finish_line = current_line

    
        return current_line + 1
    
    def attribute_asignation_build_expr_symbol(self, node: Node, current_scope: Scope, current_line: int)-> int:
        expression_string = self.get_expresion_to_str(node)
        value_str = expression_string.split("<-")[1]
        self.insert(
            name = expression_string,
            data_type=None,
            semantic_type="attribute_assignation",
            value=value_str,
            default_value=None,
            start_line=current_line,
            finish_line=current_line,
            scope=current_scope,
            is_function=None,
            parameters=None,
            parameter_passing_method=None,
            node=node
            )
        return current_line 

    def parent_method_call_expr_symbol(self, node: Node, current_scope: Scope, current_line: int)-> int:
        print(1)
        return current_line

    def delete_content(self, name: str, scope: Scope=None)-> bool:
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

    def insert(self, name, data_type, semantic_type, value, default_value, start_line = None, finish_line = None, scope = None, is_function = False, parameters = [], parameter_passing_method = None, node = None, can_inherate = False):
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
        symbol = Symbol(name = name, value = value, node=node, default_value=default_value,data_type = data_type,semantic_type=semantic_type, start_line=start_line, finish_line=finish_line,scope=scope.scope_id, is_function = is_function, parameters=parameters, parameter_passing_method=parameter_passing_method, can_inherate=can_inherate)
        scope.add_content(symbol)
        self.content[scope.scope_id][symbol.name] = symbol
        return symbol

    def search(self, name, scope = None):
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
            if item==None:
                scope = scope.get_parent()
            else:
                found_item = True

        return item

    def start_scope(self, parent_scope = None, scope_id = None):
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
    
    
    def check_inhertance_chain(self, class_name) -> tuple:
        classes = self.global_scope.get_all_classees()
        if class_name not in classes:
            msg = f"OutOfScope: {class_name} not defined in global scope"
            print(msg) # Comentar o eliminar despues 
            return msg, True, [class_name], class_name

        class_chain = [class_name]
        class_object: Symbol = classes.get(class_name)


        while class_object.name != "Object":

            next_class = class_object.data_type
            

            if next_class not in classes:
                return f"InhertanceMissingFather: Missing parent class reference of class \"{class_object}\", called \"{next_class}\"", True, class_chain, class_object.name

            next_class_object:Symbol = classes.get(next_class)

            if next_class in class_chain:
                class_chain.append(next_class)
                return f"InhertanceRecursive: Found circular reference on {next_class} class.", True, class_chain, next_class

            if not next_class_object.can_inherate:
                return f"NotAllowedInhertance: Class {class_object.name} cannot inherate from {next_class} special class.", True, class_chain, class_object.name
 
            class_chain.append(next_class)
            class_object = next_class_object

            

        return "", False, class_chain, None


    # Pendiente implementar el contenido dentro de los metodos 
    def __build_basic_classes(self)->Dict[str, Symbol]:
        # Object
        self.insert(name = "Object", data_type=None, semantic_type="class", can_inherate=True, scope=self.global_scope, value=None, default_value=None)
        object_scope = self.start_scope(self.global_scope, scope_id=f"{self.global_scope.scope_id}-Object(class)")
        # abort()
        self.insert(name = "abort", data_type="Object", semantic_type="method", can_inherate=None, scope=object_scope, value=None, default_value=None, parameters=[], parameter_passing_method="value")
        # type_name()
        self.insert(name = "type_name", data_type="String", semantic_type="method", can_inherate=None, scope=object_scope, value=None, default_value=None, parameters=[], parameter_passing_method="value")
        # copy()
        self.insert(name = "copy", data_type="SELF_TYPE", semantic_type="method", can_inherate=None, scope=object_scope, value=None, default_value=None, parameters=[], parameter_passing_method="value")


        # IO
        self.insert(name= "IO", data_type="Object", semantic_type="class", can_inherate=True, value=None, default_value=None)
        IO_scope = self.start_scope(self.global_scope, scope_id=f"{self.global_scope.scope_id}-IO(class)")
        # out_string(x: String) : SELF_TYPE
        self.insert(name = "out_string", data_type="SELF_TYPE", semantic_type="method", can_inherate=None, scope=IO_scope, value=None, default_value=None, parameters=[("x", "String")], parameter_passing_method="value")
        IO_out_string_scope = self.start_scope(IO_scope, f"{IO_scope.scope_id}-out_string(method)")
        self.insert(name = "x", data_type="String", semantic_type="formal", can_inherate=None, scope=IO_out_string_scope, value=None, default_value="", parameters=None)
        # out_int(x: Int): SELF_TYPE
        self.insert(name = "out_int", data_type="SELF_TYPE", semantic_type="method", can_inherate=None, scope=IO_scope, value=None, default_value=None, parameters=[("x", "Int")], parameter_passing_method="value")
        IO_out_int_scope = self.start_scope(IO_scope, f"{IO_scope.scope_id}-out_int(method)")
        self.insert(name="x", data_type="Int", semantic_type="formal", can_inherate=None, scope=IO_out_int_scope, value=None, default_value=0, parameters=None, parameter_passing_method=None)
        # in_string() : String
        self.insert(name = "in_string", data_type="String", semantic_type="method", can_inherate=None, scope=IO_scope, value=None, default_value="", parameters=[], parameter_passing_method="value")
        # in_int(): Int
        self.insert(name = "in_int", data_type="Int", semantic_type="method", can_inherate=None, scope=IO_scope, value=None, default_value=0, parameters=[], parameter_passing_method="value")

        # Int
        self.insert(name= "Int", data_type="Object", semantic_type="class", can_inherate=False, value=None, default_value=0, scope=self.global_scope)
        Int_scope = self.start_scope(parent_scope=self.global_scope, scope_id=f"{self.global_scope.scope_id}-Int(class)")
        # String
        self.insert(name="String", data_type="Object", semantic_type="class", can_inherate=False, value=None, default_value="", scope=self.global_scope)
        StringScope = self.start_scope(self.global_scope, f"{self.global_scope.scope_id}-String(class)")

        # length() : Int
        self.insert(name="length", data_type="Int", semantic_type="method", can_inherate=None, scope=StringScope, value=None, default_value=0, parameters=[], parameter_passing_method="value")
        # concat(s: String) :String
        self.insert(name="concat", data_type="String", semantic_type="method", can_inherate=None, scope=StringScope, value=None, default_value="", parameters=[("s", "String")])
        StringConcatScope = self.start_scope(StringScope, f"{StringScope.scope_id}-concat")
        self.insert(name="s", data_type="String", semantic_type="formal", can_inherate=None, scope=StringConcatScope, value=None, default_value="")
        # substr(i: Int, l: Int) : String
        self.insert(name="substr", data_type="String", semantic_type="method", can_inherate=None, scope=StringScope, value=None, default_value=0, parameters=[("i", "Int"), ("l", "Int")],parameter_passing_method="value")
        StringSubstrScope = self.start_scope(StringScope, f"{StringScope.scope_id}-substr")
        self.insert(name="i", data_type="Int", semantic_type="formal", can_inherate=None, scope=StringSubstrScope, value=None, default_value=0, parameters=None, parameter_passing_method=None )
        self.insert(name="l", data_type="Int", semantic_type="formal", can_inherate=None, scope=StringSubstrScope, value=None, default_value=0, parameters=None, parameter_passing_method=None)
        # Bool
        Int_scope = self.start_scope(parent_scope=self.global_scope, scope_id=f"{self.global_scope.scope_id}-Bool(class)")
        self.insert(name="Bool", data_type="Object", semantic_type="class", can_inherate=False, value=None, default_value=False, scope=self.global_scope)

    def check_or_get_default_scope(self, scope: Scope):
        """Revisa la validez de un scope y en caso no lo sea, devuelve el global para ser utilizado.

        Args:
            scope (Scope): Scope que se desea comprobar validez/utilizar.

        Returns:
            Scope: Un Scope valido, ya sea el original (de ser válido), o el global por default.
        """
        if scope == None:
            return self.global_scope

        if scope.scope_id not in self.scopes:
            return self.global_scope
        return scope
    
    @staticmethod
    def get_expresion_to_str(expr_node: Node)-> str:
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
                    content.append(SymbolTable.get_expresion_to_str(child))
                return "".join(content)

            return expr_node.name
        else:
            return expr_node

    @staticmethod
    def evaluate_expr(exp_node):
        

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
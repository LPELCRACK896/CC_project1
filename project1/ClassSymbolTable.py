from dataclasses import dataclass, field
from collections import defaultdict
from prettytable import PrettyTable
from typing import List
import anytree

@dataclass
class Symbol:
    """Representa un simbolo en un tabla de simbolos. 
    """
    name: str
    data_type: str
    semantic_type:str
    line: str
    value: any = None
    memory_position: int = None
    scope: str = None
    is_function: bool = False
    parameters: List[str] = field(default_factory=list)  
    parameter_passing_method: str = None  

class Scope:
    """Representa un espacio en una tabla de simbolos y son el objeto que tiene una referencia directa a simbolos. Estos a su vez pueden tener scopes padres. 
    """
    def __init__(self, parent = None, scope_id = "global") -> None:
        """Metodo constructor

        Args:
            parent (Scope): Scope padre, poner none si este es un scope sin padre (como un scope global). Defaults to None.
            scope_id (str): Nombre que identifica al scope en este contexto, puede ser el nombre de la clase o metodo que inicio el scope. Defaults to "global".
        """
        self.parent:Scope = parent
        self.scope_id = scope_id  # identificador de alcance
        self.content = {}

    def get_parent(self):
        """Devuelve el scope padre. None en caso no tenga. 

        Returns:
            Scope: Devuelve el scope padre. None en caso no tenga. 
        """
        return self.parent

    def add_content(self, symbol: Symbol)-> Symbol:
        """Añade un símbolo al scope. 

        Args:
            symbol (Symbol): Simbolo con el mayor número de atributos posibles. 

        Returns:
            Symbol: El símbolo añadido
        """
        self.content[symbol.name] = symbol
        return symbol

    def search_content(self, name: str)->Symbol:
        """En base al nombre del símbolo, lo busca dentro del scope. 

        Args:
            name (str): Nombre del Symbol. 

        Returns:
            Symbol: Simbolo buscado o None en caso no es encuentre. 
        """
        if name in self.content:
            return self.content[name]
        return None
    
    def delete_content(self, name: str) -> bool:
        """Utilizando el nombre como referencia, borra el simbolo del scope

        Args:
            name (str): Nombre del Symbol. 

        Returns:
            bool: Indica si la operación se realizo correctamente. False en caso no haya encontrado el item. 
        """
        if name in self.content:
            del self.content[name]
            return True 
        return False      

class SymbolTable:
    def __init__(self, root):
        """Método constructor

        Args:
            root (anytree.Node): Nodo raiz del árbol de análisis sintáctico generado por anytree para la gramática. 
        """
        self.content = defaultdict(dict)  # {<scope_id>: {symbol_name: Symbol}} >>  Diccionario con clave el id_scope y valor un diccionario con simbolos (diccionario interno, identificador de simbolo como clave; Objeto Simbolo como valor)
        self.global_scope = Scope(parent=None, scope_id = "global") # La tabla de simbolos de inicializa con un scope global en el que se almacenan simbolos que no esten debajo de otros scopes creados. 
        self.scopes = { "global": self.global_scope } # {<scope_id>: Scope} >> Scopes de la tabla almacenados en dicionarios que tiene por clave su identificador y su objeto por valor. 
        self.build_symbol_table(root, current_scope=self.global_scope) # Construye recursivamente la tabla de simbolos

    def __str__(self)-> str:
        """Crea una version bonita y para consola de la tabla. 

        Returns:
            str: Tabla estetica. 
        """
        table = PrettyTable()
        table.field_names = ["Scope", "Name", "Semantic Type", "Value", "Data type", "Parameters"]
        for scope_id,  symbols in self.content.items():
            for symbol_name, symbol in symbols.items():
                table.add_row([scope_id, symbol_name, symbol.semantic_type, self.__get_expresion_to_str(symbol.value) if symbol.value else symbol.value, symbol.data_type, symbol.parameters])
        return str(table)

    def __check_or_get_default_scope(self, scope: Scope):
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
    
    def __get_expresion_to_str(self, expr_node: anytree.Node)-> str:
        """Convierte Nodos de anytree con nombre expr en su valor to string deconstruyendo el valor de sus hijos. 

        Args:
            expr_node (anytree.Node): Nodo base que referencia a demas nodos parte de la expresion. 

        Returns:
            str: Version to string del nodo. 
        """
        if isinstance(expr_node, anytree.Node):
            children = expr_node.children
            if expr_node.name == "expr":
                content = []
                for child in children:
                    content.append(self.__get_expresion_to_str(child))
                return "".join(content)     
            
            return expr_node.name
        else:
            return expr_node

    def __get_parameters_from_method(self, method_node: anytree.Node) -> List[tuple]:
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

    def build_symbol_table(self, node, current_scope = None):
        """Construye la tabla de simbolos. Al encontrar metodos o clases inicializa Scopes y llama recursivamente sobre los hijos de ese nodo. 

        Args:
            node (anytree.Node): Nodo el cual se deasea ubicar en tabla de simbolos. 
            current_scope (scope_actual, optional): En el cual se desea estableceer el nodo. Defaults to None.
        """
        if node.name == "program":
            for child in node.children:
                self.build_symbol_table(child, current_scope)

        elif node.name == "classDef":
            parent_class = "Object"
            children = node.children
            if len(children)>4:
                if children[2].name == 'inherits':
                    parent_class = children[3].name

            class_name = node.children[1].name
            self.insert(name = class_name, data_type = parent_class, semantic_type="class", value=None,line = None, scope = current_scope)

            current_scope = self.start_scope(parent_scope=current_scope, scope_id=class_name)

            for child in node.children:
                self.build_symbol_table(child, current_scope)

            current_scope = current_scope.get_parent()

        elif node.name == "method":
            method_name = node.children[0].name
            method_return_type = node.children[5].children[0].name
            param_types = [param.children[0].name for param in node.children[2].children]
            full_signature = f"method -> ({', '.join(param_types)}) -> {method_return_type}"
            method_scope_id = f"{current_scope.scope_id}"

            method_scope = self.start_scope(parent_scope=current_scope, scope_id=method_scope_id)
            parameters = self.__get_parameters_from_method(node)

            self.insert(name = method_name, semantic_type="method", data_type = full_signature, value=None, line = None, scope = method_scope, parameters=parameters, is_function=True )

            for child in node.children:
                self.build_symbol_table(child, method_scope)

            current_scope = method_scope.get_parent()

        elif node.name == "attr":
            children = node.children
            attr_name = children[0].name
            attr_type = children[2].children[0].name
            attr_value =  children[-2] if len(children)>3 else None

            self.insert(name = attr_name, data_type=attr_type, semantic_type="attr" ,value=attr_value, line=None, scope=current_scope, is_function=False, parameters=[], parameter_passing_method=None,  )
        else:
            for child in node.children:
                self.build_symbol_table(child, current_scope)

    def delete_content(self, name: str, scope: Scope=None)-> bool: 
        """Utilizando el nombre del simbolo eliminar toda referencia del simbolo en el objeto. 

        Args:
            name (str): Nombre del símbolo. 
            scope (Scope, optional): Objeto scope en el que se espera encontrar el simbolo. Defaults to None.

        Returns:
            bool: Indica si la operación se realizó con éxito. True si se elimino, False si no lo encontro en el scope. 
        """
        scope: Scope = self.__check_or_get_default_scope(scope)
        if name in self.content[scope.scope_id]:
            del self.content[scope.scope_id][name]
            scope.delete_content(name)  
            return True  
        return False  
    
    def insert(self, name, data_type, semantic_type, value, line = None, scope = None, is_function = False, parameters = [], parameter_passing_method = None):
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
        scope = self.__check_or_get_default_scope(scope)
        symbol = Symbol(name = name, value = value, data_type = data_type,semantic_type=semantic_type, line=line, scope=scope.scope_id, is_function = is_function, parameters=parameters, parameter_passing_method=parameter_passing_method)
        scope.add_content(symbol)
        self.content[scope.scope_id][symbol.name] = symbol  # <- Change here
 
    def search(self, name, scope = None):
        """Busca por nombre el símbolo en la tabla partiendo de un scope. En caso de encontrarlo en el actual expande la busqueda al padre. 

        Args:
            name (str): _description_
            scope (Scope, optional): Scope sobre el que se espera encontrar . Defaults to None.

        Returns:
            Symbol: El simbolo buscado con todos su atributos. 
        """
        scope: Scope = self.__check_or_get_default_scope(scope)
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
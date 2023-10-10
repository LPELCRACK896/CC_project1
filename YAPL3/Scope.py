from Symbol import Symbol
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple
from collections import namedtuple

Error = namedtuple('Error', ['name', 'details', "symbol", "scope", "line"])


class Scope:
    """Representa un espacio en una tabla de simbolos y son el objeto que tiene una referencia directa a simbolos. Estos a su vez pueden tener scopes padres. 
    """

    def __init__(self, parent=None, scope_id="global") -> None:
        """Metodo constructor

        Args:
            parent (Scope): Scope padre, poner none si este es un scope sin padre (como un scope global). Defaults to None.
            scope_id (str): Nombre que identifica al scope en este contexto, puede ser el nombre de la clase o metodo que inicio el scope. Defaults to "global".
        """
        self.parent: Scope | None = parent
        self.scope_id = scope_id  # identificador de alcance
        self.content = {}

    def has_higher_hierarchy(self, other_scope):
        return not self.scope_id.startswith(other_scope.scope_id)

    def get_parent(self):
        """Devuelve el scope padre. None en caso no tenga. 

        Returns:
            Scope: Devuelve el scope padre. None en caso no tenga. 
        """
        return self.parent

    def add_content(self, symbol: Symbol) -> Tuple[Symbol, Error | None]:
        """Añade un símbolo al scope. 

        Args:
            symbol (Symbol): Simbolo con el mayor número de atributos posibles. 

        Returns:
            Symbol: El símbolo añadido
        """

        if symbol.name in self.get_all_variables_declarations_symbols():
            error = Error(
                name="Repeated Declaration::",
                details=f"Identifier \"{symbol.name}\" tried to be declared on same scope. Was already declared in line {self.get_all_variables_declarations_symbols()[symbol.name].start_line} as {self.get_all_variables_declarations_symbols()[symbol.name].data_type} type.",
                symbol=symbol,
                scope=self,
                line=symbol.start_line
            )
            return symbol, error

        self.content[symbol.name] = symbol
        return symbol, None

    def search_content(self, name: str) -> Symbol:
        """En base al nombre del símbolo, lo busca dentro del scope. 

        Args:
            name (str): Nombre del Symbol. 

        Returns:
            Symbol: Simbolo buscado o None en caso no es encuentre. 
        """
        if name in self.content:
            return self.content[name]
        return None

    @staticmethod
    def search_symbol_in_content(symbol_name: str, content: Dict[str, Symbol]) -> Symbol | None:
        if symbol_name in content:
            return content[symbol_name]
        return None

    @staticmethod
    def filter_symbols_expr_by_type_of_expression(type_of_expression, content: Dict[str, Symbol]) -> Dict[str, Symbol]:
        return {symbol_alias: symbol for symbol_alias, symbol in content.items()
                if symbol.semantic_type == "expression" and symbol.type_of_expression == type_of_expression}

    @staticmethod
    def filter_symbols_by_semantic_type(semantic_type, content: Dict[str, Symbol]) -> Dict[str, Symbol]:
        return {symbol_alias: symbol for symbol_alias, symbol in content.items()
                if symbol.semantic_type == semantic_type}

    def get_declarations(self, declaration_type="variable"):
        if declaration_type not in ["variable", "method", "class"]:
            return None

        if declaration_type == "variable":
            return self.get_all_variables_declarations_symbols()

        elif declaration_type == "method":
            return self.get_all_methods()

        elif declaration_type == "class":
            return self.get_all_classes()

    def get_all_variables_declarations_symbols(self):
        let_variables = self.filter_symbols_expr_by_type_of_expression("declaration_assignation", self.content)
        method_formals = self.filter_symbols_by_semantic_type("formal", self.content)
        class_attributes = self.filter_symbols_by_semantic_type("attr", self.content)

        all_declarations = {**let_variables, **method_formals, **class_attributes}

        return all_declarations

    def search_availabilty_of_content(self, name: str) -> (Symbol, str):
        """En base al nombre del símbolo, busca dentro del scope. Si no lo enceuntra lo busca en su padre (recursivo).

        Args:
            name (str): Nombre del Symbol. 

        Returns:
            tuple: (Simbolo buscado o none: Symbol, Ultimo scope donde busco: str)
        """
        content = self.search_content(name)

        if content == None and self.parent != None:
            return self.parent.search_availabilty_of_content(name)

        return content, self.scope_id

    def get_all_classes(self):
        return {name: symbol for name, symbol in self.content.items() if symbol.semantic_type == "class"}

    def get_all_attributes(self):
        return {name: symbol for name, symbol in self.content.items() if symbol.semantic_type == "attr"}

    def get_all_methods(self):
        return {name: symbol for name, symbol in self.content.items() if symbol.semantic_type == "method"}

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

    def get_scope_chain(self):
        """Get a string that contains the scope_ids from the current scope
        up to the root scope, separated by underscores."""
        scope_chain = []
        current_scope = self

        while current_scope is not None:
            scope_chain.append(current_scope.scope_id)
            current_scope = current_scope.get_parent()

        return "_".join(reversed(scope_chain))

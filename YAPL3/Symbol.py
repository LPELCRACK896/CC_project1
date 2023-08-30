from dataclasses import dataclass, field
import anytree
from typing import List


    
@dataclass
class Symbol:
    """Representa un simbolo en un tabla de simbolos. 
    """
    name: str
    data_type: str
    semantic_type:str
    node: anytree.Node = None
    default_value: any = None
    is_local_scope: bool = False 
    start_index: str = None
    end_index: str = None
    start_line: str = -1
    end_line: str = 0
    value: any = None
    memory_position: int = None
    scope: str = None
    is_function: bool = False
    parameters: List[str] = field(default_factory=list)  
    parameter_passing_method: str = None  
    can_inherate: bool = False


    def get_value(self):
        if self.value == None:
            if not self.data_type:
                return None
            if self.data_type == "Int" or self.data_type == "String" or self.data_type == "Bool" :   
                return self.default_value
        return get_expresion_to_str(self.value)
    


def get_expresion_to_str(expr_node: anytree.Node)-> str:
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
                content.append(get_expresion_to_str(child))
            return "".join(content)

        return expr_node.name
    else:
        return expr_node
from dataclasses import dataclass, field
import anytree
from typing import List
import bytes_required as br


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
    type_of_expression: str = None
    bytes_memory_size: int = None



    def get_value(self):
        if self.value == None:
            if not self.data_type:
                return None
            if self.data_type == "Int" or self.data_type == "String" or self.data_type == "Bool" :
                return self.default_value
        return get_expresion_to_str(self.value)

    def estimate_memory_size(self):
        if self.semantic_type == "class":
            self.bytes_memory_size = self.get_class_size()
        elif self.semantic_type == "expression":
            self.bytes_memory_size = self.get_expression_size()
        elif self.semantic_type == "method":
            self.bytes_memory_size = self.get_method_size()
        elif self.semantic_type == "formal":
            self.bytes_memory_size = self.get_formal_size()
        elif self.semantic_type == "attr":
            self.bytes_memory_size = self.get_attr_size()


    def get_class_size(self):
        # Default return
        return 1

    def get_expression_size(self):
        # Default return
        return 1

    def get_method_size(self):
        # Default return
        return 1

    def get_formal_size(self):
        total_size = 0

        # First add the necessary memory to the data according its type
        if self.data_type in br.basic_types_data_required:
            total_size += br.basic_types_data_required.get(self.data_type)
        else:
            print(f"Unable to set memory size for formal {self.name}. Unidentified type: {self.data_type}")

        # Add memory necessary for other meta-data
        # Pending code
        return total_size

    def get_attr_size(self):
        total_size = 0

        # First add the necessary memory to the data according its type
        if self.data_type in br.basic_types_data_required:
            total_size += br.basic_types_data_required.get(self.data_type)
        else:
            print(f"Unable to set memory size for formal {self.name}. Unidentified type: {self.data_type}")

        # Add memory necessary for other meta-data
        # Pending code
        return total_size
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

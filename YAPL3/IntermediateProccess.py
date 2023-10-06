from SymbolTable import SymbolTable
from IntermediateCode import *

generative = {
    "general_scope_quadruples": general_scope_quadruples,
}


def build_cuadruples(symbol_table: SymbolTable = None, generative_rules=generative):
    quadruples = []
    for rule, method in generative_rules.items():
        quadruple = method(symbol_table)
        quadruples.extend(quadruple)
        #print(rule, " >>> ", quadruple)
    return quadruples


# Pruebas
if __name__ == "__main__":
    # You need to create a SymbolTable instance here
    symbol_table = SymbolTable(root=None)
    quadruples = build_cuadruples(symbol_table)
    print(quadruples)

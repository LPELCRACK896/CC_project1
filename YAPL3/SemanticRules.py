from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, SemanticFeedBack
from SemanticRules import *


def not_implemented_true(symbol_table: SymbolTable = None)-> (bool, SemanticFeedBack):
    print("REGLA DEBE SER IPMLEMENTADA, METODO TEMPORAL")
    return True, [SemanticError(name="Unimplemented", details = "Must implmeent method, rather than use this function.", symbol=None, scope=None)]

def not_implemented_false(symbol_table: SymbolTable = None)-> (bool, SemanticFeedBack) :
    print("REGLA DEBE SER IPMLEMENTADA, METODO TEMPORAL")
    return False, [SemanticError(name="Unimplemented", details = "Must implmeent method, rather than use this function.", symbol=None, scope=None)]

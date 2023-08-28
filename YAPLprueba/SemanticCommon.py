from dataclasses import dataclass
from ClassSymbolTable import SymbolTable, Symbol, Scope
from typing import Callable, Dict, List


@dataclass
class SemanticError:
    name: str
    details: str
    symbol: Symbol
    scope: Scope


ActiveRulesType = Dict[str, Callable]
SemanticFeedBack = List[SemanticError]


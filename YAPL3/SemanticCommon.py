from dataclasses import dataclass
from Symbol import Symbol
from Scope import Scope
from typing import Callable, Dict, List


@dataclass
class SemanticError:
    name: str
    details: str
    symbol: Symbol
    scope: Scope
    line: str


ActiveRulesType = Dict[str, Callable]

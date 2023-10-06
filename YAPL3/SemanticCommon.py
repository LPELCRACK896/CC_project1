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

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.details == other.details and
            self.symbol == other.symbol and
            self.scope == other.scope and
            self.line == other.line
        )

ActiveRulesType = Dict[str, Callable]

from typing import AnyStr, Dict
from Symbol import Symbol
from Scope import Scope


class Direction:

    content: AnyStr | Symbol
    scopes: Dict[AnyStr, Scope]

    def __init__(self, content: AnyStr | Symbol, scopes: Dict[AnyStr, Scope]):
        self.content = content
        self.scopes = scopes

    def update_real_tag(self, real_tag: str):
        self.content = real_tag

    def replace_tag(self, new_tag: AnyStr):
        self.content = new_tag

    def is_reference(self):
        return isinstance(self.content, Symbol)

    def is_temporary_variable(self):
        return not self.is_reference()

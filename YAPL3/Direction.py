from typing import AnyStr, Dict
from Symbol import Symbol
from Scope import Scope
from Operation import Operation


class Direction:

    content: AnyStr
    scopes: Dict[AnyStr, Scope]

    def __init__(self, content: AnyStr, scopes: Dict[AnyStr, Scope]):
        self.content = content
        self.scopes = scopes

    def __str__(self) -> str:

        return str(self.content)

    def update_real_tag(self, real_tag: str):
        self.content = real_tag

    def replace_tag(self, new_tag: AnyStr):
        self.content = new_tag

    def is_reference(self):
        return self.content.startswith("<DIR>")

    def is_temporary_variable(self):
        return not self.is_reference()

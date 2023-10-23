from typing import Dict, AnyStr


class Operation:
    type_of_operation: str

    def __init__(self, type_of_operation: AnyStr | None):
        self.type_of_operation = type_of_operation


    def __str__(self):
        if self.type_of_operation is None:
            return ""

        if len(self.type_of_operation) > 5:
            return str(self.type_of_operation[:6]).upper()

        return f"{self.type_of_operation}"

    def is_sum(self):
        return str(self.type_of_operation) == "SUM"

    def is_div(self):
        return str(self.type_of_operation) == "DIV"

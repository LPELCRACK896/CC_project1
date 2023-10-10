from typing import Dict, AnyStr


class Operation:
    type_of_operation: str
    translation_operation_to_str: Dict[AnyStr, AnyStr]

    def __init__(self, type_of_operation: AnyStr | None):
        self.type_of_operation = type_of_operation
        self.translation_operation_to_str = \
            {
                "assign": "ASS",
            }

    def __str__(self):
        if self.type_of_operation is None:
            return ""

        if len(self.type_of_operation) > 5:
            return str(self.type_of_operation[:5]).upper()

        return f"{self.type_of_operation}"

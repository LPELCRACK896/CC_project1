from typing import Dict, AnyStr


class Operation:
    type_of_operation: str
    translation_operation_to_str: Dict[AnyStr, AnyStr]

    def __init__(self, type_of_operation):
        self.type_of_operation = type_of_operation
        self.translation_operation_to_str = \
            {
                "if": "if",
                "assign": "="
            }

    def __str__(self):
        if self.type_of_operation in self.translation_operation_to_str:
            return f"{self.translation_operation_to_str[self.type_of_operation]}"

        return f"{self.type_of_operation}"

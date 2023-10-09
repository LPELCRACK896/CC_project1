from typing import AnyStr, Dict
from Direction import Direction
from Operation import Operation

class Register:
    tag: AnyStr
    first_direction: Direction | None
    second_direction: Direction | None
    third_direction: Direction | None

    temporary_tag_count: int

    first_operation: Operation
    second_operation: Operation

    temporary_tag_equivalences: Dict[AnyStr, AnyStr]  # Type of waiting instruction: Temporary

    def __init__(self, first_direction, second_direction, third_direction, first_operation_alias: AnyStr, second_operation_alias: AnyStr):
        self.first_direction = first_direction
        self.second_direction = second_direction
        self.third_direction = third_direction

        self.first_operation = Operation(first_operation_alias)
        self.second_operation = Operation(second_operation_alias)

        self.temporary_tag_equivalences = {}
        self.temporary_tag_count = 1

    def __str__(self):
        if self.first_direction and self.second_direction and self.third_direction:
            return f"{self.first_direction} {self.first_operation}" \
                   f" {self.second_direction} {self.second_operation} {self.third_direction}"

        elif self.first_direction and self.second_direction:
            return f"{self.first_direction} {self.first_operation} {self.second_direction}"

        # Is possible any other variant???

    def create_temporary_tag(self, waiting_tag_reference):
        temporary_tag = f"TT{self.temporary_tag_count}"
        self.temporary_tag_equivalences[waiting_tag_reference] = temporary_tag
        self.temporary_tag_count += 1

    def listen_outside_tag(self, tag_reference: str, real_tag: str):
        if tag_reference in self.temporary_tag_equivalences:
            self.try_to_update_directions_tags(tag_reference, real_tag)
            self.temporary_tag_equivalences.pop(tag_reference)

    def try_to_update_directions_tags(self, tag_reference: str, real_tag: str):
        self.try_to_update_direction(self.first_direction, tag_reference, real_tag)
        self.try_to_update_direction(self.second_direction, tag_reference, real_tag)
        self.try_to_update_direction(self.third_direction, tag_reference, real_tag)

    @staticmethod
    def try_to_update_direction(direction: Direction, tag_reference: str, real_tag: str):
        if direction.content == tag_reference:
            direction.update_real_tag(real_tag)

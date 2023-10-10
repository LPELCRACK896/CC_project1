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

    def __init__(self, tag: str, first_direction: Direction):
        self.first_direction = first_direction
        self.second_direction = None
        self.third_direction = None

        self.first_operation: Operation = None
        self.second_operation: Operation = None
        self.tag = tag

    def set_first_operation(self, operation: Operation):
        self.first_operation = operation

    def set_second_operation(self, operation: Operation):
        self.second_operation = operation

    def set_first_direction(self, direction: Direction):
        self.first_direction = direction

    def set_second_direction(self, direction: Direction):
        self.second_direction = direction

    def set_third_direction(self, direction: Direction):
        self.third_direction = direction

    def __str__(self):
        if self.first_direction and self.second_direction and self.third_direction:
            return f"\t{self.tag} {self.first_direction} {self.first_operation}" \
                   f" {self.second_direction} {self.second_operation} {self.third_direction}"

        elif self.first_direction and self.second_direction:
            return f"\t{self.tag} {self.first_direction} {self.first_operation} {self.second_direction}"

        if self.tag.startswith("CL"):
            return f"{self.tag} {self.first_operation} {self.first_direction}"
        else:
            return f"\t{self.tag} {self.first_operation} {self.first_direction}"
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

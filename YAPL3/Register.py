from typing import AnyStr, Dict
from Direction import Direction
from Operation import Operation


class Register:
    tag: AnyStr
    first_direction: Direction | None
    second_direction: Direction | None
    third_direction: Direction | None

    temporary_tag_count: int

    first_operation: Operation | None
    second_operation: Operation | None
    third_operation: Operation | None

    temporary_tag_equivalences: Dict[AnyStr, AnyStr]  # Type of waiting instruction: Temporary

    def __init__(self, tag: str, first_direction: Direction):
        self.first_direction = first_direction
        self.second_direction = None
        self.third_direction = None

        self.first_operation: Operation | None = None
        self.second_operation: Operation | None = None
        self.third_operation: Operation | None = None
        self.tag = tag

    def set_first_operation(self, operation: Operation):
        self.first_operation = operation

    def set_second_operation(self, operation: Operation):
        self.second_operation = operation

    def set_third_operation(self, operation: Operation):
        self.third_operation = operation

    def set_first_direction(self, direction: Direction):
        self.first_direction = direction

    def set_second_direction(self, direction: Direction):
        self.second_direction = direction

    def set_third_direction(self, direction: Direction):
        self.third_direction = direction

    def __str__(self):
        prefix = "\t" if not self.tag.startswith("CL") else ""

        if self.only_one_of_each():
            return f"{prefix}{self.tag} " \
                   f"{self.first_operation} {self.first_direction} "

        if self.has_all():
            return f"{prefix}{self.tag} " \
                   f"{self.first_direction} {self.first_operation} " \
                   f"{self.second_operation} {self.second_direction} " \
                   f"{self.third_operation} {self.third_direction} "

        return f"{prefix}{self.tag} " \
               f"{self.str_if_exist(self.first_direction)} {self.str_if_exist(self.first_operation)} " \
               f"{self.str_if_exist(self.second_direction)} {self.str_if_exist(self.second_operation)} " \
               f"{self.str_if_exist(self.third_direction)}"

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

    def only_one_of_each(self):
        return (
            self.first_direction is not None and
            self.first_operation is not None and

            self.second_direction is None and
            self.third_direction is None and
            self.second_operation is None and
            self.third_operation is None
        )

    def has_all(self):
        return (
                self.first_direction is not None and
                self.first_operation is not None and

                self.second_direction is not None and
                self.third_direction is not None and
                self.second_operation is not None and
                self.third_operation is not None
        )
    @staticmethod
    def try_to_update_direction(direction: Direction, tag_reference: str, real_tag: str):
        if direction.content == tag_reference:
            direction.update_real_tag(real_tag)

    @staticmethod
    def str_if_exist(item):
        if item is None:
            return ""
        return str(item)
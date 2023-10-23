from typing import AnyStr, Dict, List
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
        space_if_tag = " " if self.tag else ""
        prefix = "\t" if not self.tag.startswith("CL") else ""
        # Special cases
        if self.first_direction is not None:
            if str(self.first_operation) == "IFNOT":
                return f"{prefix}{self.tag}{space_if_tag}" \
                       f"{self.first_operation} {self.first_direction} {self.second_operation} {self.second_direction}"


        if self.only_one_of_each():
            return f"{prefix}{self.tag}{space_if_tag}" \
                   f"{self.first_operation} {self.first_direction} "

        if self.has_all():
            return f"{prefix}{self.tag}{space_if_tag}" \
                   f"{self.first_direction} {self.first_operation} " \
                   f"{self.second_operation} {self.second_direction} " \
                   f"{self.third_operation} {self.third_direction} "

        return f"{prefix}{self.tag}{space_if_tag}" \
               f"{self.str_if_exist(self.first_direction)} {self.str_if_exist(self.first_operation)} " \
               f"{self.str_if_exist(self.second_direction)} {self.str_if_exist(self.second_operation)} " \
               f"{self.str_if_exist(self.third_direction)}"

    def includes_div_or_sum(self):

        operations = [self.first_operation, self.second_operation, self.third_operation]
        for operation in operations:
            if isinstance(operation, Operation):
                if operation.is_div() or operation.is_sum():
                    return True

        return False


    def to_list_existing_directions(self) -> List[Direction]:
        return [direction for direction in [self.first_direction, self.second_direction, self.third_direction]
                if direction is not None]

    def update_directions_tag(self, old_tag: AnyStr, net_tag: AnyStr):

        directions = self.to_list_existing_directions()
        for direction in directions:
            if direction.content == old_tag:
                direction.content = net_tag

    def only_tag_and_goto(self):
        if self.first_operation is None:
            return False
        if str(self.first_operation) == "GOTO":
            pass
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

from SymbolTable import SymbolTable
from Symbol import Symbol

OPERATIONS = [
    "=",
    "ASSIGN",
    "ON",
    "PARAM",
    "CALL",
    "NEW",
    "WITH",
    "SUM",
    "MULT",
    "DIV",
    "MULT",
    "RETURN",
    "IFNOT"
]


def is_arithmetic_operation(slice_of_line):
    return (
        "MULT" in slice_of_line or
        "DIV" in slice_of_line or
        "SUM" in slice_of_line or
        "SUB" in slice_of_line
    )

def is_comparing_operation(slice_of_line):
    pass


def is_start_line_representation(item: str):
    return item.startswith("S")


def is_tag_line(item: str):
    if not item.startswith("L"):
        return False
    return item[1:].isnumeric()


def is_temporal_variable(item: str):
    if not item.startswith("t"):
        return False
    return item[1:].isnumeric()


def is_an_attribute(item: str):
    split_item = item.split(".")
    if len(split_item) != 4:
        return False

    if split_item[0] != "<DIR>" or split_item[2] != "attr":
        return False

    return True


def is_an_assignation(line: str):
    parts = line.split(" ")
    if len(parts) < 2:
        return False
    return parts[1] == "ASSIGN"


def is_a_let_variable_declaration(item: str):
    split_item = item.split(".")
    if len(split_item) != 5:
        return False

    if split_item[0] != "<DIR>" or split_item[3] != "declaration_assignation":
        return False

    return True


def build_ram_name_from_tdc_direction(direction):
    parts = direction.split(".")

    class_owner = parts[1]
    type_of_direction = parts[2]

    if type_of_direction == "attr":
        name = parts[-1]
        return f"{class_owner}_attr_{name}"
        pass
    else:
        print("")

    pass


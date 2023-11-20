from typing import List, Dict, AnyStr
from Method import Method
from mips_common import *
from Prototype import Prototype
from SymbolTable import SymbolTable
from Symbol import Symbol


def get_default_mips_value(mips_type):
    if mips_type == ".word" or mips_type == ".byte":
        return 0
    return "\"\""


def to_mips_type(source_data_type):
    if source_data_type == "Int":
        return ".word"
    if source_data_type == "String":
        return ".asciiz"
    if source_data_type == "Bool":
        return ".byte"


def calculate_offset(parameter, mips_parameters):

    parameters_left = mips_parameters[:]
    for param in mips_parameters:
        parameters_left.pop(0)
        if param[0] == parameter[0]:
            break

    return len(parameters_left) * 4


def get_direction_type(direction):
    split_direction = direction.split(".")
    if split_direction[2] == "attr":
        return "attr"

    if split_direction[-2] == "formal":
        return "formal"

    return "let"


def get_direction_data_type(direction: str, symbol_table: SymbolTable):
    direction_type = get_direction_type(direction)
    split_direction = direction.split(".")

    if direction_type == "attr":
        attr_name = split_direction[-1]
        class_name = split_direction[1]
        class_symbol: Symbol = [cls for _, cls in symbol_table.get_classes().items() if cls.name == class_name][0]
        attr_symbol: Symbol = [attr for _, attr in symbol_table.class_get_attributes(class_symbol).items()
                               if attr.name == attr_name][0]
        return attr_symbol.data_type

    if direction_type == "formal":
        formal_name = split_direction[-1]
        class_name = split_direction[1]
        method_name = split_direction[2]
        class_symbol: Symbol = [cls for _, cls in symbol_table.get_classes().items() if cls.name == class_name][0]
        method_symbol: Symbol = [mthd for _, mthd in symbol_table.class_get_methods(class_symbol).items()
                                 if mthd.name == method_name][0]
        param_type = [param[1] for param in method_symbol.parameters if param[0]==formal_name][0]
        return param_type

    return None


def direction_to_data_alias(direction: str) -> str:
    """
    Three types of directions:
    - Let
    - Formals
    - Attributes
    :param direction:
    :return:
    """
    direction_type = get_direction_type(direction)
    split_direction = direction.split(".")
    var_name = split_direction[-1]
    class_name = split_direction[1]
    if direction_type == "attr":
        class_name = split_direction[1]
        return f"{class_name}_attr_{var_name}"

    method_name = split_direction[2]
    if direction_type == "formal":
        return f"{class_name}_{method_name}_formal_{var_name}"

    return None



def search_reference(alias: str, storage: Dict[str, List[Reference]], owner) -> Reference | None:
    if owner not in storage:
        return None
    variables = storage.get(owner)
    for var in variables:
        if var.alias == alias:
            return var
    return None


def get_empty_string_with_tabulations(number_of_tabulations) -> str:
    line = ""
    if number_of_tabulations < 0:
        number_of_tabulations = 0
    for _ in range(number_of_tabulations):
        line += "\t"
    return line


def find_last_usage_temporary(current_line, temporary_var, block_context):
    line = None
    start_search = False
    for ln in block_context:
        if not start_search:
            start_search = ln == current_line
        else:
            if temporary_var in ln:
                line = ln
    return line


def update_class_variables_references(variables_as_object_reference: Dict[AnyStr, List[Reference]],
                                      reference: Reference) -> Dict[AnyStr, List[Reference]]:
    owner = reference.class_owner
    if owner in variables_as_object_reference.keys():
        variables_as_object_reference[owner].append(reference)
    else:
        variables_as_object_reference[owner] = [reference]

    return variables_as_object_reference


def build_and_get_IO_prototype() -> Prototype:

    """
    out_string(x: String): SELF_TYPE
    out_int(x: Int): SELF_TYPE
    in_string(): String
    in_int(): Int
    """
    class_prototype = Prototype("IO")

    #  outString(s: String)
    prototype_out_string = Method("outString")
    prototype_out_string.set_content([
        "li $v0, 4",
        "lw $a0, 0($sp)",
        "syscall",
        "jr $ra"
    ])
    class_prototype.add_method(prototype_out_string)

    #  out_int(x: Int): SELF_TYPE
    prototype_out_int = Method("outInt")
    prototype_out_int.set_content([
        "li $v0, 1",
        "lw $a0, 0($sp)",
        "syscall",
        "jr $ra"
    ])
    class_prototype.add_method(prototype_out_int)

    # in_string()
    prototype_in_string = Method("inString")
    prototype_in_string.set_content([
        "li $v0, 8",
        "la $a0, buffer",
        "li $a1, 1024",
        "syscall",
        "jr $ra"
    ])
    class_prototype.add_method(prototype_in_string)

    # in_int()
    prototype_in_int = Method("inInt")
    prototype_in_int.set_content([
        "li $v0, 5 ",
        "syscall",
        "jr $ra"
    ])
    class_prototype.add_method(prototype_in_int)
    class_prototype.write_example()
    return class_prototype


def char_to_ascii(char):
    return ord(char)
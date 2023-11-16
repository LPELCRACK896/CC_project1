import MIPS_CONSTANTS as MC


def is_primitive(data_type):
    return data_type in MC.primitives


def identify_type_by_value(value: str):
    """
    Assumes a primitive value is being passed
    Use in simple assignaton:
    Example:
        t10 = 'hola'

    :param value:
    :return:
    """

    if value.startswith("\'") or value.startswith("\"") :
        return "String"
    if value.isnumeric():
        return "Int"
    return "Bool"


def transform_value(value: str, data_type: str):
    value = str(value)
    if data_type == "Int":
        if value.isnumeric():
            return value
        else:
            return 0

    if data_type == "String":
        value.replace("\'", "\"")
        return value

    return 1 if value == "true" else 0


def is_a_primitive_reference(dir_name, variables_as_object_reference):
    pass


def is_an_object_reference(dir_name, ):
    pass

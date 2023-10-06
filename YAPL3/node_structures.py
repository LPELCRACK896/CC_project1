from typing import Tuple, List
from dataclasses import dataclass, field

from anytree import Node

"""
-----------
IDENTIFIERS
-----------
Receives a <expr> node and returns the node_type and subtype (structure)
"""
expressions = [
    "assignment",  # ID '<-' expr
    "dynamic_dispatch",  # expr '@' (node_type | CLASS_ID) '.' ID '(' (expr (',' expr)* )?')'
    "static_dispatch",  # expr '.' ID '(' (expr (',' expr)* )? ')'
    "function_call",  # ID '(' (expr (',' expr)* )? ')'
    "conditional",  # 'if' (bool_value | expr)  'then' expr 'else' expr 'fi'
    "loop",  # 'while' (bool_value | expr) 'loop' expr 'pool'
    "block",  # '{' expr (';' expr)* '}'
    "let_in",  # 'let' ID ':' node_type ('<-' expr)? (',' ID ':' node_type ('<-' expr)?)* 'in' expr
    "object_creation",  # 'new' (CLASS_ID | node_type)
    "isvoid",  # 'isvoid' expr
    "not",  # 'not' expr
    "bitwise_not",  # '~' expr
    "arithmetic_or_comparison",  # expr op=OP expr
    "parenthesized_expr",  # '(' expr ')'
    "identifier",  # ID
    "integer",  # INT
    "string",  # STRING
    "boolean_true",  # RW_TRUE
    "boolean_false",  # RW_FALSE
    #  NONE EXPRESSION NODES #####
    "attribute"
]

operators = [
    '+',
    '-',
    '*',
    '/',
    '<',
    '<=',
    '=',
    '>=',
    '>'
]


@dataclass
class LetVariable:
    var_id: str | None = None
    var_type: str | None = None
    value: Node | None = None


def identify_node(node: Node):

    if node.name == "attr":
        return expressions.index("attribute")
    # expr
    if not node.children:
        return -1

    if node.children[0].name == "if":
        return expressions.index("conditional")

    if len(node.children) > 1:
        if node.children[1].name == "<-":
            return expressions.index("assignment")
        if node.children[1].name == "@":
            return expressions.index("dynamic_dispatch")
        if node.children[1].name == "(":
            return expressions.index("function_call")
        if node.children[1].name == ".":
            return expressions.index("static_dispatch")

    if node.children[0].name == "while":
        return expressions.index("loop")

    if node.children[0].name == "{":
        return expressions.index("block")

    if node.children[0].name == "let":
        return expressions.index("let_in")

    if node.children[0].name == "new":
        return expressions.index("object_creation")

    if node.children[0].name == "isvoid":
        return expressions.index("isvoid")

    if node.children[0].name == "not":
        return expressions.index("not")

    if node.children[0].name == "~":
        return expressions.index("bitwise_not")

    # Check for parenthesized expression
    if node.children[0].name == "(" and node.children[-1].name == ")":
        return expressions.index("parenthesized_expr")

    # Check for arithmetic or comparison expression
    if len(node.children) > 2:
        if node.children[1].name in operators:
            return expressions.index("arithmetic_or_comparison")

    if len(node.children) == 1:
        content = str(node.children[0].name)
        if starts_with_number(content):
            return expressions.index("integer")
        if content.startswith('\''):
            return expressions.index("string")
        if content == "true":
            return expressions.index("boolean_true")
        if content == "false":
            return expressions.index("boolean_false")

        return expressions.index(
            "identifier")  # Esta suposición puede necesitar ser ajustada dependiendo de la naturaleza de tus nodos.

    return -1


"""
-----------
VERIFIERS
-----------
"""


def verify_node_structure_attribute(attr_root: Node) -> int:
    """
    Ensure the attribute node contains all elements in one of the expected structures
    VALID STRUCTURE No. 1 (unassigned):
    └── attr
        ├── radius
        ├── :
        ├── node_type
        │    └── Int
        └── ;
    VALID STRUCTURE No. 2:
     └── attr
        ├── radius
        ├── :
        ├── node_type
        │   └── Int
        ├── <-
        ├── expr
        │   └── 10
        └── ;

    Children:
    0 - Attribute name
    1 - :
    2 - <node_type>
        0 - (String | Int | ... |)
    3 - <-
    4 - <expr>
    :param attr_root: the attribute node
    :return:The number of structure or -1 in case of not having any of those
    """
    children = attr_root.children

    if len(children) < 4:
        return -1

    if children[1].name != ":":
        return -1

    attr_type_node = children[2]

    if len(attr_type_node.children) < 1:
        return -1

    if len(children) == 4:
        return 1

    if len(children) != 6:
        return -1

    expr_node = children[4]
    return 2


def verify_node_structure_while(node: Node) -> int:
    """
    Ensure the expression node that contains all elements related to while loop has a valis structure.
    VALID STRUCTURE No. 1 (bool_value as condition):
    ├── <expr>
    │   ├── while
    │   ├── <bool_value>
    │   │   └── etc
    │   ├── loop
    │   ├── <expr>
    │   │   └── etc
    │   └── pool
    VALID STRUCTURE No. 2 (expr as condition):
    ├── expr
    │   ├── while
    │   ├── <expr>
    │   │   ├── etc...
    │   │   │
    │   │   └── etc...
    │   ├── loop
    │   ├── <expr>
    │   │   ├── etc...
    │   │   │
    │   │   └── etc...
    │   └── pool
    Children:
    0 - "while"
    1 - Condition: <expr> | <bool_value>
    2 - "loop"
    3 - Looped expression: <expr>
    4 - "pool"
    :param node: expr node that contains while
    :return:The number of structure or -1 in case of not having any of those
    """

    if len(node.children) != 5:
        return -1

    key_word_while = node.children[0]
    condition = node.children[1]  # Either bool_value or expr
    key_word_loop = node.children[2]
    looped_expression = node.children[3]
    key_word_pool = node.children[4]

    if (key_word_while.name != "while"
            or key_word_loop.name != "loop"
            or key_word_pool.name != "pool"
            or looped_expression.name != "expr"):
        return -1

    if condition.name == "bool_value":
        return 1
    if condition.name == "expr":
        return 2
    return -1


def verify_node_structure_let(node: Node):
    """
    Ensure the expression node that contains all elements related to while loop has a valis structure.
    VALID STRUCTURE No. 1 (bool_value as condition):
    ├── expr
    │   ├── let
    │   ├── ID
    │   ├── :
    │   ├── node_type
    │   │   └── Int
    │   ├── <-
    │   ├── <expr>
    │   │   ...
    │   ├── in
    │   ├── [
    │   ├── <expr>
    │   │   ├── etc...
    │   └── ]
    """
    let_content = list(node.children)
    let_content.pop(0)  # Remove initial "let"

    found_in = False
    empty_stack = len(let_content) > 0
    number_of_local_variables = 0

    item = let_content.pop(0)

    while not (found_in and empty_stack):
        if item.name == "in":
            found_in = True
        else:
            number_of_local_variables += 1
            variable_name = item
            colon = let_content.pop(0)
            if colon.name != ":":
                return -1

            item_type = let_content.pop(0)
            if item_type.name != "node_type":
                return -1

            either_coma_or_arrow = let_content.pop(0)
            if either_coma_or_arrow.name == "<-":
                variable_value = let_content.pop(0)
                if variable_value.name != "expr":
                    return -1

                item = let_content.pop(0)
                if item.name == "in":
                    found_in = True
                else:  # Moves to next item in case ","
                    item = let_content.pop(0)

            elif either_coma_or_arrow.name == ",":
                item = let_content.pop(0)
            else:
                return -1

        empty_stack = len(let_content) > 0

    return number_of_local_variables


"""
OTHER FUNCTIONS RELATED TO NODES
"""


def decompose_let_expr(node: Node) -> (List[LetVariable] | None, Node | None, str):
    """
    Decomposes the expression node that contains all elements related to while loop has a valis structure.
    VALID STRUCTURE No. 1 (bool_value as condition):
    ├── expr
    │   ├── let
    │   ├── ID
    │   ├── :
    │   ├── node_type
    │   │   └── Int
    │   ├── <-
    │   ├── <expr>
    │   │   ...
    │   ├── in
    │   ├── [
    │   ├── <expr>
    │   │   ├── etc...
    │   └── ]
    :param node: expr node that contains while
    :return:The number of structure or -1 in case of not having any of those
    """
    let_content = list(node.children)
    let_content.pop(0)  # Remove initial "let"

    found_in = False
    empty_stack = len(let_content) > 0
    number_of_local_variables = 0

    item = let_content.pop(0)

    error_on_structure = False

    let_variables: List[LetVariable] = []
    err_string = ""

    while not (found_in and empty_stack) and not error_on_structure:
        if item.name == "in":
            found_in = True
        else:
            let_item: LetVariable = LetVariable()

            number_of_local_variables += 1
            variable_name = item

            let_item.var_id = variable_name

            colon = let_content.pop(0)
            if colon.name != ":":
                error_on_structure = True
                err_string = f"For variable \"{variable_name}\" couldn't colon after variable name"

            else:
                item_type = let_content.pop(0)
                let_item.var_type = item_type
                if item_type.name != "node_type":
                    error_on_structure = True
                    err_string = f"For variable {variable_name} couldn't found node_type after colon"
                else:
                    either_coma_or_arrow = let_content.pop(0)

                    if either_coma_or_arrow.name == "<-":
                        variable_value = let_content.pop(0)
                        let_item.value = variable_value
                        if variable_value.name != "expr":
                            error_on_structure = True
                            err_string = f"For variable {variable_name} couldn't find value after <- assignation operator"

                        else:
                            item = let_content.pop(0)
                            if item.name == "in":
                                found_in = True
                            else:  # Moves to next item in case ","
                                item = let_content.pop(0)
                            let_variables.append(let_item)
                    elif either_coma_or_arrow.name == ",":
                        let_variables.append(let_item)
                        item = let_content.pop(0)
                    else:
                        error_on_structure = True
                        err_string = f"Couldn't found ',' or '<-' after variable declaration '{variable_name}'"

            empty_stack = len(let_content) > 0

    if error_on_structure:
        return None, None, err_string

    if not found_in:
        return None, None, "Couldn't found 'in' token after variables declaration"

    let_content.pop(0)  # Removes [
    to_evaluate_expression = let_content.pop(0)
    if to_evaluate_expression.name != "expr":
        return None, None, "Couldn't found proper expression to evaluate in let block"

    return let_variables, to_evaluate_expression, ""


"""
AUXILIARY FUNCTIONS
"""


def starts_with_number(string: str):
    return string[0].isdigit() if string else False


def equals_ignore_case(string1: str, string2: str):
    return string1.lower() == string2.lower()

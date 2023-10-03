from anytree import Node



"""
-----------
IDENTIFIERS
-----------
Receives a <expr> node and returns the type and subtype (structure)
"""
expressions = [
    "assignment",  # ID '<-' expr
    "dynamic_dispatch",  # expr '@' (type | CLASS_ID) '.' ID '(' (expr (',' expr)* )?')'
    "static_dispatch",  # expr '.' ID '(' (expr (',' expr)* )? ')'
    "function_call",  # ID '(' (expr (',' expr)* )? ')'
    "conditional",  # 'if' (bool_value | expr)  'then' expr 'else' expr 'fi'
    "loop",  # 'while' (bool_value | expr) 'loop' expr 'pool'
    "block",  # '{' expr (';' expr)* '}'
    "let_in",  # 'let' ID ':' type ('<-' expr)? (',' ID ':' type ('<-' expr)?)* 'in' expr
    "object_creation",  # 'new' (CLASS_ID | type)
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


def identify_expr(node: Node):
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
        ├── type
        │    └── Int
        └── ;
    VALID STRUCTURE No. 2:
     └── attr
        ├── radius
        ├── :
        ├── type
        │   └── Int
        ├── <-
        ├── expr
        │   └── 10
        └── ;

    Children:
    0 - Attribute name
    1 - :
    2 - <type>
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
    pass


"""
AUXILIARY FUNCTIONS
"""

def starts_with_number(string: str):
    return string[0].isdigit() if string else False

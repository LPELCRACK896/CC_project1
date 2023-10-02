from anytree import Node


def verify_node_structure_attribute(attr_root: Node) -> int:
    """
    Ensure the attribute node contains all elements in one of the expected structures
    VALID FORM 1 (unassigned):
    └── attr
        ├── radius
        ├── :
        ├── type
        │    └── Int
        └── ;
    VALID FORM 2:
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
    :return:The number of form or -1 in case of not having any of those
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

def verify_node_structure_while(node: Node):
    """
    Ensure the attribute node contains all elements in one of the expected structures
    VALID FORM 1 (bool_value as condition):
    ├── expr
    │   ├── while
    │   ├── bool_value
    │   │   └── true
    │   ├── loop
    │   ├── expr
    │   │   └── 1
    │   └── pool
    VALID FORM 2 (simple bool value):
     └── attr
        ├── radius
        ├── :
        ├── type
        │   └── Int
        ├── <-
        ├── expr
        │   └── 10
        └── ;
    :param node:
    :return:
    """

def verify_node_structure_let(node: Node):
    pass


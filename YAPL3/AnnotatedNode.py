from anytree import Node


class AnnotatedNode:

    def __init__(self, node: Node):
        self.node = node
        self.type = node.name
        self.children = node.children
        self.notations = self.initialize_notations_based_on_type()

    def initialize_notations_based_on_type(self):
        if self.type == "attr":
            #  Would be nice to have something to check the attribute structure
            return {
                "type":  (self.children,""),
                "value": "",
                "name": ""

            }

    def get_notation(self, value):
        pass


    def operations_over_tuples(self, node_operation: tuple):
        node = node_operation[0]
        operation = node_operation[1]

        if operation == "eval_to_bool":
            pass
        elif operation == "eval_to_int":
            pass
        elif operation == "eval_to_string":
            pass
        elif operation == "get_this_content":
            pass




def check_attribute_strucutre(node: Node):
    pass

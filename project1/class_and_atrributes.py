class Attribute:
    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type


class Method:
    def __init__(self, name, return_type, parameters):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters


class ClassDefinition:
    def __init__(self, name, attributes, methods):
        self.name = name
        self.attributes = attributes
        self.methods = methods

from typing import AnyStr, List, Dict
from Attribute import  Attribute
from Method import Method
import os


class Prototype:
    attributes: List[Attribute]
    special_attributes: List[AnyStr]
    methods: List[Method]
    tdc_methods: Dict[AnyStr, List[AnyStr]]
    name: AnyStr

    def __init__(self, name):
        self.name = name
        self.methods = []
        self.attributes = []
        self.special_attributes = []

    def add_special_attribute(self, attribute):
        self.special_attributes.append(attribute)

    def get_last_method_added(self):
        return self.methods[-1]

    def set_attributes(self, attributes):
        self.attributes = attributes

    def set_methods(self, methods):
        self.methods = methods

    def add_method(self, method):
        self.methods.append(method)

    def add_attribute(self, attribute):
        self.attributes.append(attribute)


    def write_example(self):
        file_content = f"# Clase {self.name}"
        file_content += "\n.data"
        file_content += "\n\tbuffer: .space 1024  # Reserva 1024 bytes para el buffer de entrada"
        string_attributes = "\n\t".join(attr.get_example() for attr in self.attributes)
        file_content += string_attributes

        file_content += "\n"
        file_content += "\n.text"
        file_content += "\n".join(method.get_example() for method in self.methods)

        filename = f"{self.name}.prototype"
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"
        with open(input_file, 'w') as file:
            file.write(file_content)

    def write_instance(self, memory_unit):
        pass



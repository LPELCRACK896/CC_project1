from ThreeDirectionsCode import ThreeDirectionsCode
from CodeStack import CodeStack
from typing import AnyStr, Tuple, List
from Prototype import Prototype
from Attribute import Attribute
from Method import Method
from RAM import RAM
from SymbolTable import SymbolTable
import MIPS_CONSTANTS as MC
import os

#  buffer: .space 1024  # Reserva 1024 bytes para el buffer de entrada

INTERMEDIATE_CODE_FILENAME = "intermediate_code.tdc"


class MIPS:

    tdc: ThreeDirectionsCode
    code: list
    filename: str
    prototypes: List[Prototype]
    ram: RAM

    temporary_regs: List
    saved_regs: List
    argument_regs: List
    result_regs: List
    special_regs: List
    mul_div_regs: List
    late_lines_assignation: List
    if_func_count: int

    symbol_table: SymbolTable

    def __init__(self, tdc: ThreeDirectionsCode, symbol_table: SymbolTable, filename=INTERMEDIATE_CODE_FILENAME):
        self.filename = filename
        self.code = []
        self.tdc = tdc
        self.available_regs = ["$t" + str(i) for i in range(9, -1, -1)]  # $t9 to $t0

        self.prototypes = []
        self.symbol_table = symbol_table

        self.temporary_regs = ["$t" + str(i) for i in range(10)]
        self.saved_regs = ["$s" + str(i) for i in range(8)]
        self.argument_regs = ["$a" + str(i) for i in range(4)]
        self.result_regs = ["$v" + str(i) for i in range(2)]
        self.special_regs = ["$sp", "$gp", "$fp", "$ra"]
        self.mul_div_regs = ["hi", "lo"]
        self.if_func_count = 0

        self.ram = RAM()
        self.build_and_get_IO_prototype()
        self.translator()

        self.__from_tdc_to_MIPS()

    def __str__(self):
        string_code = ""
        for register in self.code:
            string_code += f"{register}\n"

        return string_code

    def get_register(self, register_group):
        """Obtiene y elimina un registro del grupo especificado."""
        if not getattr(self, register_group):
            raise Exception(f"No hay registros disponibles en {register_group}")
        return getattr(self, register_group).pop()

    def get_specific_register(self, register_group, register_name):
        """Obtiene un registro específico si está disponible."""
        if register_name in getattr(self, register_group):
            getattr(self, register_group).remove(register_name)
            return register_name
        else:
            raise Exception(f"El registro {register_name} no está disponible")

    def check_register_availability(self, register_group):
        """Verifica si hay registros disponibles en el grupo especificado."""
        return bool(getattr(self, register_group))

    def release_register(self, register_group, register_name):
        """Libera un registro, devolviéndolo al grupo especificado."""
        getattr(self, register_group).append(register_name)

    @staticmethod
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
            "li $v0, 4       # syscall para imprimir cadena",
            "lw $a0, 0($sp)  # Carga la dirección de la cadena desde la pila",
            "syscall",
            "jr $ra          # Retorna"
        ])
        class_prototype.add_method(prototype_out_string)

        #  out_int(x: Int): SELF_TYPE
        prototype_out_int = Method("outInt")
        prototype_out_int.set_content([
           "li $v0, 1  # syscall para imprimir entero",
            "lw $a0, 0($sp)  # Carga el entero desde la pila",
            "syscall",
            "jr $ra  # Retorna"
        ])
        class_prototype.add_method(prototype_out_int)

        # in_string()
        prototype_in_string = Method("inString")
        prototype_in_string.set_content([
            "li $v0, 8  # syscall para leer cadena",
            "la $a0, buffer  # Dirección del buffer",
            "li $a1, 1024  # Tamaño del buffer",
            "syscall",
            "jr $ra"
        ])
        class_prototype.add_method(prototype_in_string)

        # in_int()
        prototype_in_int = Method("inInt")
        prototype_in_int.set_content([
            "li $v0, 5  # syscall para leer entero",
            "syscall",
            "jr $ra  # Retorna"
        ])
        class_prototype.add_method(prototype_in_int)
        class_prototype.write_example()
        return class_prototype

    def write_on_main(self):
        pass

    def build_and_get_Object_prototype(self) -> Prototype:
        pass

    def how_deep_does_temporary_goes(self, temporary_var, code_left: List):
        last_line_found = 0
        deep = 0
        for line in code_left:
            if temporary_var in self.safe_split(line):
                last_line_found = deep
            deep += 1

        return last_line_found

    def add_basic_prototypes(self):
        # Builds 'IO' and 'Object' classes
        io_prototype = self.build_and_get_IO_prototype()
        # object_prototype = self.build_and_get_Object_prototype()

        self.prototypes.extend([io_prototype])


    def translator_get_next_state(self, state: AnyStr, line: AnyStr, remaining_lines: CodeStack,
                                  personalized_prototypes: List[Prototype], instructions_for_attr: List) \
            -> Tuple[bool, AnyStr, bool, List]:

        split_line = MIPS.safe_split(line)

        if state == "waiting_class":
            if split_line[0].startswith("CL"):
                if split_line[1] == "START":
                    class_prototype = Prototype(split_line[2])
                    personalized_prototypes.append(class_prototype)
                    return True, "waiting_attribute", False, instructions_for_attr
                return False, "waiting_class", True, instructions_for_attr
            return False, "end", False, instructions_for_attr
        elif state == "waiting_attribute":

            """
            Viable events: 
            - Found attribute
            - Found start method
            - Found end of class
            """
            if not personalized_prototypes:
                return False, "waiting_attribute", True, instructions_for_attr # No hay prototipo para asignar atributo
            last_prototype = personalized_prototypes[-1]

            if split_line[0].startswith(f"<DIR>.{last_prototype.name}.attr"):
                attr_name = split_line[0].split(".")[-1]
                attribute = Attribute(attr_name)
                attribute.set_additional_code(instructions_for_attr)
                symbol_class = self.symbol_table.get_classes().get(last_prototype.name)
                attributes_symbol = self.symbol_table.class_get_attributes(symbol_class)
                attribute_symbol = [attr_symbol for attr_name, attr_symbol in attributes_symbol.items()
                                    if attr_name == attr_name][0]
                attr_type = attribute_symbol.data_type

                if len(split_line) == 1:  # has no value
                    if attr_type in MC.defaults_values:  # Regular attribute
                        default_value = MC.defaults_values.get(attr_type)
                        attribute.set_value(default_value)
                        last_prototype.add_attribute(attribute)
                        return True, "waiting_attribute", False, []
                    else:  # Probably an object
                        last_prototype.add_special_attribute(attribute)
                        return True, "waiting_attribute", False, []
                else:  # has value || might be a temporal tho
                    value = split_line[2]
                    attribute.set_value(value)
                    last_prototype.add_attribute(attribute)
                    return True, "waiting_attribute", False, []
            elif split_line[0].startswith("MT"):
                if instructions_for_attr: # at this point this buffer should be empty
                    return False, "waiting_attribute", True, instructions_for_attr
                method = Method(split_line[-1])
                last_prototype.add_method(method)
                return False, "waiting_return_statement", False, instructions_for_attr
            elif split_line[0].startswith("CL"):  # End of class
                print("")
                return True, "waiting_class", False, instructions_for_attr
            else:  # additional instructions
                instructions_for_attr.append(line)
                return False, "waiting_attribute", False, instructions_for_attr
        elif state == "waiting_return_statement":
            """
            Viable events: 
            - Found end method
            - Found any other type of line (method content) 
            """
            if not personalized_prototypes:
                return False, "waiting_return_statement", True, instructions_for_attr
            last_prototype = personalized_prototypes[-1]
            if not last_prototype.methods:
                return False, "waiting_return_statement", True, instructions_for_attr
            last_method = last_prototype.get_last_method_added()
            last_method.add_tdc_line(line)
            if split_line[0] == "RETURN":
                remaining_lines.pop()
                return True, "waiting_method", False, instructions_for_attr
            else:
                return False, "waiting_return_statement", False, instructions_for_attr
        elif state == "waiting_method":
            """
            Viable events: 
            - Found method
            - Found end of class
            """
            if not personalized_prototypes:
                return False, "waiting_method", True, instructions_for_attr
            last_prototype = personalized_prototypes[-1]
            if split_line[0].startswith("MT"):  # Start other method
                if instructions_for_attr: # at this point this buffer should be empty
                    return False, "waiting_attribute", True, instructions_for_attr
                method = Method(split_line[-1])
                last_prototype.add_method(method)
                return True, "waiting_return_statement", False, instructions_for_attr
            else:  # End of class
                return True, "waiting_class", False, instructions_for_attr
        elif state == "end":
            return True, "end", False, instructions_for_attr

    @staticmethod
    def safe_split(line_to_split):

        if "'" not in line_to_split:
            return line_to_split.split(sep=" ")

        split = []
        pre_string, string, post_string = line_to_split.split(sep="'", maxsplit=2)

        split.extend(pre_string.split(sep=" "))
        split.append(f"'{string}'")
        split.extend(post_string.split(sep=" "))

        split = [item for item in split if item != ""]
        return split

    def translator(self):
        state_and_next_state_combinations = [
            ("waiting_class", "waiting_class" ),
            ("waiting_class", "waiting_attribute"),
        ]
        states = [
            "waiting_class",
            "waiting_attribute",
            "waiting_return_statement",
            "waiting_method",
            "end"
        ]
        instructions_for_attr = []

        self.ram.reset()
        self.add_basic_prototypes()

        def remove_special_chars_at_start(string):
            if string and string[0] in special_chars:
                return remove_special_chars_at_start(string[1:])
            return string

        def remove_special_chars_at_end(string):
            if string and string[-1] in special_chars:
                return remove_special_chars_at_end(string[:-1])
            return string

        def remove_special_chars_at_start_and_end(string):
            return remove_special_chars_at_start(remove_special_chars_at_end(string))

        with open(f"./{self.filename}", "r") as file:
            code_stack = CodeStack()

            special_chars = ["\n", "\t", " "]

            code_stack.initialize_content([remove_special_chars_at_start_and_end(line) for line in file
                                           if line.strip() != ""])
            code_stack.content.reverse()
            new_prototypes = []
            state = "waiting_class"
            current_class = None
            current_method = None
            found_end = False
            encounter_error = False
            while not code_stack.is_empty() and not encounter_error and not found_end:

                next_line = code_stack.pop()
                got_expected, next_state, encounter_error, instructions_for_attr \
                    = self.translator_get_next_state(state, next_line, code_stack, new_prototypes, instructions_for_attr)

                state = next_state
                if next_state == "end":
                    found_end = True
            self.prototypes.extend(new_prototypes)
            print(1)

    def get_register(self):
        return self.available_regs.pop() if self.available_regs else None

    def release_register(self, reg):
        self.available_regs.append(reg)

    def __from_tdc_to_MIPS(self, filename="yapl_assembler.s"):
        self.code.append(".data\n\n")
        # logica del data

        self.code.append(".text\n")
        # resto del codigo
        for register in self.tdc.code:
            str_register = str(register)

            operands = str_register.split(' ')
            dest = operands[0] if len(operands) > 0 else None
            op1 = operands[2] if len(operands) > 1 else None
            op2 = operands[4] if len(operands) > 4 else None

            # if None in [dest, op1, op2]:
            #     # self.code.append(f"TDC>> {register}")
            #     continue

            reg1 = self.get_register()
            reg2 = self.get_register()

            if "CL" in str_register and "START" in str_register: # para inicios de clases
                self.code.append(f"{op1.lower()}:")
            if "CL" in str_register and "END" in str_register: # para inicios de clases
                self.code.append(f"\n")

            # Handle different operations
            if "SUM" in str_register:
                if "<DIR>" in op1:
                    self.code.append(f"\tlw {reg1}, {op1}")
                else:
                    self.code.append(f"\tli {reg1}, {op1}")
                if "<DIR>" in op2:
                    self.code.append(f"\tlw {reg2}, {op2}")
                else:
                    self.code.append(f"\tli {reg2}, {op2}")
                self.code.append(f"\tadd {dest}, {reg1}, {reg2}")
            elif "DIV" in str_register:
                if "<DIR>" in op1:
                    self.code.append(f"\tlw {reg1}, {op1}")
                else:
                    self.code.append(f"\tli {reg1}, {op1}")
                if "<DIR>" in op2:
                    self.code.append(f"\tlw {reg2}, {op2}")
                else:
                    self.code.append(f"\tli {reg2}, {op2}")
                self.code.append(f"\tdiv {reg1}, {reg2}")
                self.code.append(f"\tmflo {dest}")
            elif "SUB" in str_register:  # Handling subtraction
                if "<DIR>" in op1:
                    self.code.append(f"\tlw {reg1}, {op1}")
                else:
                    self.code.append(f"\tli {reg1}, {op1}")
                if "<DIR>" in op2:
                    self.code.append(f"\tlw {reg2}, {op2}")
                else:
                    self.code.append(f"\tli {reg2}, {op2}")
                self.code.append(f"\tsub {dest}, {reg1}, {reg2}")
            elif "MULT" in str_register:  # Handling multiplication
                if "<DIR>" in op1:
                    self.code.append(f"\tlw {reg1}, {op1}")
                else:
                    self.code.append(f"\tli {reg1}, {op1}")
                if "<DIR>" in op2:
                    self.code.append(f"\tlw {reg2}, {op2}")
                else:
                    self.code.append(f"\tli {reg2}, {op2}")
                self.code.append(f"\tmul {dest}, {reg1}, {reg2}")
            else:
                # self.code.append(f"TDC>> {register}")
                pass
            self.release_register(reg1)
            self.release_register(reg2)

    def write_file(self, filename: AnyStr = "yapl_assembler.s"):
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"

        with open(input_file, 'w') as file:
            file.write(str(self))


def example():
    mips = MIPS(None)  # Asumiendo que tienes una implementación adecuada para ThreeDirectionsCode
    reg = mips.get_register("temporary_regs")
    print(f"Registro obtenido: {reg}")
    mips.release_register("temporary_regs", reg)
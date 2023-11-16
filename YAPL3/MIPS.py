from ThreeDirectionsCode import ThreeDirectionsCode
from CodeStack import CodeStack
from typing import AnyStr, Tuple, List, Dict
from Prototype import Prototype
from Attribute import Attribute
from Method import Method
from SymbolTable import SymbolTable
from Symbol import Symbol
import MIPS_CONSTANTS as MC
import MIPS_RESOURCES as mr
import TDC_RESOURCES as tdcr
import os
from collections import namedtuple

#  buffer: .space 1024  # Reserva 1024 bytes para el buffer de entrada

INTERMEDIATE_CODE_FILENAME = "intermediate_code.tdc"
Reference = namedtuple('Reference', ['alias', 'class_owner', 'type_of_reference'])
TemporaryContext = namedtuple('TemporaryContext',
                              ["is_primitive", "data_type", "register", "expiring_line", "is_instance"])


class MIPS:
    tdc: ThreeDirectionsCode
    filename: str
    prototypes: List[Prototype]

    temporary_regs: List
    saved_regs: List
    argument_regs: List
    result_regs: List
    special_regs: List
    mul_div_regs: List
    late_lines_assignation: List
    if_func_count: int

    symbol_table: SymbolTable

    registers_usage: Dict[AnyStr, AnyStr]
    temporary_vars: Dict[AnyStr, TemporaryContext]

    static_classes: List
    assembler_code: Dict[AnyStr, List[AnyStr]]

    def __init__(self, tdc: ThreeDirectionsCode, symbol_table: SymbolTable, filename=INTERMEDIATE_CODE_FILENAME):
        self.filename = filename
        self.tdc = tdc

        self.prototypes = []
        self.symbol_table = symbol_table
        self.static_classes = []
        self.temporary_vars = {}

        self.temporary_regs = ["$t" + str(i) for i in range(10)]
        self.temporary_regs.reverse()
        self.saved_regs = ["$s" + str(i) for i in range(8)]
        self.saved_regs.reverse()
        self.argument_regs = ["$a" + str(i) for i in range(4)]
        self.argument_regs.reverse()
        self.result_regs = ["$v" + str(i) for i in range(2)]
        self.result_regs.reverse()
        self.special_regs = ["$sp", "$gp", "$fp", "$ra"]
        self.mul_div_regs = ["hi", "lo"]
        self.if_func_count = 0
        self.assembler_code = \
            {
                ".data": [
                    "\tbuffer: .space 1024"
                ],
                "pre_main_run": [

                ],
                ".text": [

                ]
            }
        self.registers_usage: Dict[AnyStr] = {}
        self.build_and_get_IO_prototype()
        self.extract_prototypes_from_tdc()

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

    def add_basic_prototypes(self):
        # Builds 'IO' and 'Object' classes
        io_prototype = self.build_and_get_IO_prototype()
        # object_prototype = self.build_and_get_Object_prototype()

        self.prototypes.extend([io_prototype])

    def prototype_get_next_state(self, state: AnyStr, line: AnyStr, remaining_lines: CodeStack,
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
                return False, "waiting_attribute", True, instructions_for_attr  # No hay prototipo para asignar atributo
            last_prototype = personalized_prototypes[-1]

            if split_line[0].startswith(f"<DIR>.{last_prototype.name}.attr"):
                attr_name = split_line[0].split(".")[-1]
                attribute = Attribute(attr_name)
                instructions_for_attr.append(" ".join(split_line))
                attribute.set_additional_code(instructions_for_attr)
                symbol_class = self.symbol_table.get_classes().get(last_prototype.name)
                attributes_symbol = self.symbol_table.class_get_attributes(symbol_class)
                attribute_symbol = [attr_symbol for attri_name, attr_symbol in attributes_symbol.items()
                                    if attri_name == attr_name][0]
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
                if instructions_for_attr:  # at this point this buffer should be empty
                    return False, "waiting_attribute", True, instructions_for_attr
                method = Method(split_line[-1])
                last_prototype.add_method(method)
                return False, "waiting_return_statement", False, instructions_for_attr
            elif split_line[0].startswith("CL"):  # End of class
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
                if instructions_for_attr:  # at this point this buffer should be empty
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

    def extract_prototypes_from_tdc(self):
        instructions_for_attr = []
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
            found_end = False
            encounter_error = False
            while not code_stack.is_empty() and not encounter_error and not found_end:

                next_line = code_stack.pop()
                got_expected, next_state, encounter_error, instructions_for_attr \
                    = self.prototype_get_next_state(state, next_line, code_stack, new_prototypes, instructions_for_attr)

                state = next_state
                if next_state == "end":
                    found_end = True
            self.prototypes.extend(new_prototypes)

    def get_main_prototype(self) -> Prototype | None:
        for prototype in self.prototypes:
            if prototype.name == "Main":
                return prototype
        return None

    def get_main_method(self):
        main_class_prototype = self.get_main_prototype()
        if main_class_prototype is None:
            return None

        for method in main_class_prototype.methods:
            if method.name == "main":
                return method

        return None

    @staticmethod
    def update_class_variables_references(variables_as_object_reference: Dict[AnyStr, List[Reference]],
                                          reference: Reference) -> Dict[AnyStr, List[Reference]]:
        owner = reference.class_owner
        if owner in variables_as_object_reference.keys():
            variables_as_object_reference[owner].append(reference)
        else:
            variables_as_object_reference[owner] = [reference]

        return variables_as_object_reference

    def exist_let_variable(self, class_name, method_name, variable_name):
        existing_let_variables = [line.split(":")[0] for line in self.assembler_code.get(".data")
                                  if len(line.split(":")[0].split("_")) >= 4]

        for let_var in existing_let_variables:
            split_name = let_var.split("_")
            var_class_owner, var_method, var_name = split_name[0], split_name[1], split_name[-1]
            if var_class_owner == class_name and var_method == method_name and variable_name == var_name:
                return True
        return False

    @staticmethod
    def search_reference(alias: str, storage: Dict[str, List[Reference]], owner) -> Reference | None:
        if owner not in storage:
            return None
        variables = storage.get(owner)
        for var in variables:
            if var.alias == alias:
                return var
        return None

    def build_from_main_method(self):
        main_prototype = self.get_main_prototype()
        main_method = self.get_main_method()

        variables_as_object_reference: Dict[AnyStr, List[Reference]] = {}
        existing_classes_in_mips = []
        if main_method is None:
            print("NO ES POSIBLE IDENTIFICAR LLAMADA MAIN")
            return
        class_symbol = [the_class for class_name, the_class in self.symbol_table.get_classes().items()
                        if class_name == "Main"][0]
        existing_classes_in_mips.append("Main")
        self.build_static_instance_attributes(
            prototype_name="Main",
            class_symbol=class_symbol,
            attributes=main_prototype.attributes,
            variables_as_object_reference=variables_as_object_reference,
            existing_classes_in_mips=existing_classes_in_mips
        )
        self.build_static_instance_method(
            prototype_name="Main",
            class_symbol=class_symbol,
            method=main_method,
            variables_as_object_reference=variables_as_object_reference,
            existing_classes_in_mips=existing_classes_in_mips,
            is_main_func=True
        )
        other_methods = [method for method in main_prototype.methods if method != main_method]
        self.build_static_instance_methods(
            prototype_name="Main",
            class_symbol=class_symbol,
            methods=other_methods,
            variables_as_object_reference=variables_as_object_reference,
            existing_classes_in_mips=existing_classes_in_mips
        )

        self.asm_to_file()

    def build_static_instance_attributes(self, prototype_name: AnyStr, class_symbol: Symbol,
                                         attributes: List[Attribute], variables_as_object_reference: Dict,
                                         existing_classes_in_mips: List):

        for attr in attributes:
            self.build_static_instance_attribute(
                prototype_name=prototype_name,
                class_symbol=class_symbol,
                attribute=attr,
                variables_as_object_reference=variables_as_object_reference,
                existing_classes_in_mips=existing_classes_in_mips,
            )

        pass

    def build_static_instance_attribute(self, prototype_name: AnyStr, class_symbol: Symbol, attribute: Attribute,
                                        variables_as_object_reference: Dict[AnyStr, list],
                                        existing_classes_in_mips: List):
        attributes = self.symbol_table.class_get_attributes(class_symbol)
        attribute_symbol = [attr for attr_name, attr in attributes.items() if attr_name == attribute.name][0]
        attribute_type = attribute_symbol.data_type

        if mr.is_primitive(attribute_type):
            default_value = MC.defaults_values.get(attribute_type)
            mips_type = MC.type_of_data_on_mips.get(attribute_type)
            real_value = attribute.get_value()
            value = default_value if real_value is None else mr.transform_value(real_value, attribute_type)
            assembler_line = f"\t{prototype_name}_attr_{attribute.name}: {mips_type} {value}"
            self.assembler_code[".data"].append(assembler_line)
            if len(attribute.additional_code) > 1:
                self.process_block_tdc_code(attribute.additional_code, "pre_main_run", 1)
        else:
            new_reference = Reference(alias=attribute.name, class_owner=prototype_name, type_of_reference="attribute")
            variables_as_object_reference = self.update_class_variables_references(variables_as_object_reference,
                                                                                   new_reference)
            if not (attribute_type in existing_classes_in_mips):
                personalized_proto = [proto for proto in self.prototypes if proto.name == attribute_type][0]
                variables_as_object_reference, existing_classes_in_mips= self.build_static_instance(personalized_proto, variables_as_object_reference, existing_classes_in_mips)

    def build_IO_static_instance(self, prototype: Prototype, variables_as_object_reference: Dict,
                                 existing_classes_in_mips: List):
        existing_classes_in_mips.append("IO")
        for method in prototype.methods:
            method_name = f"IO_{method.name}"
            self.assembler_code.get(".text").append(f"\t{method_name}:")
            for cnt in method.content:
                self.assembler_code.get(".text").append(f"\t\t{cnt}")
        return variables_as_object_reference,existing_classes_in_mips

    def build_static_instance(self, prototype: Prototype, variables_as_object_reference: Dict,
                              existing_classes_in_mips: List):
        if prototype.name == "IO":
            return self.build_IO_static_instance(prototype, variables_as_object_reference, existing_classes_in_mips)

        class_symbol = [the_class for class_name, the_class in self.symbol_table.get_classes().items()
                        if class_name == prototype.name][0]
        existing_classes_in_mips.append(prototype.name)
        self.build_static_instance_attributes(
            prototype_name=prototype.name,
            class_symbol=class_symbol,
            attributes=prototype.attributes,
            variables_as_object_reference=variables_as_object_reference,
            existing_classes_in_mips=existing_classes_in_mips
        )
        self.build_static_instance_methods(
            prototype_name=prototype.name,
            class_symbol=class_symbol,
            methods=prototype.methods,
            variables_as_object_reference=variables_as_object_reference,
            existing_classes_in_mips=existing_classes_in_mips
        )
        return variables_as_object_reference, existing_classes_in_mips

    def build_static_instance_let_vars(self, prototype_name: AnyStr, let_variable, class_symbol: Symbol
                                       , additional_code: List, variables_as_object_reference: Dict,
                                       existing_classes_in_mips: List):
        pass

    def build_static_instance_methods(self, prototype_name: AnyStr, class_symbol: Symbol, methods: List[Method],
                                      variables_as_object_reference: Dict, existing_classes_in_mips: List):
        for method in methods:
            self.build_static_instance_method(prototype_name, class_symbol, method, variables_as_object_reference,
                                              existing_classes_in_mips, False)

    def build_static_instance_method(self, prototype_name: AnyStr, class_symbol: Symbol, method: Method,
                                     variables_as_object_reference: Dict, existing_classes_in_mips: List,
                                     is_main_func: bool):
        methods_symbols = self.symbol_table.class_get_methods(class_symbol)
        method_symbol: Symbol = [mth for mth_name, mth in methods_symbols.items() if mth_name == method.name][0]
        function_name = f"{prototype_name}_{method.name}"

        parameters: List[Tuple[AnyStr, AnyStr]] = method_symbol.parameters
        #  reference_io = self.search_reference("io", variables_as_object_reference, prototype_name)
        self.assembler_code.get(".text").append(f"\t{function_name}:")

        if is_main_func:
            self.assembler_code.get(".text").append("\t\tli $v0, 10")
            self.assembler_code.get(".text").append("\t\tsyscall")
        else:
            self.assembler_code.get(".text").append("\t\tjr $ra")
        pass


    def try_to_release_registers_and_temp_vars(self, line):

        to_delete = []

        for temp_name, temporary_var in self.temporary_vars.items():
            if line == temporary_var.expiring_line:
                to_delete.append(temp_name)

        for temp_name in to_delete:
            register_used = self.temporary_vars[temp_name].register
            self.release_register("temporary_regs", register_used)
            del self.temporary_vars[temp_name]

    def process_block_tdc_code(self, block: List[str], code_section, number_of_tabs):
        temporary_context = {}
        for line in block:
            self.process_line_tdc_code(line, block, code_section, number_of_tabs)
            self.try_to_release_registers_and_temp_vars(line)

    def process_line_tdc_code(self, line: AnyStr, block_context: List[AnyStr], code_section, number_of_tabs):
        parts = line.split(" ")
        size = len(parts)

        if tdcr.is_temporal_variable(parts[0]):
            if parts[1] == "=":  # Assigns into temporary variable
                self.process_temporary_variable_creation(line=line,
                                                         block_context=block_context,
                                                         code_section=code_section,
                                                         number_of_tabs=number_of_tabs,
                                                         )
            else:
                print(1)
        elif tdcr.is_an_assignation(line):

            self.process_assignation(line=line,
                                     block_context=block_context,
                                     code_section=code_section,
                                     number_of_tabs=number_of_tabs,)

        pass

    def save_temporary_var_on_register_reference(self, current_line: str, temporary_var: str, register: str,
                                                 block_context: list, data_type: str, is_primitive: bool,
                                                 is_instance:bool):
        expiring_line = self.find_last_usage_temporary(current_line, temporary_var, block_context)
        if not expiring_line:
            return False
        temp_context = TemporaryContext(
            is_primitive=is_primitive,
            data_type=data_type,
            register=register,
            expiring_line=expiring_line,
            is_instance=is_instance
        )
        self.temporary_vars[temporary_var] = temp_context

    def figure_out_data_type_assembler(self, data_name_variable):
        data_section = self.assembler_code[".data"]

        for line in data_section:
            if data_name_variable in line:
                data_type = line.split(" ")[1]
                return data_type
        return None

    def process_assignation(self, line, block_context, code_section, number_of_tabs):
        parts = line.split(" ")

        if not parts[0].startswith("<DIR>"):
            print()

        data_name_variable = tdcr.build_ram_name_from_tdc_direction(parts[0])

        register_loaded = self.load_address(data_name_variable, number_of_tabs, code_section)

        data_type = self.figure_out_data_type_assembler(data_name_variable)

        self.save_new_value_on_variable(register_loaded, parts[-1], data_type, number_of_tabs, code_section)
        self.release_register("temporary_regs", register_loaded)
        pass

    def save_new_value_on_variable(self, target_register, value, type_of_variable, number_of_tabs, code_section):

        if type_of_variable == ".asciiz":  # string
            # Assumes value is a string
            ln = self.get_empty_string_with_tabulations(number_of_tabs)
            for i, char in enumerate(value):
                if char != "'":
                    register_saved = self.load_value_into_register(f"\"{char}\"", number_of_tabs, code_section)
                    self.assembler_code[code_section].append(f"{ln}sb {register_saved}, {i}({target_register})")
                    self.release_register("temporary_regs", register_saved)

            register_saved = self.load_value_into_register("0", number_of_tabs, code_section)
            self.assembler_code[code_section].append(f"{ln}sb {register_saved}, {len(value)}({target_register})")
            self.release_register("temporary_regs", register_saved)

        elif type_of_variable == ".word":  # int
            register_val = self.get_register_from_component(value)
            use_new_register = False
            if register_val is None:
                register_val = self.load_immediate(value, number_of_tabs, code_section)
                use_new_register = True

            ln = self.get_empty_string_with_tabulations(number_of_tabs)
            self.assembler_code[code_section].append(f"{ln}sw {register_val}, 0({target_register})")
            if use_new_register:
                self.release_register("temporary_regs", register_val)
        elif type_of_variable == ".byte":  # bool
            register_val = self.get_register_from_component(value)
            use_new_register = False
            if register_val is None:
                register_val = self.load_immediate(value, number_of_tabs, code_section)
                use_new_register = True

            ln = self.get_empty_string_with_tabulations(number_of_tabs)
            self.assembler_code[code_section].append(f"{ln}sb {register_val}, 0({target_register})")
            if use_new_register:
                self.release_register("temporary_regs", register_val)

    def load_address(self, variable_name, num_tabs, code_section):
        register = self.get_register("temporary_regs")
        new_line = self.get_empty_string_with_tabulations(num_tabs)

        new_line += f"la {register}, {variable_name}"
        self.assembler_code[code_section].append(new_line)
        return register

        pass

    def process_temporary_variable_creation(self, line, block_context, code_section, number_of_tabs):
        split_line = line.split(" ")
        temporary_name = split_line[0]
        right_side_of_assignation = split_line[2:]

        if len(right_side_of_assignation) == 1:
            # Simple assignation
            pass

        if tdcr.is_arithmetic_operation(right_side_of_assignation):
            operation = right_side_of_assignation[1]
            temporary_to_save = split_line[0]
            if operation == "SUM":
                result_register = self.write_addition_assembler(right_side_of_assignation, code_section, number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_to_save, result_register, block_context,
                                                              "Int", True, False)
                return result_register
            elif operation == "MULT":
                result_register = self.write_multiplication_assembler(right_side_of_assignation, code_section,
                                                                      number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_to_save, result_register, block_context,
                                                              "Int", True, False)
                return result_register
            elif operation == "DIV":
                result_register = self.write_division_assembler(right_side_of_assignation, code_section, number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_to_save, result_register, block_context,
                                                              "Int", True, False)
                return result_register
            elif operation == "SUB":
                result_register = self.write_subtraction_assembler(right_side_of_assignation, code_section, number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_to_save, result_register, block_context,
                                                              "Int", True, False)
                return result_register

        if "ON" in right_side_of_assignation:
            # Es la llamada a una funcion
            pass
        elif "NEW" in right_side_of_assignation:
            # Es referencia a una clase
            print(1)
            pass
        elif "CALL" in right_side_of_assignation:
            pass

    def get_value_from_operation_component(self, component) -> int | None | str | TemporaryContext:

        if isinstance(component, TemporaryContext):
            return component

        component = str(component)
        if component.isnumeric():
            return int(component)

        if tdcr.is_temporal_variable(component):
            return self.temporary_vars.get(component)
        return None

    @staticmethod
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

    @staticmethod
    def get_empty_string_with_tabulations(number_of_tabulations) -> str:
        line = ""
        if number_of_tabulations < 0:
            number_of_tabulations = 0
        for _ in range(number_of_tabulations):
            line += "\t"
        return line

    """
    START
    OPERACIONES ARTIMÉTICAS
    """

    def load_value_into_register(self, value: str, num_tabs: int, code_section) -> AnyStr:
        register = self.get_register("temporary_regs")
        new_line = self.get_empty_string_with_tabulations(num_tabs)

        new_line += f"li {register}, {value}"
        self.assembler_code[code_section].append(new_line)
        return register

    def save_result_in_variable(self, register, variable, code_section):

        pass

    def get_register_from_component(self, component):
        value = self.get_value_from_operation_component(component)
        if isinstance(value, TemporaryContext):
            return value.register
        return None

    def load_immediate(self, component, number_of_tabs, code_section):
        value = self.get_value_from_operation_component(component)
        return self.load_value_into_register(value, number_of_tabs, code_section)

    def get_register_or_load_new_value_from_comp(self, component, number_of_tabs, code_section):
        value = self.get_value_from_operation_component(component)
        if not isinstance(value, TemporaryContext):
            return self.load_value_into_register(value, number_of_tabs, code_section)

        return value.register

    # RESTA
    def write_subtraction_assembler(self, tdc_line_operating, code_section, number_of_tabs):
        operator_1, _, operator_2 = tdc_line_operating

        operator_1 = self.get_value_from_operation_component(operator_1)
        operator_2 = self.get_value_from_operation_component(operator_2)

        register_operator_1 = self.get_register_or_load_new_value_from_comp(operator_1, number_of_tabs, code_section)
        register_operator_2 = self.get_register_or_load_new_value_from_comp(operator_2, number_of_tabs, code_section)

        register_save = self.get_register("temporary_regs")

        subtraction_line = self.get_empty_string_with_tabulations(number_of_tabs)
        subtraction_line += f"sub {register_save}, {register_operator_1}, {register_operator_2}"

        self.assembler_code[code_section].append(subtraction_line)
        self.release_register("temporary_regs", register_operator_1)
        self.release_register("temporary_regs", register_operator_2)

        return register_save

    # SUMA
    def write_addition_assembler(self, tdc_line_operating, code_section, number_of_tabs):

        operator_1, _, operator_2 = tdc_line_operating

        operator_1 = self.get_value_from_operation_component(operator_1)
        operator_2 = self.get_value_from_operation_component(operator_2)

        register_operator_1 = self.get_register_or_load_new_value_from_comp(operator_1, number_of_tabs, code_section)
        register_operator_2 = self.get_register_or_load_new_value_from_comp(operator_2, number_of_tabs, code_section)

        register_save = self.get_register("temporary_regs")

        add_line = self.get_empty_string_with_tabulations(number_of_tabs)
        add_line += f"add {register_save}, {register_operator_1}, {register_operator_2}"
        self.assembler_code[code_section].append(add_line)

        self.release_register("temporary_regs", register_operator_1)
        self.release_register("temporary_regs", register_operator_2)

        return register_save

    # MULTIPLICACION
    def write_multiplication_assembler(self, tdc_line_operating, code_section, number_of_tabs):
        operator_1, _, operator_2 = tdc_line_operating
        operator_1 = self.get_value_from_operation_component(operator_1)
        operator_2 = self.get_value_from_operation_component(operator_2)

        register_operator_1 = self.get_register_or_load_new_value_from_comp(operator_1, number_of_tabs, code_section)
        register_operator_2 = self.get_register_or_load_new_value_from_comp(operator_2, number_of_tabs, code_section)

        register_save = self.get_register("temporary_regs")

        multiplication_line = self.get_empty_string_with_tabulations(number_of_tabs)
        multiplication_line += f"mul {register_save}, {register_operator_1}, {register_operator_2}"

        self.assembler_code[code_section].append(multiplication_line)
        self.release_register("temporary_regs", register_operator_1)
        self.release_register("temporary_regs", register_operator_2)

        return register_save

    # DIVISION
    def write_division_assembler(self, tdc_line_operating, code_section, number_of_tabs):
        operator_1, _, operator_2 = tdc_line_operating

        operator_1 = self.get_value_from_operation_component(operator_1)
        operator_2 = self.get_value_from_operation_component(operator_2)

        register_operator_1 = self.get_register_or_load_new_value_from_comp(operator_1, number_of_tabs, code_section)
        register_operator_2 = self.get_register_or_load_new_value_from_comp(operator_2, number_of_tabs, code_section)

        register_save = self.get_register("temporary_regs")

        division_line_1 = self.get_empty_string_with_tabulations(number_of_tabs)
        division_line_1 += f"div {register_operator_1}, {register_operator_2}"
        self.assembler_code[code_section].append(division_line_1)

        division_line_2 = self.get_empty_string_with_tabulations(number_of_tabs)
        division_line_2 += f"mflo {register_save}"

        self.assembler_code[code_section].append(division_line_2)
        self.release_register("temporary_regs", register_operator_1)
        self.release_register("temporary_regs", register_operator_2)

        return register_save

    """
    TERMINA
    OPERACIONES ARTIMÉTICAS
    """

    def asm_to_file(self):
        file_string = "#  Proyecto final Contruccion de compiladores\n" \
                      "#  - Luis Pedro Gonzalez\n" \
                      "#  - Mariano Reyes\n"
        data_section = self.assembler_code.get(".data")
        addition_assembler_code = self.assembler_code.get("pre_main_run")
        text_section = self.assembler_code.get(".text")

        file_string += ".data\n"
        for line in data_section:
            file_string += f"{line}\n".replace("'", "\"")

        file_string += ".text\n"

        for line in addition_assembler_code:
            file_string += f"{line}\n".replace("'", "\"")

        file_string += "\n"
        file_string += "\tj Main_main\n"
        file_string += "\n"

        for line in text_section:
            file_string += f"{line}\n".replace("'", "\"")

        filename = f"output.asm"

        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"
        with open(input_file, 'w') as file:
            file.write(file_string)

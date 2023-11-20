from ThreeDirectionsCode import ThreeDirectionsCode
from typing import AnyStr, Tuple, List, Dict
from SymbolTable import SymbolTable
from Prototype import Prototype
from CodeStack import CodeStack
from Attribute import Attribute
import TDC_RESOURCES as tdcr
import MIPS_RESOURCES as mr
import MIPS_CONSTANTS as MC
from Method import Method
from Symbol import Symbol
import os

from mips_common import *
from mips_functions import *


INTERMEDIATE_CODE_FILENAME = "intermediate_code.tdc"


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

    temporary_vars: Dict[AnyStr, TemporaryContext]

    assembler_code: Dict[AnyStr, List[AnyStr]]
    params: list

    def __init__(self, tdc: ThreeDirectionsCode, symbol_table: SymbolTable, filename=INTERMEDIATE_CODE_FILENAME):
        self.filename = filename
        self.tdc = tdc

        self.prototypes = []
        self.symbol_table = symbol_table
        self.temporary_vars: Dict[AnyStr, TemporaryContext] = {}

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
        self.dynamic_string_count = 1
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
        self.params = []
        build_and_get_IO_prototype()
        self.extract_prototypes_from_tdc()

        self.last_on_line = ""

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

    """
    START PROTOTYPING EXTRACTION
    """

    def add_basic_prototypes(self):
        io_prototype = build_and_get_IO_prototype()
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

    """
    END PROTOTYPING EXTRACTION
    """

    """
    START ASSEMBLER CODE TRANSLATION
    """

    def try_to_release_registers_and_temp_vars(self, line):

        to_delete = []

        for temp_name, temporary_var in self.temporary_vars.items():
            if line == temporary_var.expiring_line:
                to_delete.append(temp_name)

        for temp_name in to_delete:
            register_used = self.temporary_vars[temp_name].register
            self.release_register("temporary_regs", register_used)
            del self.temporary_vars[temp_name]

    def save_temporary_var_on_register_reference(self, current_line: str, temporary_var: str, register: str,
                                                 block_context: list, data_type: str, is_primitive: bool,
                                                 is_instance: bool, is_address: bool):
        expiring_line = find_last_usage_temporary(current_line, temporary_var, block_context)
        if not expiring_line:
            return False
        temp_context = TemporaryContext(
            is_primitive=is_primitive,
            data_type=data_type,
            register=register,
            expiring_line=expiring_line,
            is_instance=is_instance,
            is_address=is_address

        )
        self.temporary_vars[temporary_var] = temp_context

    def get_assembler_data_type(self, data_name_variable):
        data_section = self.assembler_code[".data"]

        for line in data_section:
            if data_name_variable in line:
                data_type = line.split(" ")[1]
                return data_type
        return None

    def save_temporary_reference(self, target_register, value, type_of_variable, number_of_tabs, code_section):

        if type_of_variable == ".asciiz":  # string
            # Assumes value is a string
            ln = get_empty_string_with_tabulations(number_of_tabs)
            for i, char in enumerate(value):
                if char != "'":
                    register_saved = self.load_value_into_register(f"\"{char}\"", number_of_tabs, code_section)
                    self.assembler_code[code_section].append(f"{ln}sb {register_saved}, {i}({target_register})")
                    self.release_register("temporary_regs", register_saved)

            register_saved = self.load_value_into_register("0", number_of_tabs, code_section)
            self.assembler_code[code_section].append(f"{ln}sb {register_saved}, {len(value)-1}({target_register})")
            self.release_register("temporary_regs", register_saved)
        elif type_of_variable == ".word":  # int
            register_val = self.get_register_from_component(value)
            use_new_register = False
            if register_val is None:
                register_val = self.load_immediate(value, number_of_tabs, code_section)
                use_new_register = True

            ln = get_empty_string_with_tabulations(number_of_tabs)
            self.assembler_code[code_section].append(f"{ln}sw {register_val}, 0({target_register})")
            if use_new_register:
                self.release_register("temporary_regs", register_val)
        elif type_of_variable == ".byte":  # bool
            register_val = self.get_register_from_component(value)
            use_new_register = False
            if register_val is None:
                register_val = self.load_immediate(value, number_of_tabs, code_section)
                use_new_register = True

            ln = get_empty_string_with_tabulations(number_of_tabs)
            self.assembler_code[code_section].append(f"{ln}sb {register_val}, 0({target_register})")
            if use_new_register:
                self.release_register("temporary_regs", register_val)

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

    """
        - START BUILDING PROCESS
    """
    def build_IO_static_instance(self, prototype: Prototype, variables_as_object_reference: Dict,
                                 existing_classes_in_mips: List):
        existing_classes_in_mips.append("IO")
        for method in prototype.methods:
            method_name = f"IO_{method.name}"
            self.assembler_code.get(".text").append(f"\t{method_name}:")
            for cnt in method.content:
                self.assembler_code.get(".text").append(f"\t\t{cnt}")
        return variables_as_object_reference,existing_classes_in_mips

    def build_from_main_method(self):
        main_prototype = self.get_main_prototype()
        main_method = self.get_main_method()

        variables_as_object_reference: Dict[AnyStr, List[Reference]] = {}
        existing_classes_in_mips = []

        class_symbol = [the_class for class_name, the_class in self.symbol_table.get_classes().items()
                        if class_name == "Main"][0]
        existing_classes_in_mips.append("Main")
        self.build_multiple_attributes(prototype_name="Main", class_symbol=class_symbol,
                                       attributes=main_prototype.attributes,
                                       variables_as_object_reference=variables_as_object_reference,
                                       existing_classes_in_mips=existing_classes_in_mips)
        self.build_single_method(prototype_name="Main", class_symbol=class_symbol, method=main_method,
                                 variables_as_object_reference=variables_as_object_reference,
                                 existing_classes_in_mips=existing_classes_in_mips, is_main_func=True)

        other_methods = [method for method in main_prototype.methods if method != main_method]

        self.build_multiple_methods(prototype_name="Main", class_symbol=class_symbol, methods=other_methods,
                                    variables_as_object_reference=variables_as_object_reference,
                                    existing_classes_in_mips=existing_classes_in_mips)

        self.asm_to_file()

    def build_static_instance(self, prototype: Prototype, variables_as_object_reference: Dict,
                              existing_classes_in_mips: List):
        if prototype.name == "IO":
            return self.build_IO_static_instance(prototype, variables_as_object_reference, existing_classes_in_mips)

        class_symbol = [the_class for class_name, the_class in self.symbol_table.get_classes().items()
                        if class_name == prototype.name][0]
        existing_classes_in_mips.append(prototype.name)
        self.build_multiple_attributes(prototype_name=prototype.name, class_symbol=class_symbol,
                                       attributes=prototype.attributes,
                                       variables_as_object_reference=variables_as_object_reference,
                                       existing_classes_in_mips=existing_classes_in_mips)
        self.build_multiple_methods(prototype_name=prototype.name, class_symbol=class_symbol, methods=prototype.methods,
                                    variables_as_object_reference=variables_as_object_reference,
                                    existing_classes_in_mips=existing_classes_in_mips)
        return variables_as_object_reference, existing_classes_in_mips

    def build_multiple_attributes(self, prototype_name: AnyStr, class_symbol: Symbol, attributes: List[Attribute],
                                  variables_as_object_reference: Dict, existing_classes_in_mips: List):
        for attr in attributes:
            self.build_single_attribute\
                (
                    prototype_name=prototype_name,
                    class_symbol=class_symbol,
                    attribute=attr,
                    variables_as_object_reference=variables_as_object_reference,
                    existing_classes_in_mips=existing_classes_in_mips
                 )

    def build_single_attribute(self, prototype_name: AnyStr, class_symbol: Symbol, attribute: Attribute,
                               variables_as_object_reference: Dict[AnyStr, list], existing_classes_in_mips: List):
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
                self.process_tdc_block(attribute.additional_code, "pre_main_run", 1)
        else:
            new_reference = Reference(alias=attribute.name, class_owner=prototype_name, type_of_reference="attribute")
            variables_as_object_reference = update_class_variables_references(variables_as_object_reference,
                                                                                   new_reference)
            if not (attribute_type in existing_classes_in_mips):
                personalized_proto = [proto for proto in self.prototypes if proto.name == attribute_type][0]
                variables_as_object_reference, existing_classes_in_mips= self.build_static_instance(personalized_proto, variables_as_object_reference, existing_classes_in_mips)

    def build_multiple_methods(self, prototype_name: AnyStr, class_symbol: Symbol, methods: List[Method],
                               variables_as_object_reference: Dict, existing_classes_in_mips: List):
        for method in methods:
            self.build_single_method(prototype_name, class_symbol, method, variables_as_object_reference,
                                     existing_classes_in_mips, False)

    def build_single_method(self, prototype_name: AnyStr, class_symbol: Symbol, method: Method,
                            variables_as_object_reference: Dict, existing_classes_in_mips: List, is_main_func: bool):
        methods_symbols = self.symbol_table.class_get_methods(class_symbol)
        method_symbol: Symbol = [mth for mth_name, mth in methods_symbols.items() if mth_name == method.name][0]
        function_name = f"{prototype_name}_{method.name}"

        parameters: List[Tuple[AnyStr, AnyStr]] = method_symbol.parameters
        #  reference_io = search_reference("io", variables_as_object_reference, prototype_name)
        self.assembler_code[".text"].append(f"\t{function_name}:")
        writing_formals = method.tdc_code[0].startswith(f"<DIR>.{prototype_name}.{method.name}.formal")
        i = 0
        for line in method.tdc_code:
            if writing_formals:
                self.process_formal(line.strip(), 2, parameters)
                i += 1
                writing_formals = method.tdc_code[i].startswith(f"<DIR>.{prototype_name}.{method.name}.formal")
            else:
                self.process_tdc_line(line, method.tdc_code, ".text", 2)
                self.try_to_release_registers_and_temp_vars(line)

        if is_main_func:
            self.assembler_code.get(".text").append("\t\tli $v0, 10")
            self.assembler_code.get(".text").append("\t\tsyscall")
        else:
            self.assembler_code.get(".text").append("\t\tjr $ra")
        pass

    def process_tdc_block(self, block: List[str], code_section, number_of_tabs):
        for line in block:
            self.process_tdc_line(line, block, code_section, number_of_tabs)
            self.try_to_release_registers_and_temp_vars(line)

    def process_tdc_line(self, line: AnyStr, block_context: List[AnyStr], code_section, number_of_tabs):
        parts = self.safe_split(line)
        size = len(parts)
        if tdcr.is_temporal_variable(parts[0]):
            if parts[1] == "=":  # Assigns into temporary variable
                self.process_temporary_variable_creation(line=line,
                                                         block_context=block_context,
                                                         code_section=code_section,
                                                         number_of_tabs=number_of_tabs,
                                                         )
            else:
                print("ERROR")
        elif tdcr.is_an_assignation(line):
            self.write_assignation(line=line, block_context=block_context, code_section=code_section,
                                   number_of_tabs=number_of_tabs)
        elif line.startswith("PARAM"):
            param = parts[1]
            temporary_var: TemporaryContext = self.temporary_vars.get(param)
            tabs = get_empty_string_with_tabulations(number_of_tabs)
            self.assembler_code[".text"].append(f"{tabs}addi $sp, $sp -4")
            self.assembler_code[".text"].append(f"{tabs}sw {temporary_var.register}, 0($sp)")
            self.params.append(param)
        elif line.startswith("<DIR>"):
            print(1)

    def write_assignation(self, line, block_context, code_section, number_of_tabs):
        parts = self.safe_split(line)
        if not parts[0].startswith("<DIR>"):
            print()

        data_name_variable = direction_to_data_alias(parts[0])

        register_loaded = self.load_address(data_name_variable, number_of_tabs, code_section)

        data_type = self.get_assembler_data_type(data_name_variable)

        self.save_temporary_reference(register_loaded, parts[-1], data_type, number_of_tabs, code_section)
        self.release_register("temporary_regs", register_loaded)
        pass

    def identify_data_type(self, item):
        if item.startswith("<DIR>"):
            return get_direction_data_type(item, self.symbol_table)
        else:
            return mr.identify_type_by_value(item)


    def process_temporary_variable_creation(self, line, block_context, code_section, number_of_tabs):
        split_line = self.safe_split(line)
        temporary_name = split_line[0]
        right_side_of_assignation = split_line[2:]

        if len(right_side_of_assignation) == 1:
            value = right_side_of_assignation[0]
            data_type = self.identify_data_type(value)
            if data_type == "String":
                result_register = self.load_data(value, number_of_tabs, code_section) if value.startswith("<DIR>") \
                        else self.load_temporal_string_address(value, number_of_tabs, code_section)
                self.save_temporary_var_on_register_reference(line, temporary_name, result_register, block_context,
                                                                  "String", True, False, True)
            elif data_type == "Int":
                result_register = self.load_data(value, number_of_tabs, code_section) if value.startswith("<DIR>") \
                    else self.load_int(value, number_of_tabs, code_section)
                self.save_temporary_var_on_register_reference(line, temporary_name, result_register, block_context,
                                                              "Int", True, False, False)
            else:  # Bool
                result_register = self.load_data(value, number_of_tabs, code_section) if value.startswith("<DIR>") \
                        else self.load_bool(value, number_of_tabs, code_section)
                self.save_temporary_var_on_register_reference(line, temporary_name, result_register, block_context,
                                                              "Bool", True, False, False)
            # Simple assignation
            print()

        if tdcr.is_arithmetic_operation(right_side_of_assignation):
            operation = right_side_of_assignation[1]
            if operation == "SUM":
                result_register = self.write_addition(right_side_of_assignation, code_section, number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_name, result_register, block_context,
                                                              "Int", True, False, False)
                return result_register
            elif operation == "MULT":
                result_register = self.write_multiplication(right_side_of_assignation, code_section, number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_name, result_register, block_context,
                                                              "Int", True, False, False)
                return result_register
            elif operation == "DIV":
                result_register = self.write_division(right_side_of_assignation, code_section, number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_name, result_register, block_context,
                                                              "Int", True, False, False)
                return result_register
            elif operation == "SUB":
                result_register = self.write_subtraction(right_side_of_assignation, code_section, number_of_tabs)
                self.save_temporary_var_on_register_reference(line, temporary_name, result_register, block_context,
                                                              "Int", True, False, False)
                return result_register

        if "ON" in right_side_of_assignation:
            self.last_on_line = line

        elif "NEW" in right_side_of_assignation:
            class_referenced = split_line[2]
            temp = TemporaryContext(
                is_primitive=False,
                is_address=False,
                data_type=class_referenced,
                register=None,
                expiring_line=find_last_usage_temporary(line, temporary_name, block_context),
                is_instance=True
            )
            self.temporary_vars[temporary_name] = temp
            pass
        elif "CALL" in right_side_of_assignation:
            calling_on = self.last_on_line
            self.last_on_line = ""
            num_params_used = len(self.params)
            self.params = []
            direction_called = calling_on.split(" ")[2]
            direction_called_split = direction_called.split(".")
            procedure_name = f"{direction_called_split[1]}_{direction_called_split[3]}"
            tabs = get_empty_string_with_tabulations(number_of_tabs)
            self.assembler_code[".text"].append(f"{tabs}jal {procedure_name}")
            self.assembler_code[".text"].append(f"{tabs}addi $sp, $sp, {4*num_params_used}")




    def get_value_from_operation_component(self, component) -> int | None | str | TemporaryContext:

        if isinstance(component, TemporaryContext):
            return component

        component = str(component)
        if component.isnumeric():
            return int(component)

        if tdcr.is_temporal_variable(component):
            return self.temporary_vars.get(component)
        return None

    """
    START
    OPERACIONES ARTIMÉTICAS
    """
    def load_address(self, variable_name, num_tabs, code_section):
        register = self.get_register("temporary_regs")
        new_line = get_empty_string_with_tabulations(num_tabs)

        new_line += f"la {register}, {variable_name}"
        self.assembler_code[code_section].append(new_line)
        return register

    def load_value_into_register(self, value: str, num_tabs: int, code_section) -> AnyStr:
        register = self.get_register("temporary_regs")
        new_line = get_empty_string_with_tabulations(num_tabs)
        if isinstance(value, str):
            value = char_to_ascii(value[1]) if value.startswith("\"") else value
        new_line += f"li {register}, {value}"
        self.assembler_code[code_section].append(new_line)
        return register

    def get_register_from_component(self, component):
        value = self.get_value_from_operation_component(component)
        if isinstance(value, TemporaryContext):
            return value.register
        return None

    def load_immediate(self, component, number_of_tabs, code_section):
        value = self.get_value_from_operation_component(component)
        return self.load_value_into_register(value, number_of_tabs, code_section)

    def load_temporal_string_address(self, value, number_of_tabs, code_section):
        """
        Must release manually register
        :param value:
        :param number_of_tabs:
        :param code_section:
        :return:
        """

        tab = get_empty_string_with_tabulations(1)
        variable_name = f"temporal_var_{self.dynamic_string_count}"
        assembler_line = f"{tab}{variable_name}: .asciiz {value}"

        self.assembler_code.get(".data").append(assembler_line)
        self.dynamic_string_count += 1

        return self.load_address(variable_name, number_of_tabs, code_section)

    def load_bool(self, value, number_of_tabs, code_section):
        mips_bool_val = 0 if value == "false" else 1
        register = self.get_register("temporary_regs")
        new_line = get_empty_string_with_tabulations(number_of_tabs)
        new_line += f"li {register}, {mips_bool_val}"
        self.assembler_code[code_section].append(new_line)

        return register

    def load_int(self, value, number_of_tabs, code_section):
        register = self.get_register("temporary_regs")
        new_line = get_empty_string_with_tabulations(number_of_tabs)
        new_line += f"li {register}, {value}"
        self.assembler_code[code_section].append(new_line)

        return register

    def load_to_register_from_data(self, direction: str):
        if not direction.startswith("<DIR>"):
            return None
        split_direction = direction.split(".")
        print(1)

    def get_register_or_load_new_value_from_comp(self, component, number_of_tabs, code_section):
        if str(component).startswith("<DIR>"):
            return self.load_to_register_from_data(str(component))
            pass

        value = self.get_value_from_operation_component(component)
        if not isinstance(value, TemporaryContext):
            return self.load_value_into_register(value, number_of_tabs, code_section)

        return value.register

    def process_formal(self, direction, num_tabs, parameters):
        get_direction_type(direction)
        data_type = get_direction_data_type(direction, self.symbol_table)
        mips_type = to_mips_type(data_type)
        var_name = self.save_direction(direction)
        formal_name = direction.split(".")[-1]

        mips_parameters = [(param[0], to_mips_type(param[1])) for param in parameters]
        mip_parameter = [mip_parameter for mip_parameter in mips_parameters if mip_parameter[0]==formal_name][0]
        off_set = calculate_offset(mip_parameter, mips_parameters)
        #  Load in some register
        tabs = get_empty_string_with_tabulations(num_tabs)
        arg_reg = self.get_register("argument_regs")

        self.assembler_code[".text"].append(f"{tabs}lw {arg_reg}, {off_set}($sp)")

        store_instruction = "sb" if mips_type == ".byte" else "sw"
        self.assembler_code[".text"].append(f"{tabs}{store_instruction} {arg_reg}, {var_name}")

        self.release_register("argument_regs", arg_reg)
        print(1)

    def save_direction(self, direction, value = None):
        data_name = direction_to_data_alias(direction)
        data_type = get_direction_data_type(direction, self.symbol_table)
        mips_type = to_mips_type(data_type)
        value = value if value is not None else get_default_mips_value(mips_type)
        self.assembler_code[".data"].append(f"\t{data_name}: {mips_type} {value}")
        return data_name

    def load_word(self, value, num_tabs, code_section):
        tabs = get_empty_string_with_tabulations(num_tabs)
        register = self.get_register("temporary_regs")
        self.assembler_code[code_section].append(f"{tabs}lw {register}, {value}")
        return register

    def load_byte(self, value, num_tabs, code_section):
        tabs = get_empty_string_with_tabulations(num_tabs)
        register = self.get_register("temporary_regs")
        self.assembler_code[code_section].append(f"{tabs}lb {register}, {value}")
        return register

    def load_data(self, direction, num_tabs, code_section):
        """
        Tries to load from data
        :param direction:
        :param num_tabs:
        :param code_section:
        :return:
        """
        data_var_alias = direction_to_data_alias(direction)
        data_block = self.assembler_code.get(".data")

        found_data = False

        i = 0
        while not found_data and i < len(data_block):
            found_data = data_var_alias in data_block[i]
            i += 1

        if not found_data:
            return None

        data_line = data_block[i-1]

        var_name, data_type, _ = data_line.split(" ", 2)

        var_name = var_name.replace(":", "").strip()
        data_type = data_type.strip()

        if data_type == ".word":
            return self.load_word(var_name, num_tabs, code_section)
        elif data_type == ".byte":
            return self.load_byte(var_name, num_tabs, code_section)
        elif data_type == ".asciiz":
            return self.load_address(var_name, num_tabs, code_section)

        return None

    def load_item(self, item, num_tabs, code_section) -> str | None:
        """
        Two cases:
        -> Is a direction
            Must first load the data into some register and the get that register
            -> Depending on type od data will load the data
                -> Int -> .word -> lw
                -> Bool -> .byte -> lb
            -> There's a chance the direction is a class reference, this isn't defined in .data, so it won't be able to
            load in a register
        -> Is a constant
            - Bool -> Crea
            - Int
            - String


        :param item:
        :param num_tabs
        :param code_section
        :return: Register or None (in case is a reference to object)
        """

        if isinstance(item, str):
            if item.startswith("<DIR>"):
                return self.load_data(item, num_tabs, code_section)

        if str(item).isnumeric():
            return self.load_int(item, num_tabs, code_section)

        if str(item) == "false" or str(item) == "true":
            return self.load_bool(item, num_tabs, code_section)

        if str(item).startswith("'"):
            return self.load_temporal_string_address(item, num_tabs, code_section)

        return None
        raise Exception("valio madres")

    def get_temp_var_register(self, temporary_alias):
        if temporary_alias in self.temporary_vars:
            return self.temporary_vars.get(temporary_alias).register
        return None

    def write_subtraction(self, tdc_line_operating, code_section, number_of_tabs):
        operand_1, _, operand_2 = tdc_line_operating
        operand_1_is_temp = str(operand_1).startswith("t")
        operand_2_is_temp = str(operand_2).startswith("t")

        register_operand_1 = self.get_temp_var_register(operand_1) if operand_1_is_temp \
            else self.load_item(operand_1, number_of_tabs, code_section)

        register_operand_2 = self.get_temp_var_register(operand_2) if operand_2_is_temp \
            else self.load_item(operand_2, number_of_tabs, code_section)

        register_result = self.get_register("temporary_regs")

        tabs = get_empty_string_with_tabulations(number_of_tabs)
        add_line = f"{tabs}sub {register_result}, {register_operand_1}, {register_operand_2}"
        self.assembler_code[code_section].append(add_line)

        if not operand_1_is_temp:  # It was just loaded
            self.release_register("temporary_regs", register_operand_1)
        if not operand_2_is_temp:
            self.release_register("temporary_regs", register_operand_2)

        return register_result

    def write_addition(self, tdc_line_operating: List[str], code_section, number_of_tabs):
        operand_1, _, operand_2 = tdc_line_operating
        operand_1_is_temp = str(operand_1).startswith("t")
        operand_2_is_temp = str(operand_2).startswith("t")

        register_operand_1 = self.get_temp_var_register(operand_1) if operand_1_is_temp \
            else self.load_item(operand_1, number_of_tabs, code_section)

        register_operand_2 = self.get_temp_var_register(operand_2) if operand_2_is_temp \
            else self.load_item(operand_2, number_of_tabs, code_section)

        register_result = self.get_register("temporary_regs")

        tabs = get_empty_string_with_tabulations(number_of_tabs)
        add_line = f"{tabs}add {register_result}, {register_operand_1}, {register_operand_2}"
        self.assembler_code[code_section].append(add_line)

        if not operand_1_is_temp:  # It was just loaded
            self.release_register("temporary_regs", register_operand_1)
        if not operand_2_is_temp:
            self.release_register("temporary_regs", register_operand_2)

        return register_result

    def write_multiplication(self, tdc_line_operating: List[str], code_section, number_of_tabs):
        operand_1, _, operand_2 = tdc_line_operating
        operand_1_is_temp = str(operand_1).startswith("t")
        operand_2_is_temp = str(operand_2).startswith("t")

        register_operand_1 = self.get_temp_var_register(operand_1) if operand_1_is_temp \
            else self.load_item(operand_1, number_of_tabs, code_section)

        register_operand_2 = self.get_temp_var_register(operand_2) if operand_2_is_temp \
            else self.load_item(operand_2, number_of_tabs, code_section)

        register_result = self.get_register("temporary_regs")

        tabs = get_empty_string_with_tabulations(number_of_tabs)
        mult_line = f"{tabs}mul {register_result}, {register_operand_1}, {register_operand_2}"
        self.assembler_code[code_section].append(mult_line)

        if not operand_1_is_temp:  # It was just loaded
            self.release_register("temporary_regs", register_operand_1)
        if not operand_2_is_temp:
            self.release_register("temporary_regs", register_operand_2)

        return register_result

    def write_division(self, tdc_line_operating, code_section, number_of_tabs):
        operand_1, _, operand_2 = tdc_line_operating
        operand_1_is_temp = str(operand_1).startswith("t")
        operand_2_is_temp = str(operand_2).startswith("t")

        register_operand_1 = self.get_temp_var_register(operand_1) if operand_1_is_temp \
            else self.load_item(operand_1, number_of_tabs, code_section)

        register_operand_2 = self.get_temp_var_register(operand_2) if operand_2_is_temp \
            else self.load_item(operand_2, number_of_tabs, code_section)

        register_result = self.get_register("temporary_regs")

        tabs = get_empty_string_with_tabulations(number_of_tabs)
        division_line = f"{tabs}div {register_operand_1}, {register_operand_2}"
        self.assembler_code[code_section].append(division_line)

        if not operand_1_is_temp:  # It was just loaded
            self.release_register("temporary_regs", register_operand_1)
        if not operand_2_is_temp:
            self.release_register("temporary_regs", register_operand_2)

        division_line_2 = get_empty_string_with_tabulations(number_of_tabs)
        division_line_2 += f"mflo {register_result}"
        return register_result

    """
    END
    OPERACIONES ARTIMÉTICAS
    """

    """
    AUXILIARY FUNCTIONS
    """
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

    """
    OTHER
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

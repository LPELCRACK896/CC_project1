from ThreeDirectionsCode import ThreeDirectionsCode
from typing import AnyStr
import os


class MIPS:

    tdc: ThreeDirectionsCode
    code: list

    def __init__(self, tdc: ThreeDirectionsCode):
        self.code = []
        self.tdc = tdc
        self.available_regs = ["$t" + str(i) for i in range(9, -1, -1)]  # $t9 to $t0

        self.__from_tdc_to_MIPS()

    def __str__(self):
        string_code = ""
        for register in self.code:
            string_code += f"{register}\n"

        return string_code

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
                self.code.append(f"{op1}:")
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
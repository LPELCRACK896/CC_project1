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
        for register in self.tdc.code:
            str_register = str(register)
            if "SUM" in str_register:
                operands = str_register.split(' ')
                dest = operands[0]
                op1 = operands[2]
                op2 = operands[4]

                reg1 = self.get_register()
                reg2 = self.get_register()

                if "<DIR>" in op1:
                    self.code.append(f"lw {reg1}, {op1}")
                else:
                    self.code.append(f"li {reg1}, {op1}")
                if "<DIR>" in op2:
                    self.code.append(f"lw {reg2}, {op2}")
                else:
                    self.code.append(f"li {reg2}, {op2}")

                # add operation
                self.code.append(f"add {dest}, {reg1}, {reg2}")

                self.release_register(reg1)
                self.release_register(reg2)

            elif "DIV" in str_register:
                operands = str_register.split(' ')
                dest = operands[0]
                op1 = operands[2]
                op2 = operands[4]

                reg1 = self.get_register()
                reg2 = self.get_register()

                if "<DIR>" in op1:
                    self.code.append(f"lw {reg1}, {op1}")
                else:
                    self.code.append(f"li {reg1}, {op1}")
                if "<DIR>" in op2:
                    self.code.append(f"lw {reg2}, {op2}")
                else:
                    self.code.append(f"li {reg2}, {op2}")

                # div operation
                self.code.append(f"div {reg1}, {reg2}")
                self.code.append(f"mflo {dest}")

                self.release_register(reg1)
                self.release_register(reg2)

    def write_file(self, filename: AnyStr = "yapl_assembler.s"):
        directory = os.path.dirname(os.path.realpath(__file__))
        input_file = f"{directory}/{filename}"

        with open(input_file, 'w') as file:
            file.write(str(self))
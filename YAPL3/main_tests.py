from SyntaxTree import SyntaxTree
from SymbolTable import SymbolTable
from ThreeDirectionsCode import ThreeDirectionsCode
import SemanticProccess as sp
from MIPS import MIPS
import os


def compile_yapl(input_data, gui_window=None):
    syntax_tree = SyntaxTree(input_data)
    # syntax_tree.print_errors()
    # syntax_tree.print_tree()

    symbol_table = SymbolTable(syntax_tree.root_at)
    symbol_table.estimate_symbol_table_memory_usage()
    print(symbol_table)
    semantic_verification, semantic_errors = sp.check_semantic(symbol_table)

    if syntax_tree.has_errors():
        print("#====SYNTAX ERRORS====#")
        syntax_tree.print_errors()

    if semantic_errors:
        print("#====SEMANTIC ERRORS====#")
        for error in semantic_errors:
            print("Error en linea " + str(error.line) + ": " + str(error.name) + " : " + str(error.details))

    if not (syntax_tree.has_errors() or semantic_errors):
        symbol_table.amplify_classes_content()
        # print(symbol_table.to_string_sequential_symbols())
        t_dir_code: ThreeDirectionsCode = symbol_table.get_three_directions_code()
        content = str(t_dir_code)
        #  print(content)
        t_dir_code.write_file("intermediate_code.tdc")

        mips: MIPS = MIPS(t_dir_code, symbol_table)
        mips.build_from_main_method()
        mips.asm_to_file()


if __name__ == "__main__":
    directory = os.path.dirname(os.path.realpath(__file__))  # Get the script's directory
    filename = "/helloworld.yapl"
    input_file = directory + filename

    with open(input_file, 'r') as file:
        input_data = file.read()
    compile_yapl(input_data)

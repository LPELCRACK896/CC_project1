from SyntaxTree import SyntaxTree
from SymbolTable import SymbolTable
import SemanticProccess as sp
import os


def compile_yapl(input_data, gui_window=None):
    syntax_tree = SyntaxTree(input_data)
    syntax_tree.print_tree()

    symbol_table = SymbolTable(syntax_tree.root_at)
    print(symbol_table)
    semantic_verification, semantic_errors = sp.check_semantic(symbol_table)

    if syntax_tree.has_errors():
        print("====SYNTAX ERRORS====")
        syntax_tree.print_errors()
    if semantic_errors:
        print("====SEMANTIC ERRORS====")
        for error in semantic_errors:
            print("Error en linea " + str(error.line) + ": " + str(error.name) + " : " + str(error.details))


if __name__ == "__main__":
    directory = os.path.dirname(os.path.realpath(__file__))  # Get the script's directory
    filename = "/input.yapl"
    input_file = directory + filename

    with open(input_file, 'r') as file:
        input_data = file.read()
    compile_yapl(input_data)

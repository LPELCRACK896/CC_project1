import os
from tkinter import filedialog, Tk
from antlr4 import *
from YAPLLexer import YAPLLexer
from YAPLParser import YAPLParser
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter
from customErrorListener import CustomErrorListener
from antlr4.tree.Tree import TerminalNode
from ClassSymbolTable import SymbolTable, Scope  # import de la symboltable
from chequeoSemantico import *


def build_anytree(node, antlr_node):
    if isinstance(antlr_node, TerminalNode):
        value = antlr_node.getText()
        # Replace double quotes with single quotes
        value = value.replace('"', "'")
        Node(value, parent=node)
    else:
        rule_name = parser.ruleNames[antlr_node.getRuleIndex()]
        child_node = Node(rule_name, parent=node)
        for child in antlr_node.getChildren():
            build_anytree(child_node, child)


root = Tk()
root.withdraw()
input_file = filedialog.askopenfilename(initialdir=os.getcwd(
), filetypes=(('YAPL files', '*.yapl'), ('All files', '*.*')))
with open(input_file, 'r') as file:
    input_data = file.read()
input_stream = InputStream(input_data)

# error listener customizado en español
error_listener = CustomErrorListener()

lexer = YAPLLexer(input_stream)
lexer.removeErrorListeners()
lexer.addErrorListener(error_listener)

stream = CommonTokenStream(lexer)
parser = YAPLParser(stream)
parser.removeErrorListeners()
parser.addErrorListener(error_listener)

# Aplica la regla inicial de la gramática (expr)
tree = parser.program()

# Print errors if any
errors = error_listener.get_errors()
for error in errors:
    print(error)

if errors:
    print("----------------------------------------------------------------------------------")
    print("\nYa que hay 1 o más errores no se armará el árbol sintáctico del archivo input.\n")
    print("----------------------------------------------------------------------------------")
else:
    print(tree.toStringTree(recog=parser))

    root = Node(parser.ruleNames[tree.getRuleIndex()])
    build_anytree(root, tree)

    # Imprime el árbol anytree
    for pre, fill, node in RenderTree(root):
        print(f'{pre}{node.name}')

    # Genera una representación visual del árbol anytree
    dot_exporter = UniqueDotExporter(root)
    dot_exporter.to_picture("visual_tree.png")
    os.system(f"start visual_tree.png")

    # Build the symbol table
    symbol_table = SymbolTable(root)

    print(symbol_table)

    # funciones de insertad, busqueda y elminacion
    '''
    # Inserta símbolo en global scope
    symbol_table.insert(name="MySymbol", data_type="int",
                        semantic_type="var", value=5, scope=symbol_table.global_scope)

    print(symbol_table)

    searched_symbol = symbol_table.search("MySymbol")
    print("\nBúsqueda de símbolo en tabla:")
    print(searched_symbol)

    symbol_table.delete_content("MySymbol")

    searched_symbol = symbol_table.search("MySymbol")
    print("\nSímbolo tras eliminacion:")
    print(searched_symbol)

    print(symbol_table)
    '''
    # Proyecto # 1 Análisis Semántico
    print("\nInicio del Chequeo Semántico:\n")

    if check_semantic_rules(tree, root, symbol_table):
        print("\nChequeo semántico exitoso!\n")
        # imprimir la GUI
    else:
        print("\nSe procede a terminar el programa por errores semánticos.")

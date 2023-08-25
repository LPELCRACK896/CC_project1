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


def check_main_class_and_method(tree):
    main_class_found = False
    main_method_found = False

    for child in tree.children:  # Iterate through top-level nodes
        if child.getChildCount() >= 2:  # Check for class definition
            class_name = child.children[1].getText()
            if class_name == "Main":
                main_class_found = True
                for class_child in child.children:  # Iterate through class body
                    if isinstance(class_child, YAPLParser.Method_declarationContext):
                        method_name = class_child.ID().getText()
                        if method_name == "main":
                            method_params = class_child.parameter_list()
                            if not method_params:
                                main_method_found = True
    errores = 0

    if not main_class_found:
        print("\nError: no hay clase Main.")
        errores += 1
    if not main_method_found:
        print("\nError: no hay método Main o tiene parámetros")
        errores += 1

    return errores


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
    print("\nInicio del Chequeo Semántico:")

    chequeo_semantico = True
    # chequear si hay main conforme a la regla semantica 2
    if check_main_class_and_method(tree) > 0:
        chequeo_semantico = False
    else:
        print("El chequeo de main fue exitoso")

    if chequeo_semantico:  # si se logro llegar con true al final de todo se crea el gui
        # imprimir la GUI
        pass

import os
from tkinter import filedialog, Tk
from antlr4 import *
from YAPLLexer import YAPLLexer
from YAPLParser import YAPLParser
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter
import antlr4
import re
from antlr4.tree.Tree import TerminalNode
from ClassSymbolTable import SymbolTable, Scope  # Make sure to import the SymbolTable and Scope classes


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

# Define a custom error listener
class CustomErrorListener(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # error en español
        translations = {
            r"missing (.+) at (.+)": r"falta \1 en \2",
            r"mismatched input (.+) expecting (.+)": r"entrada no coincidente \1, se esperaba \2",
            r"extraneous input '(.+)' expecting (.+)": r"entrada innecesaria '\1', se esperaba \2",
            # Agrega más traducciones aquí si lo deseas
        }

        # Buscar coincidencias con las expresiones regulares y traducir el mensaje
        for pattern, translation in translations.items():
            msg = re.sub(pattern, translation, msg)

        # Personalizar el mensaje de error aquí
        custom_msg = f"Error en la línea {line}, columna {column}, mensaje: {msg}"
        self.errors.append(custom_msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        pass

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        pass

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        pass

    def get_errors(self):
        return self.errors
    
root = Tk()
root.withdraw()
input_file = filedialog.askopenfilename(initialdir=os.getcwd(
), filetypes=(('YAPL files', '*.yapl'), ('All files', '*.*')))
with open(input_file, 'r') as file:
    input_data = file.read()
input_stream = InputStream(input_data)
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

    # Inserta símbolo en global scope
    symbol_table.insert(name="MySymbol", data_type="int", semantic_type="var", value=5, scope=symbol_table.global_scope)


    print(symbol_table)

    searched_symbol = symbol_table.search("MySymbol")
    print("\nBúsqueda de símbolo en tabla:")
    print(searched_symbol)

    symbol_table.delete_content("MySymbol")

    searched_symbol = symbol_table.search("MySymbol")
    print("\Símbolo tras eliminacion:")
    print(searched_symbol)

    print(symbol_table)


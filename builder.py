import os
import subprocess
from tkinter import filedialog, Tk


def generate_main_file(directory, start_rule="expr"):
    grammar_name = directory.rsplit("/", 1)[1]
    with open(f"{directory}/main.py", "w", encoding="utf-8") as f:
        f.write("import os\n")
        f.write("from tkinter import filedialog, Tk\n")  # Added this line
        f.write("from anytree.exporter import DotExporter\n")
        f.write("from antlr4 import *\n")
        f.write(f"from {grammar_name}Lexer import {grammar_name}Lexer\n")
        f.write(f"from {grammar_name}Parser import {grammar_name}Parser\n")
        f.write("from anytree import Node, RenderTree\n")
        f.write("from anytree.exporter import UniqueDotExporter\n")
        f.write("import antlr4\n")
        f.write("import re\n")
        f.write("from antlr4.tree.Tree import TerminalNode\n\n")

        f.write('''
class CustomErrorListener(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # error en español
        translations = {
            r"missing (.+) at (.+)": r"falta \\1 en \\2",
            r"mismatched input (.+) expecting (.+)": r"entrada no coincidente \\1, se esperaba \\2",
            r"extraneous input '(.+)' expecting (.+)": r"entrada innecesaria '\\1', se esperaba \\2",
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
        return self.errors\n\n''')

        # Below code to get file as input
        f.write("root = Tk()\n")
        f.write("root.withdraw()\n")
        f.write("input_file = filedialog.askopenfilename(initialdir=os.getcwd(),filetypes=(('YAPL files', '*.yapl'),('All files', '*.*')))\n")
        f.write("with open(input_file, 'r') as file:\n")
        f.write("    input_data = file.read()\n")
        f.write("input_stream = InputStream(input_data)\n")

        f.write("error_listener = CustomErrorListener()\n")

        f.write(f"lexer = {grammar_name}Lexer(input_stream)\n")
        f.write(f"lexer.removeErrorListeners()\n")
        f.write(f"lexer.addErrorListener(error_listener)\n\n")

        f.write("stream = CommonTokenStream(lexer)\n")

        f.write(f"parser = {grammar_name}Parser(stream)\n")

        f.write(f"parser.removeErrorListeners()\n")
        f.write(f"parser.addErrorListener(error_listener)\n\n")

        f.write("# Aplica la regla inicial de la gramática (expr)\n")
        f.write(
            f"tree = parser.{start_rule}()# Linea a cambiar en funcion de la regla inicial del parser\n\n")

        f.write('''
# tdos los errores se imprimen si hay
errors = error_listener.get_errors()
for error in errors:
    print(error)

if errors:
    print("----------------------------------------------------------------------------------")
    print("\\nYa que hay 1 o más errores no se armará el árbol sintáctico del archivo input.\\n")
    print("----------------------------------------------------------------------------------")
else:
    print(tree.toStringTree(recog=parser))

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

    root = Node(parser.ruleNames[tree.getRuleIndex()])
    build_anytree(root, tree)

    # Imprime el árbol anytree
    for pre, fill, node in RenderTree(root):
        print(f'{pre}{node.name}')

    # Genera una representación visual del árbol anytree
    dot_exporter = UniqueDotExporter(root)
    dot_exporter.to_picture("visual_tree.png")
    os.system(f"start visual_tree.png")
''')


def list_g4_files():
    return [f for f in os.listdir() if f.endswith('.g4')]


def generate_antlr_files(start_rule="expr"):
    root = Tk()
    root.withdraw()  # we don't want a full GUI, so keep the root window from appearing
    file = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=(
        ("ANTLR4 files", "*.g4"), ("All files", "*.*")))  # open the dialog GUI
    if file:
        directory = file.rsplit(".", maxsplit=1)[0]
        cmd = f'java -jar antlr-4.13.0-complete.jar -Dlanguage=Python3 -o "{directory}" "{file}"'
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            process = subprocess.run(
                cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            output = process.stdout
            print(output)

            # Generate main.py file for the grammar
            generate_main_file(directory=directory, start_rule=start_rule)

        except subprocess.CalledProcessError as e:
            print(
                f"Error generating ANTLR files for {file}. Command '{cmd}' returned non-zero exit status {e.returncode}.")


def compile_YAPL(start_rule="program"):
    generate_antlr_files(start_rule=start_rule)


def main():
    compile_YAPL()


if __name__ == "__main__":
    main()

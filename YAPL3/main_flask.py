from flask import Flask, render_template, request, redirect, url_for
from CustomErrorListener import CustomErrorListener
from YAPL3Lexer import YAPL3Lexer
from YAPL3Parser import YAPL3Parser
from ClassSymbolTable import SymbolTable
from SemanticProccess import check_semantic
from antlr4 import *
import os
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter, DotExporter
from tkinter import filedialog, Tk
from IntermediateProccess import build_cuadruples

app = Flask(__name__)


def build_anytree(node, antlr_node, parser):
    if isinstance(antlr_node, TerminalNode):
        value = antlr_node.getText()
        # Replace double quotes with single quotes
        value = value.replace('"', "'")
        Node(value, node, start_line=antlr_node.symbol.line,
             end_line=antlr_node.symbol.line)
        1
    else:
        rule_name = parser.ruleNames[antlr_node.getRuleIndex()]

        child_node = Node(
            rule_name, node, start_line=antlr_node.start.line, end_line=antlr_node.stop.line)
        for child in antlr_node.getChildren():
            build_anytree(child_node, child, parser)


@app.route('/', methods=['GET', 'POST'])
def index():

    syntax_errors = []
    semantic_errors = []
    uploaded_file = None
    input_data = None

    if request.method == 'POST':
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                input_data = uploaded_file.read().decode('utf-8')

                input_stream = InputStream(input_data)

                # error listener customizado en español
                error_listener = CustomErrorListener()

                lexer = YAPL3Lexer(input_stream)
                lexer.removeErrorListeners()
                lexer.addErrorListener(error_listener)

                stream = CommonTokenStream(lexer)
                parser = YAPL3Parser(stream)
                parser.removeErrorListeners()
                parser.addErrorListener(error_listener)

                # Aplica la regla inicial de la gramática (expr)
                tree = parser.program()

                # Print errors if any
                syntax_errors = error_listener.get_errors()
                for error in syntax_errors:
                    print(error)

                print(tree.toStringTree(recog=parser))
                if syntax_errors:
                    print(
                        "----------------------------------------------------------------------------------")
                    print(
                        "\nYa que hay 1 o más errores no se armará el árbol sintáctico del archivo input.\n")
                    print(
                        "----------------------------------------------------------------------------------")

                else:

                    root = Node(
                        name=parser.ruleNames[tree.getRuleIndex()], start_line=0, end_line=-1)
                    build_anytree(root, tree, parser)

                    # Imprime el árbol anytree
                    """ for pre, fill, node in RenderTree(root):
                        print(f'{pre}{node.name}') """

                    # Genera una representación visual del árbol anytree
                    dot_exporter = UniqueDotExporter(root)
                    dot_exporter.to_picture("visual_tree.png")
                    # os.system(f"start visual_tree.png")

                    # Build the symbol table
                    symbol_table = SymbolTable(root)
                    symbol_table.estimate_symbol_table_memory_usage()
                    print(symbol_table)

                    # Proyecto # 1 Análisis Semántico
                    print("\nInicio del Chequeo Semántico:\n")

                    semantic_verification, semantic_errors = check_semantic(
                        symbol_table)

                    if semantic_verification:
                        print("\nChequeo semántico exitoso!\n")

                        print("\nInicio de Construcción de Código Intermedio!\n")
                        quadruples = build_cuadruples(symbol_table)

                        print(quadruples)
                    else:
                        print("\n")
                        for error in semantic_errors:
                            print("Error en linea " +
                                  str(error.line) + ": " + str(error.name) +
                                  " : " + str(error.details))
                        print(
                            "----------------------------------------------------------------------------------")
                        print(
                            "\nYa que hay 1 o más errores semánticos no se compilará el archivo input.\n")
                        print(
                            "----------------------------------------------------------------------------------")

                # Renderiza una plantilla con los resultados
                return render_template('/index.html', input_data=input_data, syntax_errors=syntax_errors, semantic_errors=semantic_errors)
            else:
                return redirect(url_for('index'))
        else:
            # Check if 'edited_code' key exists in request.form
            edited_code = request.form.get(
                'edited_code', '')  # Get edited code from form
            if edited_code:

                input_stream = InputStream(edited_code)

                # error listener customizado en español
                error_listener = CustomErrorListener()

                lexer = YAPL3Lexer(input_stream)
                lexer.removeErrorListeners()
                lexer.addErrorListener(error_listener)

                stream = CommonTokenStream(lexer)
                parser = YAPL3Parser(stream)
                parser.removeErrorListeners()
                parser.addErrorListener(error_listener)

                # Aplica la regla inicial de la gramática (expr)
                tree = parser.program()

                # Print errors if any
                syntax_errors = error_listener.get_errors()
                for error in syntax_errors:
                    print(error)

                print(tree.toStringTree(recog=parser))
                if syntax_errors:
                    print(
                        "----------------------------------------------------------------------------------")
                    print(
                        "\nYa que hay 1 o más errores no se armará el árbol sintáctico del archivo input.\n")
                    print(
                        "----------------------------------------------------------------------------------")

                else:

                    root = Node(
                        name=parser.ruleNames[tree.getRuleIndex()], start_line=0, end_line=-1)
                    build_anytree(root, tree, parser)

                    # Imprime el árbol anytree
                    """ for pre, fill, node in RenderTree(root):
                        print(f'{pre}{node.name}') """

                    # Genera una representación visual del árbol anytree
                    dot_exporter = UniqueDotExporter(root)
                    dot_exporter.to_picture("visual_tree.png")

                    # Build the symbol table
                    symbol_table = SymbolTable(root)
                    symbol_table.estimate_symbol_table_memory_usage()
                    print(symbol_table)

                    # Proyecto # 1 Análisis Semántico
                    print("\nInicio del Chequeo Semántico:\n")

                    semantic_verification, semantic_errors = check_semantic(
                        symbol_table)

                    if semantic_verification:
                        print("\nChequeo semántico exitoso!\n")

                        print("\nInicio de Construcción de Código Intermedio!\n")
                        quadruples = build_cuadruples(symbol_table)

                        print(quadruples)
                    else:
                        print("\n")
                        for error in semantic_errors:
                            print("Error en linea " +
                                  str(error.line) + ": " + str(error.name) +
                                  " : " + str(error.details))
                        print(
                            "----------------------------------------------------------------------------------")
                        print(
                            "\nYa que hay 1 o más errores semánticos no se compilará el archivo input.\n")
                        print(
                            "----------------------------------------------------------------------------------")

                # Renderiza una plantilla con los resultados
                return render_template('/index.html', input_data=edited_code, syntax_errors=syntax_errors, semantic_errors=semantic_errors)
            else:
                return redirect(url_for('index'))
    return render_template('/index.html')


if __name__ == '__main__':
    app.run(debug=True)

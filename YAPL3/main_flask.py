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
from SyntaxTree import SyntaxTree
from IntermediateProccess import build_cuadruples
from Tres_Dir import IntermediateCode

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

                s_tree = SyntaxTree(input_data)

                # Print errors if any
                syntax_errors = s_tree.syntax_errors

                if s_tree.has_errors():
                    s_tree.print_errors()
                    print(
                        "----------------------------------------------------------------------------------")
                    print(
                        "\nYa que hay 1 o más errores no se armará el árbol sintáctico del archivo input.\n")
                    print(
                        "----------------------------------------------------------------------------------")

                else:
                    root = s_tree.root_at
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
                        # OPCION 1 PARA CODIGO INTERMEDIO
                        quadruples = build_cuadruples(symbol_table)

                        # OPCION 2 PARA CODIGO INTERMEDIO
                        visitor = IntermediateCode()
                        walker = ParseTreeWalker()
                        walker.walk(visitor, s_tree.tree)

                        codigo_intermedio = visitor.get_codigo_intermedio()

                        # Abrir el archivo en modo escritura
                        with open("codigo_intermedio.txt", "w") as archivo:
                            archivo.write(codigo_intermedio)

                        # # Abrir el archivo en modo escritura
                        # with open("codigo_intermedio.txt", "w") as archivo:
                        #     # Recorrer cada tupla en la lista y escribirla en el archivo
                        #     for tupla in quadruples:
                        #         # Convertir la tupla en una cadena
                        #         linea = " ".join(tupla)
                        #         # Escribir la cadena en el archivo seguida de un salto de línea
                        #         archivo.write(linea + "\n")

                        with open("codigo_intermedio.txt", "r") as archivo:
                            tres_dir = archivo.read()

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
                return render_template('/index.html', input_data=input_data, syntax_errors=syntax_errors, semantic_errors=semantic_errors, tres_dir=tres_dir)
            else:
                return redirect(url_for('index'))
        else:
            # Check if 'edited_code' key exists in request.form
            edited_code = request.form.get(
                'edited_code', '')  # Get edited code from form
            if edited_code:
                input_data = edited_code

                s_tree = SyntaxTree(input_data)

                if s_tree.has_errors():
                    s_tree.print_errors()
                    print(
                        "----------------------------------------------------------------------------------")
                    print(
                        "\nYa que hay 1 o más errores no se armará el árbol sintáctico del archivo input.\n")
                    print(
                        "----------------------------------------------------------------------------------")

                else:
                    root = s_tree.root_at
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

                        # Abrir el archivo en modo escritura
                        with open("codigo_intermedio.txt", "w") as archivo:
                            # Recorrer cada tupla en la lista y escribirla en el archivo
                            for tupla in quadruples:
                                # Convertir la tupla en una cadena
                                linea = " ".join(tupla)
                                # Escribir la cadena en el archivo seguida de un salto de línea
                                archivo.write(linea + "\n")

                        with open("codigo_intermedio.txt", "r") as archivo:
                            tres_dir = archivo.read()

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
                return render_template('/index.html', input_data=edited_code, syntax_errors=syntax_errors, semantic_errors=semantic_errors, tres_dir=tres_dir)
            else:
                return redirect(url_for('index'))
    return render_template('/index.html')


if __name__ == '__main__':
    app.run(debug=True)

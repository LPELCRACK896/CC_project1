from flask import Flask, render_template, request, redirect, url_for
from CustomErrorListener import CustomErrorListener
from YAPL3Lexer import YAPL3Lexer
from YAPL3Parser import YAPL3Parser
from SymbolTable import SymbolTable
import SemanticProccess as sp
from antlr4 import *
import os
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter, DotExporter
from SyntaxTree import SyntaxTree
from ThreeDirectionsCode import ThreeDirectionsCode
from MIPS import MIPS

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

                syntax_tree = SyntaxTree(input_data)
                syntax_tree.print_tree()

                symbol_table = SymbolTable(syntax_tree.root_at)
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
                    t_dir_code: ThreeDirectionsCode = symbol_table.get_three_directions_code()
                    content = str(t_dir_code)
                    print(content)
                    t_dir_code.write_file("intermediate_code.tdc")
                else:
                    with open("./intermediate_code.tdc", "w") as archivo:
                        archivo.write("")

                with open("./intermediate_code.tdc", "r") as archivo:
                    tres_dir = archivo.read()

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

                syntax_tree = SyntaxTree(input_data)
                syntax_tree.print_tree()

                symbol_table = SymbolTable(syntax_tree.root_at)
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
                    t_dir_code: ThreeDirectionsCode = symbol_table.get_three_directions_code()
                    content = str(t_dir_code)
                    t_dir_code.write_file("intermediate_code.tdc")
                else:
                    with open("./intermediate_code.tdc", "w") as archivo:
                        archivo.write("")

                with open("./intermediate_code.tdc", "r") as archivo:
                    tres_dir = archivo.read()

                # Dividir el texto en líneas y eliminar los caracteres de tabulación
                lineas = tres_dir.splitlines()
                lineas = [linea.replace('\t', '') for linea in lineas]

                # Dividir cada línea en palabras utilizando espacios como separador
                tripletas = [linea.split() for linea in lineas]

                # Eliminar líneas vacías
                tripletas = [palabras for palabras in tripletas if palabras]

                mips: MIPS = MIPS(t_dir_code)
                mips.write_file()

                # Renderiza una plantilla con los resultados
                return render_template('/index.html', input_data=edited_code, syntax_errors=syntax_errors, semantic_errors=semantic_errors, tres_dir=tres_dir, tripletas=tripletas, mips=mips)
            else:
                return redirect(url_for('index'))
    return render_template('/index.html')


if __name__ == '__main__':
    app.run(debug=True)

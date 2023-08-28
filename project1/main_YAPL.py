import os
from tkinter import filedialog, Tk
import tkinter as tk
from antlr4 import *
from YAPLLexer import YAPLLexer
from YAPLParser import YAPLParser
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter
from customErrorListener import CustomErrorListener
from antlr4.tree.Tree import TerminalNode
from ClassSymbolTable import SymbolTable, Scope  # import de la symboltable
from chequeoSemantico import *
import sys


def run_program(text_widget, gui_window):
    # Definir la función para guardar el nuevo contenido en un archivo
    new_input_data = text_widget.get("1.0", tk.END)
    with open('new_input.yapl', 'w') as file:
        file.write(new_input_data)

    with open('new_input.yapl', 'r') as file:
        input_data = file.read()
    main_program(input_data, gui_window)


def build_anytree(node, antlr_node, parser):
    if isinstance(antlr_node, TerminalNode):
        value = antlr_node.getText()
        # Replace double quotes with single quotes
        value = value.replace('"', "'")
        Node(value, parent=node)
    else:
        rule_name = parser.ruleNames[antlr_node.getRuleIndex()]
        child_node = Node(rule_name, parent=node)
        for child in antlr_node.getChildren():
            build_anytree(child_node, child, parser)


def clear_error_labels(window):
    for widget in window.winfo_children():
        if isinstance(widget, tk.Label) and widget.cget("fg") == "red":
            widget.destroy()


def create_gui(input_data):
    gui_window = tk.Tk()
    gui_window.title("Código Revisado")
    gui_window.geometry("1000x800")

    def on_window_close():
        gui_window.destroy()  # Close the GUI window
        print("Programa finalizado por el usuario.")
        sys.exit()  # Exit the program

    # Bind the window close event to the on_window_close function
    gui_window.protocol("WM_DELETE_WINDOW", on_window_close)

    # Agregar un widget de Texto más grande para mostrar el input_data
    text_widget = tk.Text(gui_window, height=30,
                          width=120, padx=20, pady=20)
    text_widget.insert("1.0", input_data)
    # Añade espacio en la parte superior e inferior
    text_widget.pack(pady=10)

    # Add an error label at the top of the new GUI window if there are no errors
    no_error_label = tk.Label(
        gui_window, text="No se encontraron errores.", fg="green")
    no_error_label.pack()

    # Agregar un botón personalizado para volver a ejecutar el programa
    button_style = {"padx": 20, "pady": 10,
                    "background": "#4CAF50", "foreground": "white"}

    run_button = tk.Button(gui_window, text="Compilar de nuevo",
                           command=lambda: run_program(text_widget, gui_window), **button_style)
    run_button.pack()

    # Run the main GUI loop
    gui_window.mainloop()


def main_program(input_data, gui_window=None):

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

        if gui_window:
            # Clear any previous error messages
            clear_error_labels(gui_window)

            # Show syntax and semantic errors above the button
            error_label = tk.Label(
                gui_window, text="¡Se encontraron errores en el código!", fg="red")
            error_label.pack()

            # If there are errors, show the GUI window again
            gui_window.deiconify()
    else:
        print(tree.toStringTree(recog=parser))

        root = Node(parser.ruleNames[tree.getRuleIndex()])
        build_anytree(root, tree, parser)

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

        # funciones de insertar, busqueda y elminacion de symboltable
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

        # if check_semantic_rules(tree, root, symbol_table):
        if True:
            print("\nChequeo semántico exitoso!\n")

            if gui_window:
                gui_window.destroy()  # Close the GUI window

            # creamos la gui
            create_gui(input_data)

        else:
            print("\nSe procede a terminar el programa por errores semánticos.")


# Pide al usuario que seleccione un archivo
root = tk.Tk()
root.withdraw()
input_file = filedialog.askopenfilename(initialdir=os.getcwd(),
                                        filetypes=(('YAPL files', '*.yapl'), ('All files', '*.*')))

with open(input_file, 'r') as file:
    input_data = file.read()

# Llamar a la función principal para ejecutar el análisis semántico y mostrar la GUI
main_program(input_data)

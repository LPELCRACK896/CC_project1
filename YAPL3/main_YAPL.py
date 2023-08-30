import os
import sys
from tkinter import filedialog, Tk
import tkinter as tk
from antlr4 import *
from YAPL3Lexer import YAPL3Lexer
from YAPL3Parser import YAPL3Parser
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter
# import del escuchador de errores personalizado
from CustomErrorListener import CustomErrorListener
from antlr4.tree.Tree import TerminalNode
from ClassSymbolTable import SymbolTable, Scope  # import de la symboltable
from SemanticProccess import check_semantic

reserved_keywords = ["if", "else", "while", "for",
                     "Int", "String", "Bool"]
reserved_ops = ["+", "-", "*", "/", ">=", ">", "=", "<", "<="]
reserved_signaling = ["{", "}", ":", "return",
                      "class", "inherits", "(new Main).main()", ";"]


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
        if isinstance(antlr_node.symbol, CommonToken) and antlr_node.symbol.type == YAPL3Parser.ERROR:
            error_node = Node("SYNTAX_ERROR: " +
                              antlr_node.symbol.text, parent=node)
    else:
        rule_name = parser.ruleNames[antlr_node.getRuleIndex()]
        child_node = Node(rule_name, parent=node)
        for child in antlr_node.getChildren():
            build_anytree(child_node, child, parser)


def clear_error_labels(window):
    for widget in window.winfo_children():
        if isinstance(widget, tk.Label) and widget.cget("fg") == "red":
            widget.destroy()


def highlight_keywords(text_widget):
    # Obtén el contenido del text_widget
    text = text_widget.get("1.0", "end-1c")

    # Lista de palabras clave reservadas
    reserved_keywords

    for keyword in reserved_keywords:
        start_index = "1.0"
        while True:
            # Busca la siguiente ocurrencia de la palabra clave
            start_index = text_widget.search(
                keyword, start_index, stopindex="end", nocase=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(keyword)}c"

            # Aplica formato de color a la palabra clave
            text_widget.tag_add(keyword, start_index, end_index)
            text_widget.tag_configure(keyword, foreground="blue")

            start_index = end_index

    for keyword in reserved_ops:
        start_index = "1.0"
        while True:
            # Busca la siguiente ocurrencia de la palabra clave
            start_index = text_widget.search(
                keyword, start_index, stopindex="end", nocase=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(keyword)}c"

            # Aplica formato de color a la palabra clave
            text_widget.tag_add(keyword, start_index, end_index)
            text_widget.tag_configure(keyword, foreground="red")

            start_index = end_index

    for keyword in reserved_signaling:
        start_index = "1.0"
        while True:
            # Busca la siguiente ocurrencia de la palabra clave
            start_index = text_widget.search(
                keyword, start_index, stopindex="end", nocase=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(keyword)}c"

            # Aplica formato de color a la palabra clave
            text_widget.tag_add(keyword, start_index, end_index)
            text_widget.tag_configure(keyword, foreground="purple")

            start_index = end_index


def create_gui(input_data):
    gui_window = tk.Tk()
    gui_window.title("Visual Studio Lite")
    gui_window.geometry("1400x800")

    def on_window_close():
        gui_window.destroy()  # Close the GUI window
        print("Programa finalizado por el usuario.")
        sys.exit()  # Exit the program

    # Bind the window close event to the on_window_close function
    gui_window.protocol("WM_DELETE_WINDOW", on_window_close)

    # Create a frame for line numbering
    line_number_frame = tk.Frame(gui_window)
    line_number_frame.pack(side="left", fill="y")

    # Create a label for each line number and add them to the frame
    lines_in_text_widget = input_data.split("\n")
    for i in range(len(lines_in_text_widget)):
        line_number_label = tk.Label(
            line_number_frame, text=str(i + 1), anchor="e", padx=5, width=3)
        line_number_label.grid(row=i, column=0, sticky="e")

    # Add a scrollbar
    scrollbar = tk.Scrollbar(gui_window)
    scrollbar.pack(side="right", fill="y")

    # Add a text widget for code display
    text_widget = tk.Text(gui_window, height=30,
                          width=70, padx=20, pady=4, wrap="none",
                          yscrollcommand=scrollbar.set, spacing3=6)

    text_widget.insert("1.0", input_data)

    # Highlight reserved keywords
    highlight_keywords(text_widget)

    text_widget.pack(side="left", fill="both", expand=False)

    scrollbar.config(command=text_widget.yview)

    # Agregar un botón personalizado para volver a ejecutar el programa
    button_style = {"padx": 20, "pady": 10,
                    "background": "#4CAF50", "foreground": "white"}

    run_button = tk.Button(gui_window, text="Compilar de nuevo",
                           command=lambda: run_program(text_widget, gui_window), **button_style)
    run_button.pack()

    # Add an error label at the top of the new GUI window if there are no errors
    no_error_label = tk.Label(
        gui_window, text="No se encontraron errores.", fg="green")
    no_error_label.pack()

    # Run the main GUI loop
    gui_window.mainloop()


def main_program(input_data, gui_window=None):

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

    if syntax_errors:
        print("----------------------------------------------------------------------------------")
        print("\nYa que hay 1 o más errores no se armará el árbol sintáctico del archivo input.\n")
        print("----------------------------------------------------------------------------------")

        if gui_window:
            # Clear any previous error messages
            clear_error_labels(gui_window)

            error_message = "¡Se encontraron errores sintácticos en el código!\n"
            for error in syntax_errors:
                error_message += error + "\n"  # Appending each error message

            # Create the error label widget with the constructed error message
            error_label = tk.Label(
                gui_window, text=error_message, fg="red", wraplength=1000)  # Adjust wrap length as needed
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

        semantic_verification, semantic_errors = check_semantic(symbol_table)

        if semantic_verification:
            print("\nChequeo semántico exitoso!\n")

            if gui_window:
                gui_window.destroy()  # Close the GUI window

            # creamos la gui
            create_gui(input_data)

        else:
            print("\n")
            for error in semantic_errors:
                print(error.name, ": ", error.details)
            print(
                "----------------------------------------------------------------------------------")
            print(
                "\nYa que hay 1 o más errores semánticos no se compilará el archivo input.\n")
            print(
                "----------------------------------------------------------------------------------")
            if gui_window:
                # Clear any previous error messages
                clear_error_labels(gui_window)

                error_message = "¡Se encontraron errores semánticos en el código!\n"
                for error in semantic_errors:
                    error = str(error.name) + ": " + str(error.details) + "\n"
                    error_message += error  # Appending each error message

                # Create the error label widget with the constructed error message
                error_label = tk.Label(
                    gui_window, text=error_message, fg="red", wraplength=1000)  # Adjust wrap length as needed
                error_label.pack()

                # Show the GUI window again with errors
                gui_window.deiconify()


# Pide al usuario que seleccione un archivo
root = tk.Tk()
root.withdraw()
input_file = filedialog.askopenfilename(initialdir=os.getcwd(),
                                        filetypes=(('YAPL files', '*.yapl'), ('All files', '*.*')))

with open(input_file, 'r') as file:
    input_data = file.read()

# Llamar a la función principal para ejecutar el análisis semántico y mostrar la GUI
main_program(input_data)

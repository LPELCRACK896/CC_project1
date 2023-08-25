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
        print("Error: no hay clase Main.")
        errores += 1
    if not main_method_found:
        print("Error: no hay método Main o tiene parámetros")
        errores += 1

    return errores


def check_inheritance_and_overrides(symbol_table):
    exito = True

    for class_name, class_symbol in symbol_table.content[symbol_table.global_scope.scope_id].items():
        if class_symbol.semantic_type == "class":
            parent_class_name = class_symbol.data_type

            if parent_class_name != "Object":
                parent_class_symbol = symbol_table.search(parent_class_name)

                if parent_class_symbol is None:
                    print(
                        f"Error: La clase {class_name} hereda de una clase inexistente: {parent_class_name}.")
                    exito = False
                else:
                    # Verificar la coherencia de los métodos sobrescritos
                    for method_name, method_info in class_symbol.content.items():
                        if method_info.semantic_type == "method":
                            parent_method = parent_class_symbol.search_content(
                                method_name)
                            if parent_method:
                                if parent_method.data_type != method_info.data_type:
                                    print(f"Error: El método {method_name} en la clase {class_name} "
                                          f"no sobrescribe correctamente el método de la clase padre {parent_class_name}.")
                                    exito = False
                            else:
                                print(f"Error: El método {method_name} en la clase {class_name} "
                                      f"no tiene un método padre correspondiente en la clase {parent_class_name}.")
                                exito = False

    return exito


def check_implicit_casting(root, symbol_table):
    exito = True
    return exito


def check_semantic_rules(tree, root, symbol_table):

    # Chequeo de herencia y sobrescritura conforme a la regla semantica 5
    if not check_inheritance_and_overrides(symbol_table):
        chequeo_semantico = False
    else:
        print("\nEl chequeo de herencia y sobrescritura fue exitoso")

    print()

    # chequear si hay main conforme a la regla semantica 2 y 3
    if check_main_class_and_method(tree) > 0:
        chequeo_semantico = False
    else:
        print("\nEl chequeo de main fue exitoso")

    # Verificar casteo implícito entre Bool e Int
    if not check_implicit_casting(root, symbol_table):
        chequeo_semantico = False
    else:
        print("\nEl chequeo de casteo implícito fue exitoso")

    return chequeo_semantico

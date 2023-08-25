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
        print("\nError: no hay clase Main.")
        errores += 1
    if not main_method_found:
        print("Error: no hay método Main o tiene parámetros")
        errores += 1

    return errores

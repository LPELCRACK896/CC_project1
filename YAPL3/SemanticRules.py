from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, SemanticFeedBack
from SemanticRules import *


def not_implemented_true(symbol_table: SymbolTable = None) -> (bool, SemanticFeedBack):
    return True, [SemanticError(name="Sin Implementar", details="Se debe implementar un método antes de usar esta función.", symbol=None, scope=None)]


def not_implemented_false(symbol_table: SymbolTable = None) -> (bool, SemanticFeedBack):
    return False, [SemanticError(name="Sin Implementar", details="Se debe implementar un método antes de usar esta función.", symbol=None, scope=None)]


def class_definition(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        if class_name == "global" or class_name == "main":
            continue  # Pasar a la siguiente clase si es 'global'

        class_scope = symbol_table.scopes[class_name]

        # Verificamos si hay atributos y métodos en la clase
        has_attributes = False
        has_methods = False
        for content_name in class_scope.content:
            content_symbol = class_scope.content[content_name]
            if content_symbol.semantic_type == "attr":
                has_attributes = True
            elif content_symbol.semantic_type == "method":
                has_methods = True

        if not has_attributes and not has_methods:
            class_symbol = symbol_table.search(class_name)
            feedback.append(SemanticError(name="EmptyClass",
                                          details=f"La clase '{class_name}' no tiene atributos ni métodos.",
                                          symbol=class_symbol,
                                          scope=class_scope))
            all_passed = False

    return all_passed, feedback


def attributes_definition(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        class_scope = symbol_table.scopes[class_name]

        # Validamos los atributos de la clase
        for attr_name in class_scope.content:
            attr_symbol = class_scope.content[attr_name]
            if attr_symbol.semantic_type == "attr":
                if attr_symbol.data_type == "":
                    feedback.append(SemanticError(name="MissingDataType",
                                                  details=f"Atributo '{attr_name}' en la clase '{class_name}' no tiene un tipo de dato definido.",
                                                  symbol=attr_symbol,
                                                  scope=class_scope))
                    all_passed = False
                else:
                    valid_types = ["Int", "String", "Bool"]
                    if attr_symbol.data_type not in valid_types:
                        feedback.append(SemanticError(name="InvalidDataType",
                                                      details=f"Atributo '{attr_name}' en la clase '{class_name}' tiene un tipo de dato inválido.",
                                                      symbol=attr_symbol,
                                                      scope=class_scope))
                        all_passed = False

                    if attr_symbol.value is not None:
                        # Verificar que el valor asignado sea compatible con el tipo de dato
                        if attr_symbol.data_type == "Int":
                            if not isinstance(attr_symbol.value, int):
                                try:
                                    int_value = int(attr_symbol.value)
                                except ValueError:
                                    feedback.append(SemanticError(name="IncorrectValueType",
                                                                  details=f"Atributo '{attr_name}' en la clase '{class_name}' tiene un valor asignado incompatible con el tipo de dato 'Int'.",
                                                                  symbol=attr_symbol,
                                                                  scope=class_scope))
                                    all_passed = False
                        elif attr_symbol.data_type == "String":
                            if not isinstance(attr_symbol.value, str):
                                feedback.append(SemanticError(name="IncorrectValueType",
                                                              details=f"Atributo '{attr_name}' en la clase '{class_name}' tiene un valor asignado incompatible con el tipo de dato 'String'.",
                                                              symbol=attr_symbol,
                                                              scope=class_scope))
                                all_passed = False
                        elif attr_symbol.data_type == "Bool":
                            if not isinstance(attr_symbol.value, bool):
                                if attr_symbol.value.lower() == "true" or attr_symbol.value.lower() == "false":
                                    attr_symbol.value = True if attr_symbol.value.lower() == "true" else False
                                else:
                                    feedback.append(SemanticError(name="IncorrectValueType",
                                                                  details=f"Atributo '{attr_name}' en la clase '{class_name}' tiene un valor asignado incompatible con el tipo de dato 'Bool'.",
                                                                  symbol=attr_symbol,
                                                                  scope=class_scope))
                                    all_passed = False

                    if attr_symbol.default_value is not None:
                        # Verificar que el valor default sea compatible con el tipo de dato
                        if attr_symbol.data_type == "Int":
                            if not isinstance(attr_symbol.default_value, int):
                                try:
                                    int_value = int(attr_symbol.default_value)
                                except ValueError:
                                    feedback.append(SemanticError(name="IncorrectDefaultValueType",
                                                                  details=f"Atributo '{attr_name}' en la clase '{class_name}' tiene un valor default incompatible con el tipo de dato 'Int'.",
                                                                  symbol=attr_symbol,
                                                                  scope=class_scope))
                                    all_passed = False
                        elif attr_symbol.data_type == "String":
                            if not isinstance(attr_symbol.default_value, str):
                                feedback.append(SemanticError(name="IncorrectDefaultValueType",
                                                              details=f"Atributo '{attr_name}' en la clase '{class_name}' tiene un valor default incompatible con el tipo de dato 'String'.",
                                                              symbol=attr_symbol,
                                                              scope=class_scope))
                                all_passed = False
                        elif attr_symbol.data_type == "Bool":
                            if not isinstance(attr_symbol.default_value, bool):
                                if attr_symbol.default_value.lower() == "true" or attr_symbol.default_value.lower() == "false":
                                    attr_symbol.default_value = True if attr_symbol.default_value.lower() == "true" else False
                                else:
                                    feedback.append(SemanticError(name="IncorrectDefaultValueType",
                                                                  details=f"Atributo '{attr_name}' en la clase '{class_name}' tiene un valor default incompatible con el tipo de dato 'Bool'.",
                                                                  symbol=attr_symbol,
                                                                  scope=class_scope))
                                    all_passed = False

    return all_passed, feedback

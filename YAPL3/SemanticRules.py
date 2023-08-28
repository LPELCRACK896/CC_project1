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
        if class_name == "global":
            continue  # Pasar a la siguiente clase si es 'global'

        class_scope = symbol_table.scopes[class_name]

        # Verificamos los atributos en la clase
        for content_name in class_scope.content:
            content_symbol = class_scope.content[content_name]

            if content_symbol.semantic_type == "attr":
                # Verificación del data type
                if content_symbol.data_type not in ["Int", "String", "Bool"]:
                    feedback.append(SemanticError(name="InvalidDataTypeError",
                                                  details=f"El atributo '{content_name}' en la clase '{class_name}' tiene un tipo de dato inválido: {content_symbol.data_type}. Debe ser 'Int', 'String' o 'Bool'.",
                                                  symbol=content_symbol,
                                                  scope=class_scope))
                    all_passed = False
                # Verificación del value
                value = content_symbol.value

                if value == "type":
                    value = content_symbol.default_value

                if content_symbol.data_type == "String":
                    if value is None or not (isinstance(value, str) and value.startswith('"') and value.endswith('"')):
                        feedback.append(SemanticError(name="InvalidValueError",
                                                      details=f"El atributo '{content_name}' en la clase '{class_name}' debe tener un valor de tipo String entre comillas dobles.",
                                                      symbol=content_symbol,
                                                      scope=class_scope))
                        all_passed = False
                elif content_symbol.data_type == "Int":
                    if value is None or not (isinstance(value, int) or (isinstance(value, str) and value.isnumeric())):
                        feedback.append(SemanticError(name="InvalidValueError",
                                                      details=f"El atributo '{content_name}' en la clase '{class_name}' debe tener un valor de tipo Int (número entero).",
                                                      symbol=content_symbol,
                                                      scope=class_scope))
                        all_passed = False
                elif content_symbol.data_type == "Bool":
                    if value is None or not (isinstance(value, bool) or (isinstance(value, str) and value.lower() in ["true", "false"])):
                        feedback.append(SemanticError(name="InvalidValueError",
                                                      details=f"El atributo '{content_name}' en la clase '{class_name}' debe tener un valor de tipo Bool (True o False).",
                                                      symbol=content_symbol,
                                                      scope=class_scope))
                        all_passed = False

    return all_passed, feedback


def main_check(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    main_method_exists = False

    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        class_scope = symbol_table.scopes[class_name]

        # Verificar si la clase 'Main' tiene un método 'main'
        if class_name == "Main":
            main_method = class_scope.search_content("main")
            if main_method and main_method.semantic_type == "method":
                main_method_exists = True
                break

    # Verificar si el método 'main' existe
    if not main_method_exists:
        feedback.append(SemanticError(name="MainMethodNotFoundError",
                                      details="La clase 'Main' debe contener un método llamado 'main'.",
                                      symbol=None,
                                      scope=None))
        all_passed = False

    return all_passed, feedback


def execution_start_check(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Verificar si existe la línea (new Main).main()
    '''
    main_call = symbol_table.search("main_call")
    if not main_call:
        feedback.append(SemanticError(name="MainCallNotFoundError",
                                      details="El programa debe contener la línea (new Main).main() para iniciar la ejecución.",
                                      symbol=None,
                                      scope=None))
        all_passed = False
    '''
    return all_passed, feedback

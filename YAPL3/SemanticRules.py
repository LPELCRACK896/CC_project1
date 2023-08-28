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
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("_")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Verificamos si hay atributos y métodos en la clase
            has_attributes = any(content_symbol.semantic_type ==
                                 "attr" for content_symbol in class_scope.content.values())
            has_methods = any(content_symbol.semantic_type ==
                              "method" for content_symbol in class_scope.content.values())

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
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global' o 'main'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("_")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Verificar atributos en la clase
            for content_name, content_symbol in class_scope.content.items():
                if content_symbol.semantic_type == "attr":
                    if content_symbol.value == None:
                        content_symbol.value = content_symbol.default_value

                    value = content_symbol.get_value()

                    if content_symbol.data_type == "Int":
                        if not isinstance(value, int) and isinstance(value, str):
                            if value.isnumeric():
                                value = int(value)
                        if value is not None and not isinstance(value, int):
                            feedback.append(SemanticError(name="InvalidAttributeValue",
                                                          details=f"El atributo '{content_name}' de la clase '{class_name}' debe tener un valor de tipo Int.",
                                                          symbol=content_symbol,
                                                          scope=class_scope))
                            all_passed = False

                        # chequear si es agrupacion de variables

                    elif content_symbol.data_type == "String":
                        if value is not None and not (isinstance(value, str)):
                            feedback.append(SemanticError(name="InvalidAttributeValue",
                                                          details=f"El atributo '{content_name}' de la clase '{class_name}' debe tener un valor de tipo String y estar entre comillas dobles.",
                                                          symbol=content_symbol,
                                                          scope=class_scope))
                            all_passed = False
                    elif content_symbol.data_type == "Bool":
                        if value is not None and value not in ["true", "false"]:
                            feedback.append(SemanticError(name="InvalidAttributeValue",
                                                          details=f"El atributo '{content_name}' de la clase '{class_name}' debe tener un valor de tipo Bool ('true' o 'false').",
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
        if class_name == "global_Main(class)":
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


def scope_check(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Función auxiliar para verificar la visibilidad de un símbolo en el ámbito actual
    def check_visibility(symbol, current_scope):
        if symbol.is_local_scope and symbol.scope != current_scope.scope_id:
            feedback.append(SemanticError(name="ScopeVisibilityError",
                                          details=f"El símbolo '{symbol.name}' no es visible en este ámbito.",
                                          symbol=symbol,
                                          scope=current_scope))
            return False
        return True

    # Recorrer todos los ámbitos en la tabla de símbolos
    for scope_id in symbol_table.scopes:
        scope = symbol_table.scopes[scope_id]

        # Recorrer los símbolos en el ámbito actual
        for symbol_name in scope.content:
            symbol = scope.content[symbol_name]

            # Verificar la visibilidad de los símbolos locales
            if symbol.is_local_scope:
                check_visibility(symbol, scope)

            # Verificar la visibilidad de los símbolos globales en métodos locales
            elif scope_id != "global":
                global_symbol = symbol_table.search(
                    symbol_name, symbol_table.global_scope)
                if global_symbol:
                    check_visibility(global_symbol, scope)

    return all_passed, feedback


def visibility_check(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Función auxiliar para verificar la visibilidad de un símbolo en un ámbito
    def check_visibility(symbol, current_scope):
        if symbol.is_local_scope and symbol.scope != current_scope.scope_id:
            return False
        return True

    # Recorrer todos los ámbitos en la tabla de símbolos
    for scope_id in symbol_table.scopes:
        scope = symbol_table.scopes[scope_id]

        # Recorrer los símbolos en el ámbito actual
        for symbol_name in scope.content:
            symbol = scope.content[symbol_name]

            # Verificar visibilidad en ámbito local
            if symbol.is_local_scope:
                if symbol.scope != scope.scope_id:
                    feedback.append(SemanticError(name="LocalScopeVisibilityError",
                                                  details=f"El símbolo '{symbol.name}' no es visible en este ámbito.",
                                                  symbol=symbol,
                                                  scope=scope))
                    all_passed = False

            # Verificar visibilidad en ámbito global
            else:
                if scope_id != "global":
                    global_symbol = symbol_table.search(
                        symbol_name, symbol_table.global_scope)
                    if global_symbol:
                        if not check_visibility(global_symbol, scope):
                            feedback.append(SemanticError(name="GlobalScopeVisibilityError",
                                                          details=f"El símbolo '{symbol.name}' no es visible en este ámbito.",
                                                          symbol=global_symbol,
                                                          scope=scope))
                            all_passed = False

    return all_passed, feedback


def check_inheritance_relations(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        class_symbol = symbol_table.search(
            class_name, symbol_table.global_scope)
        if class_symbol and class_symbol.semantic_type == "class":
            parent_class_name = class_symbol.data_type
            if parent_class_name != "Object":
                parent_class = symbol_table.search(
                    parent_class_name, symbol_table.global_scope)
                if not parent_class:
                    feedback.append(SemanticError(name="InheritanceError",
                                                  details=f"La clase '{class_name}' hereda de '{parent_class_name}', pero la clase padre no está definida.",
                                                  symbol=class_symbol,
                                                  scope=class_symbol.scope))
                    all_passed = False

    return all_passed, feedback


def check_inheritance_override_logic(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Función auxiliar para verificar si un método está sobrescrito correctamente
    def check_override(method_symbol, parent_method_symbol):
        if method_symbol.semantic_type == "method" and parent_method_symbol.semantic_type == "method":
            if method_symbol.parameters != parent_method_symbol.parameters:
                return False
        return True

    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        class_scope = symbol_table.scopes[class_name]
        class_symbol = class_scope.search_content(class_name)
        if class_symbol and class_symbol.semantic_type == "class":
            parent_class_name = class_symbol.data_type
            if parent_class_name != "Object":
                parent_class = symbol_table.search(
                    parent_class_name, symbol_table.global_scope)
                if parent_class:
                    for method_name in class_scope.content:
                        method_symbol = class_scope.search_content(method_name)
                        parent_method_symbol = parent_class.search_content(
                            method_name)
                        if parent_method_symbol and not check_override(method_symbol, parent_method_symbol):
                            feedback.append(SemanticError(name="OverrideLogicError",
                                                          details=f"El método '{method_name}' en la clase '{class_name}' no está sobrescrito correctamente.",
                                                          symbol=method_symbol,
                                                          scope=class_symbol))
                            all_passed = False

    return all_passed, feedback


def check_casting(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos

    return all_passed, feedback


def check_assignment_types(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global' o 'main'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("_")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Recorremos los símbolos en el scope de la clase
            for content_name, content_symbol in class_scope.content.items():
                if content_symbol.semantic_type == "attr":
                    attr_name = content_name
                    attr_type = content_symbol.data_type
                    attr_value = content_symbol.value

                    # Buscamos si hay una asignación al atributo en el código
                    for _, symbols in symbol_table.content.items():
                        for symbol_name, symbol in symbols.items():
                            if symbol.semantic_type == "expression" and attr_name in str(symbol.node):
                                expression_node = symbol.node
                                expression_children = expression_node.children
                                if len(expression_children) > 1 and expression_children[1].name == "<-":
                                    right_expr = expression_children[2]

                                    # Verificar tipo del lado derecho
                                    if right_expr.name == "bool_value":
                                        right_type = "Bool"
                                    elif right_expr.name == "integer":
                                        right_type = "Int"
                                    elif right_expr.name == "string":
                                        right_type = "String"
                                    elif right_expr.name == "new":
                                        right_type = right_expr.children[1].name
                                    else:
                                        right_type = symbol_table.search(
                                            right_expr.name, class_scope).data_type

                                    # Comparar tipos
                                    if attr_type != right_type:
                                        feedback.append(SemanticError(name="TypeMismatch",
                                                                      details=f"El tipo de la expresión de asignación para el atributo '{attr_name}' de la clase '{class_name}' no coincide con el tipo del atributo.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope))
                                        all_passed = False

    return all_passed, feedback


def check_type_compatibility(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    def son_tipos_compatibles(tipo1, tipo2, valor_int=None):
        if valor_int is not None:
            # Verificar si tipo1 es Int y tipo2 es Bool
            if tipo1 == "Int" and tipo2 == "Bool" and valor_int in [0, 1]:
                return True

        # Resto de las reglas de compatibilidad
        reglas_compatibilidad = {
            "String": ["String"],
            "Bool": ["Bool"]
            # Agrega más reglas aquí según las necesidades de tu lenguaje
        }

        if tipo1 in reglas_compatibilidad and tipo2 in reglas_compatibilidad[tipo1]:
            return True
        else:
            return False

    # Recorremos todas las clases en la tabla de símbolos
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global' o 'main'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("_")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Recorremos los símbolos en el scope de la clase
            for content_name, content_symbol in class_scope.content.items():
                if content_symbol.semantic_type == "attr":
                    attr_name = content_name
                    attr_type = content_symbol.data_type
                    attr_value = content_symbol.value

                    # Buscamos si hay una asignación al atributo en el código
                    for _, symbols in symbol_table.content.items():
                        for symbol_name, symbol in symbols.items():
                            if symbol.semantic_type == "expression" and attr_name in str(symbol.node):
                                expression_node = symbol.node
                                expression_children = expression_node.children
                                if len(expression_children) > 1 and expression_children[1].name == "<-":
                                    right_expr = expression_children[2]

                                    # Verificar tipo del lado derecho
                                    if right_expr.name == "bool_value":
                                        right_type = "Bool"
                                    elif right_expr.name == "integer":
                                        right_type = "Int"
                                        right_value = right_expr.value  # Obtener el valor de Int
                                    elif right_expr.name == "string":
                                        right_type = "String"
                                    elif right_expr.name == "new":
                                        right_type = right_expr.children[1].name
                                    else:
                                        right_type = symbol_table.search(
                                            right_expr.name, class_scope).data_type

                                    # Comparar tipos con función de compatibilidad
                                    if son_tipos_compatibles(attr_type, right_type, right_value):
                                        # Tipos son compatibles, no hay error
                                        pass
                                    else:
                                        feedback.append(SemanticError(name="TypeCompatibilityError",
                                                                      details=f"La expresión de asignación para el atributo '{attr_name}' de la clase '{class_name}' tiene tipos incompatibles.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope))
                                        all_passed = False

    return all_passed, feedback


def check_method_calls_and_return_values(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("_")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Recorremos los símbolos en el scope de la clase
            for content_name, content_symbol in class_scope.content.items():
                if content_symbol.semantic_type == "method":
                    method_name = content_name
                    method_parameters = content_symbol.parameters
                    method_return_type = content_symbol.data_type

                    # Buscar si hay llamadas al método en el código
                    for _, symbols in symbol_table.content.items():
                        for symbol_name, symbol in symbols.items():
                            if symbol.semantic_type == "expression" and method_name in str(symbol.node):
                                expression_node = symbol.node
                                expression_children = expression_node.children

                                # Verificar si es una llamada a método
                                if len(expression_children) > 1 and expression_children[1].name == "call":
                                    argument_nodes = expression_children[2].children

                                    # Verificar argumentos
                                    if len(argument_nodes) != len(method_parameters):
                                        feedback.append(SemanticError(name="MethodCallArgumentError",
                                                                      details=f"La llamada al método '{method_name}' en la clase '{class_name}' no tiene el número correcto de argumentos.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope))
                                        all_passed = False
                                    else:
                                        for arg_node, param_type in zip(argument_nodes, method_parameters):
                                            # Verificar tipos de argumentos
                                            arg_type = arg_node.name
                                            if not (arg_type == param_type or (arg_type.startswith(("int", "bool")) and param_type == "int")):
                                                feedback.append(SemanticError(name="MethodCallArgumentTypeError",
                                                                              details=f"El tipo del argumento en la llamada al método '{method_name}' en la clase '{class_name}' no coincide con el tipo esperado.",
                                                                              symbol=content_symbol,
                                                                              scope=class_scope))
                                                all_passed = False

                                # Verificar valores de retorno
                                if expression_node.name == "return":
                                    return_value_node = expression_children[1]
                                    return_value_type = return_value_node.name
                                    if not (return_value_type == method_return_type or (return_value_type.startswith(("int", "bool")) and method_return_type == "int")):
                                        feedback.append(SemanticError(name="MethodReturnValueError",
                                                                      details=f"El tipo de valor de retorno en el método '{method_name}' en la clase '{class_name}' no coincide con el tipo de retorno declarado.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope))
                                        all_passed = False

    return all_passed, feedback

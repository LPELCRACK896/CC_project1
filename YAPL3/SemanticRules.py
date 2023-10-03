from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError
from SemanticRules import *
import re
from typing import List

SemanticFeedBack = List[SemanticError]


def not_implemented_true(symbol_table: SymbolTable = None) -> (bool, SemanticFeedBack):
    return True, [SemanticError(name="Sin Implementar", details="Se debe implementar un método antes de usar esta función.", symbol=None, scope=None, line="")]


def not_implemented_false(symbol_table: SymbolTable = None) -> (bool, SemanticFeedBack):
    return False, [SemanticError(name="Sin Implementar", details="Se debe implementar un método antes de usar esta función.", symbol=None, scope=None, line="")]


def class_definition(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("-")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Verificamos si hay atributos y métodos en la clase
            has_attributes = any(content_symbol.semantic_type ==
                                 "attr" for content_symbol in class_scope.content.values())
            has_methods = any(content_symbol.semantic_type ==
                              "method" for content_symbol in class_scope.content.values())

            if not has_attributes and not has_methods:
                class_symbol = symbol_table.search(class_name)
                if class_symbol.name in ["Int", "Bool"]:
                    pass
                    # feedback.append(SemanticError(name="EmptyClass As Should Be",
                    #                               details=f"La clase '{class_name}' no tiene atributos ni métodos.",
                    #                               symbol=class_symbol,
                    #                               scope=class_scope,
                    #                               line=class_symbol.start_line,
                    #                               ))
                    # all_passed = False
                else:
                    feedback.append(SemanticError(name="EmptyClass",
                                                  details=f"La clase '{class_name}' no tiene atributos ni métodos.",
                                                  symbol=class_symbol,
                                                  scope=class_scope,
                                                  line=class_symbol.start_line,
                                                  ))
                    all_passed = False

    return all_passed, feedback


def attributes_definition(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    def check_elements(dictionary, elements_list):
        type_set = set()

        for element in elements_list:
            if element.isnumeric():
                element = int(element)
            if element in dictionary:
                type_set.add(dictionary[element][0])
            elif not isinstance(element, int):
                return False

        # Considerar las combinaciones "Int" y "Bool" para despues realizar el casteo
        if len(type_set) > 1 and {"Int", "Bool"} in (type_set, {"Int"}, {"Bool"}):
            return True

        return len(type_set) <= 1

    attr_dir = {}
    # Recorremos todas las clases en la tabla de símbolos
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global' o 'main'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("-")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Verificar atributos en la clase
            for content_name, content_symbol in class_scope.content.items():
                if content_symbol.semantic_type == "attr":
                    if content_symbol.value == None:
                        content_symbol.value = content_symbol.default_value

                    value = content_symbol.get_value()

                    attr_dir[content_name] = [content_symbol.data_type, value]

                    if content_symbol.data_type == "Int":
                        if not isinstance(value, int) and isinstance(value, str):
                            if value.isnumeric():
                                value = int(value)
                        if value is not None and not isinstance(value, int) and not isinstance(value, str):
                            feedback.append(SemanticError(name="InvalidAttributeValue",
                                                          details=f"El atributo '{content_name}' de la clase '{class_name}' debe tener un valor de tipo Int.",
                                                          symbol=content_symbol,
                                                          scope=class_scope,
                                                          line=content_symbol.start_line))
                            all_passed = False

                        # chequear si es agrupacion de variables
                        if isinstance(value, str):
                            if value not in ["true", "false"]:
                                value = re.split(r'\s*[-+*/]\s*', value)
                                value = [
                                    val for val in value if val.strip() != '']

                                if not check_elements(attr_dir, value):
                                    feedback.append(SemanticError(name="InvalidAttributeValue",
                                                                  details=f"El atributo '{content_name}' de la clase '{class_name}' tiene asignacion de 2 o más variables de diferente tipo.",
                                                                  symbol=content_symbol,
                                                                  scope=class_scope,
                                                                  line=content_symbol.start_line))
                                    all_passed = False

                    elif content_symbol.data_type == "String":
                        if value is not None and not (isinstance(value, str)):
                            feedback.append(SemanticError(name="InvalidAttributeValue",
                                                          details=f"El atributo '{content_name}' de la clase '{class_name}' debe tener un valor de tipo String y estar entre comillas dobles.",
                                                          symbol=content_symbol,
                                                          scope=class_scope,
                                                          line=content_symbol.start_line))
                            all_passed = False
                    elif content_symbol.data_type == "Bool":
                        if value is not None:
                            try:  # si es valor asignado por objetos
                                value_splitted = value.split("=")
                                if len(value_splitted) > 1:
                                    tipo_objeto = []
                                    for val in value_splitted:
                                        tipo_objeto.append(
                                            attr_dir[val][1].split("new")[1])
                                        # verifica que ambos sean objetos
                                        if attr_dir[val][0] != "Object":
                                            feedback.append(SemanticError(name="InvalidAttributeValue",
                                                                          details=f"El atributo '{content_name}' de la clase '{class_name}' debe ser bool asignado por comparacion de objetos.",
                                                                          symbol=content_symbol,
                                                                          scope=class_scope,
                                                                          line=content_symbol.start_line))
                                            all_passed = False
                                    # verifica que ambos sean objetos de misma clase
                                    if all(elemento == tipo_objeto[0] for elemento in tipo_objeto) == False:
                                        feedback.append(SemanticError(name="InvalidAttributeValue",
                                                                      details=f"El atributo '{content_name}' de la clase '{class_name}' debe ser bool asignado por comparacion de objetos de la misma clase.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
                                        all_passed = False
                                else:
                                    if value not in ["true", "false", "1", "0"]:
                                        feedback.append(SemanticError(name="InvalidAttributeValue",
                                                                      details=f"El atributo '{content_name}' de la clase '{class_name}' debe tener un valor de tipo Bool ('true', 'false', '1' o '0', o objetos iguales).",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
                                        all_passed = False

                            except:
                                feedback.append(SemanticError(name="InvalidAttributeValue",
                                                              details=f"El atributo '{content_name}' de la clase '{class_name}' debe tener un valor de tipo Bool ('true', 'false', '1' o '0', o objetos iguales).",
                                                              symbol=content_symbol,
                                                              scope=class_scope,
                                                              line=content_symbol.start_line))
                                all_passed = False

    return all_passed, feedback


def main_check(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    main_method_exists = False
    parameters_null = True
    inherits_null = True
    main_line = 0

    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        class_scope = symbol_table.scopes[class_name]
        # Verificar si la clase 'Main' tiene un método 'main'
        if class_name == "global-Main(class)":
            main_method = class_scope.search_content("main")
            if main_method is not None:
                main_line = main_method.start_line
            else:
                feedback.append(SemanticError(name="MainMethodNotFoundError",
                                              details="La clase 'Main' debe contener un método llamado 'main'.",
                                              symbol=None,
                                              scope=None,
                                              line=main_line))
            if main_method and main_method.semantic_type == "method":
                main_method_exists = True
                if main_method.parameters != []:  # verifica que no tenga parametros
                    parameters_null = False
        if class_name == "global":
            main_method = class_scope.search_content("Main")
            if main_method and main_method.data_type != "Object":
                inherits_null = False

    # Verificar si el método 'main' existe
    if not main_method_exists:
        feedback.append(SemanticError(name="MainMethodNotFoundError",
                                      details="La clase 'Main' debe contener un método llamado 'main'.",
                                      symbol=None,
                                      scope=None,
                                      line=main_line))
        all_passed = False

    # Verificar que el método 'main' no tenga parameters
    if not parameters_null:
        feedback.append(SemanticError(name="MainMethodWithParameters",
                                      details="La clase 'Main' tiene parámetros cuando no debería heredar de nadie.",
                                      symbol=None,
                                      scope=None,
                                      line=main_line))
        all_passed = False

    if not inherits_null:
        feedback.append(SemanticError(name="MainMethodInherits",
                                      details="La clase 'Main' hereda de otra clase cuando no debería.",
                                      symbol=None,
                                      scope=None,
                                      line=main_line-1))
        all_passed = False

    return all_passed, feedback


def execution_start_check(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True
    main_call_exists = False

    # Verificar si existe la línea (new Main).main()

    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        class_scope = symbol_table.scopes[class_name]
        # Verificar si existe el call
        if class_name == "global":
            main_call = class_scope.search_content("(newMain).main()")
            if main_call:
                main_call_exists = True

    if not main_call_exists:
        feedback.append(SemanticError(name="MainCallNotFoundError",
                                      details="El programa debe contener la línea (new Main).main() para iniciar la ejecución.",
                                      symbol=None,
                                      scope=None,
                                      line="última"
                                      ))
        all_passed = False

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
                                          scope=current_scope,
                                          line=symbol.start_line))
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
                                                  scope=scope,
                                                  line=symbol.start_line))
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
                                                          scope=scope,
                                                          line=symbol.start_line))
                            all_passed = False

    return all_passed, feedback


def check_inheritance_relations(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    classes = []
    # Recorremos todas las clases en la tabla de símbolos
    for class_name in symbol_table.scopes:
        if class_name == "global":
            class_content = symbol_table.content[class_name]

            for clase in symbol_table.content[class_name]:
                classes.append(class_content[clase].name)
                if class_content[clase].data_type != "Object" and class_content[clase].data_type not in classes:
                    feedback.append(SemanticError(name="InheritanceError",
                                                  details=f"La clase '{class_content[clase].name}' hereda de '{class_content[clase].data_type}', pero la clase padre no está definida.",
                                                  symbol="",
                                                  scope="",
                                                  line=""))
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
                                                          scope=class_symbol,
                                                          line=""))
                            all_passed = False

    return all_passed, feedback


def check_casting(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    attr_dir = {}

    def cast_bool_to_int(value):
        if value == "true":
            return 1
        elif value == "false":
            return 0
        return value

    def cast_int_to_bool(value):
        if value.isnumeric():
            value = int(value)
        if isinstance(value, int):
            return value != 0
        if value == "true":
            return True
        else:
            return False

    # Recorremos todas las clases en la tabla de símbolos
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global' o 'main'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("-")[1].split(
                "(")[0]  # Extraer el nombre de la clase del scope_id

            # Verificar atributos en la clase
            for content_name, content_symbol in class_scope.content.items():
                if content_symbol.semantic_type == "attr" and content_symbol.data_type in ["Int", "Bool"]:
                    attr_dir[content_name] = [
                        content_symbol.data_type, content_symbol.get_value()]
                    try:
                        value = content_symbol.get_value()
                        value = re.split(r'\s*[-+*/]\s*', value)
                        value = [val for val in value if val.strip() != '']
                        if len(value) == 2:
                            param1 = value[0]
                            param2 = value[1]

                            if (attr_dir[param1][0] == "Int" and attr_dir[param2][0] == "Bool") or (attr_dir[param1][0] == "Bool" and attr_dir[param2][0] == "Int"):

                                if content_symbol.data_type == "Int":
                                    new_value = int(cast_bool_to_int(
                                        attr_dir[param1][1]))
                                    new_value2 = int(cast_bool_to_int(
                                        attr_dir[param2][1]))
                                    if (new_value > 1) or (new_value2 > 1):
                                        feedback.append(SemanticError(name="InvalidCasting",
                                                                      details=f"No es posible realizar el casting implícito de Bool a Int para el atributo '{content_name}' de la clase '{class_name}', porque un valor Int es diferente a 1 o 0.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
                                        all_passed = False
                                    if not isinstance(new_value, int) and not isinstance(new_value2, int):
                                        feedback.append(SemanticError(name="InvalidCasting",
                                                                      details=f"No es posible realizar el casting implícito de Bool a Int para el atributo '{content_name}' de la clase '{class_name}'.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
                                        all_passed = False
                                    else:
                                        content_symbol.value = new_value
                                elif content_symbol.data_type == "Bool":
                                    new_value = cast_int_to_bool(
                                        attr_dir[param1][1])
                                    new_value2 = cast_int_to_bool(
                                        attr_dir[param2][1])
                                    if not isinstance(new_value, bool) and not isinstance(new_value2, bool):
                                        feedback.append(SemanticError(name="InvalidCasting",
                                                                      details=f"No es posible realizar el casting implícito de Int a Bool para el atributo '{content_name}' de la clase '{class_name}'.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
                                        all_passed = False
                    except:
                        pass

    return all_passed, feedback


def check_assignment_types(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    # Recorremos todas las clases en la tabla de símbolos
    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue  # Pasar a la siguiente clase si es 'global' o 'main'

        if class_scope.scope_id.endswith("(class)"):
            class_name = class_scope.scope_id.split("-")[1].split(
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
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
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
            class_name = class_scope.scope_id.split("-")[1].split(
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
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
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
            class_name = class_scope.scope_id.split("-")[1].split(
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
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
                                        all_passed = False
                                    else:
                                        for arg_node, param_type in zip(argument_nodes, method_parameters):
                                            # Verificar tipos de argumentos
                                            arg_type = arg_node.name
                                            if not (arg_type == param_type or (arg_type.startswith(("int", "bool")) and param_type == "int")):
                                                feedback.append(SemanticError(name="MethodCallArgumentTypeError",
                                                                              details=f"El tipo del argumento en la llamada al método '{method_name}' en la clase '{class_name}' no coincide con el tipo esperado.",
                                                                              symbol=content_symbol,
                                                                              scope=class_scope,
                                                                              line=content_symbol.start_line))
                                                all_passed = False

                                # Verificar valores de retorno
                                if expression_node.name == "return":
                                    return_value_node = expression_children[1]
                                    return_value_type = return_value_node.name
                                    if not (return_value_type == method_return_type or (return_value_type.startswith(("int", "bool")) and method_return_type == "int")):
                                        feedback.append(SemanticError(name="MethodReturnValueError",
                                                                      details=f"El tipo de valor de retorno en el método '{method_name}' en la clase '{class_name}' no coincide con el tipo de retorno declarado.",
                                                                      symbol=content_symbol,
                                                                      scope=class_scope,
                                                                      line=content_symbol.start_line))
                                        all_passed = False

    return all_passed, feedback


def check_boolean_object_expression_type(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue

        if class_scope.scope_id.endswith("(method)"):

            # Iterate through symbols in class scope
            for content_symbol in class_scope.content.values():
                if content_symbol.semantic_type == "expression":
                    expression_node = content_symbol.get_value()
                    if "if" in content_symbol.name or "while" in content_symbol.name:
                        if expression_node != "bool_value":
                            feedback.append(SemanticError(name="InvalidBooleanExpression",
                                                          details=f"La expresión en la estructura de control '{expression_node}' en el método '{class_scope.scope_id}' debe tener un tipo de dato estático de tipo Bool.",
                                                          symbol=content_symbol,
                                                          scope=class_scope,
                                                          line=content_symbol.start_line))
                            all_passed = False
                    if "if" in content_symbol.name and content_symbol.data_type != "block":
                        feedback.append(SemanticError(name="IfNoBlock",
                                                      details=f"La expresión en la estructura de control '{expression_node.name}' en el método '{class_scope.scope_id}' debe ser de tipo block.",
                                                      symbol=content_symbol,
                                                      scope=class_scope,
                                                      line=content_symbol.start_line))
                        all_passed = False
                    if "while" in content_symbol.name and content_symbol.data_type != "Object":
                        feedback.append(SemanticError(name="WhileNoObject",
                                                      details=f"La expresión en la estructura de control '{expression_node.name}' en el método '{class_scope.scope_id}' debe ser de tipo object.",
                                                      symbol=content_symbol,
                                                      scope=class_scope,
                                                      line=content_symbol.start_line))
                        all_passed = False

    return all_passed, feedback


def check_unitary(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):
    feedback = []
    all_passed = True

    for scope_id, class_scope in symbol_table.scopes.items():
        if "global" == scope_id:
            continue

        if class_scope.scope_id.endswith("(method)"):

            # Iterate through symbols in class scope
            for content_symbol in class_scope.content.values():
                if content_symbol.type_of_expression == "unitary":
                    resultado = re.search(
                        r'\((.*?)\)\s*(.*)', content_symbol.name)
                    texto_despues_del_parentesis = resultado.group(2)
                    result = texto_despues_del_parentesis.split()
                    if result[0] == "not":
                        if result[1] != "true" and result[1] != "false":
                            feedback.append(SemanticError(name="UnaryNotBadlyUsed",
                                                          details=f"La expresión unaria '{texto_despues_del_parentesis}' en el método '{class_scope.scope_id}' no esta bien aplicada.",
                                                          symbol=content_symbol,
                                                          scope=class_scope,
                                                          line=content_symbol.start_line))
                            all_passed = False
                    if result[0] == "~" and not result[1].isnumeric():
                        feedback.append(SemanticError(name="UnaryNotBadlyUsed",
                                                      details=f"La expresión unaria '{texto_despues_del_parentesis}' en el método '{class_scope.scope_id}' no esta bien aplicada.",
                                                      symbol=content_symbol,
                                                      scope=class_scope,
                                                      line=content_symbol.start_line))
                        all_passed = False

    return all_passed, feedback

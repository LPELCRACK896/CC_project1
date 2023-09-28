def general_scope_quadruples(symbol_table):
    # Define una lista para almacenar las cuádruplas generadas
    quadruples = []

    # Define un contador para las variables temporales
    temp_counter = 0

    # Comienza el procesamiento de expresiones en todos los ámbitos de la tabla de símbolos
    for scope_id, scope in symbol_table.scopes.items():
        if scope_id == "global":
            for symbol_name, symbol in scope.content.items():
                # (newMain).main() temporal
                if symbol_name not in ["Object", "IO", "Int", "String", "Bool", "(newMain).main()"]:
                    if symbol.semantic_type == "class":
                        # Generar cuádruplas para la definición de la clase
                        class_id = symbol_name
                        inherits = symbol.data_type if symbol.data_type != "Object" else "inherits_False"

                        # Generar cuádruplas para la definición de la clase
                        quadruples.append(
                            ("=", "tokenActual", "RW_CLASS", f"T{temp_counter}"))
                        temp_counter += 1
                        quadruples.append(
                            ("ifFalse", f"T{temp_counter - 1}", "goto", f"L_error"))
                        temp_counter += 1
                        quadruples.append(
                            ("=", "tokenSiguiente", "_", class_id))
                        quadruples.append(
                            ("=", "tokenSiguiente", "_", f"T{temp_counter}"))
                        temp_counter += 1
                        quadruples.append(
                            ("if", f"T{temp_counter - 1}", "RW_INHERITS", f"L_inherits"))
                        temp_counter += 1
                        quadruples.append(("goto", f"L_body"))
                        quadruples.append(
                            ("L_inherits", "=", "tokenSiguiente", f"T{temp_counter}"))
                        temp_counter += 1
                        quadruples.append(
                            ("=", f"T{temp_counter - 1}", f"{inherits} | type", f"T{temp_counter}"))
                        temp_counter += 1
                        quadruples.append(("goto", f"L_body"))
                        quadruples.append(
                            ("L_body", "=", "tokenSiguiente", "'{'"))
                        quadruples.append(("=", "tokenSiguiente", "'}'", "_"))
                        quadruples.append(("", "", "", ""))

                    # PROCESAR CADA ÁMBITO PARA GENERAR CUÁDRUPAS
                    rec_symbol = symbol_table.search(symbol_name)
                    rec_scope = symbol_table.get_symbol_scope(rec_symbol)

                    for symbol_name_scope, symbol_scope in rec_scope.content.items():
                        if symbol_scope.semantic_type == "attr":
                            # Generar cuádruplas para la definición del atributo
                            attr_id = symbol_name_scope
                            attr_type = symbol_scope.data_type

                            # Asignar una nueva variable temporal
                            temp_var = f"T{temp_counter}"
                            temp_counter += 1

                            quadruples.append(
                                ("=", "tokenActual", "ID", f"T{temp_counter}"))
                            temp_counter += 1
                            quadruples.append(
                                ("ifFalse", f"T{temp_counter - 1}", "goto", "L_error"))
                            temp_counter += 1
                            quadruples.append(
                                ("=", "tokenSiguiente", "_", ":"))
                            quadruples.append(
                                ("=", "tokenSiguiente", "_", attr_type))
                            quadruples.append(
                                ("=", "tokenSiguiente", "_", "<-"))
                            quadruples.append(
                                ("ifFalse", "tokenActual", "goto", "L_semicolon"))
                            quadruples.append(
                                ("=", "tokenSiguiente", "_", "expr"))
                            quadruples.append(
                                ("L_semicolon", "=", "tokenSiguiente", "_", ";"))

                            # Utilizar temp_var en lugar de "T1", "T2", etc.
                            quadruples.append(("=", temp_var, "expr", "_"))
                            quadruples.append(("", "", "", ""))

                            # Puedes agregar aquí el procesamiento adicional del atributo, como almacenar el nombre,
                            # tipo y, si existe, la expresión de asignación en la tabla de símbolos o donde corresponda.

                            quadruples.append(("goto", "End"))

                    quadruples.append(("L_error", "", "", ""))
                    quadruples.append(("End", "", "", ""))

    return quadruples

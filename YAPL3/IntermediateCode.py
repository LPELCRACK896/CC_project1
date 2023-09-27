def generate_expression_quadruples(symbol_table):
    # Define a list to store the generated quadruples
    quadruples = []

    # Helper function to generate unique label names
    label_counter = 0

    def generate_unique_label():
        nonlocal label_counter
        label_counter += 1
        return f"L{label_counter}"

    # Helper function to generate quadruples for binary operations
    def generate_binary_quadruple(operator, operand1, operand2, result):
        quadruples.append((operator, operand1, operand2, result))

    # Helper function to generate quadruples for unary operations
    def generate_unary_quadruple(operator, operand, result):
        quadruples.append((operator, operand, None, result))

    # Function to recursively process expressions in a scope
    def process_expressions_in_scope(scope):
        nonlocal quadruples

        for symbol_name, symbol in scope.content.items():
            if symbol.semantic_type == "expression":
                # Process expression
                T = f"T{len(quadruples) + 1}"

                # Example: For ID, you can generate a quadruple like this:
                # (=, tokenActual, ID, T)
                quadruples.append(("=", symbol.name, "ID", T))

                # Example: For constants (e.g., INT, STRING, RW_FALSE, RW_TRUE), you can generate like this:
                # (=, tokenActual, constant, T)
                quadruples.append(("=", symbol.name, symbol.semantic_type, T))

                # Process sub-expressions if applicable
                if symbol.semantic_type == "operator":
                    process_expression(symbol)

                # Handle other expression types (assignments, etc.) here

    # Helper function to recursively process expressions
    def process_expression(expr):
        nonlocal quadruples

        if expr.semantic_type == "operator":
            # Handle operators
            T3 = f"T{len(quadruples) + 1}"

            # Example: For operators, you can generate a quadruple like this:
            # (=, tokenActual, operator, T3)
            quadruples.append(("=", expr.name, "operator", T3))

            # Process left and right operands
            process_expression(expr.left)
            process_expression(expr.right)

            # Generate quadruple for the operator
            generate_binary_quadruple(
                expr.name, expr.left.name, expr.right.name, None)

        # Handle other expression types (constants, assignments, etc.) here

    # Start processing expressions in all scopes of the symbol table
    for scope_id, scope in symbol_table.scopes.items():
        if scope_id != "global":
            process_expressions_in_scope(scope)

    return quadruples


def generate_type_quadruples(symbol_table):
    # Define a list to store the generated quadruples
    quadruples = []

    # Helper function to generate unique label names
    label_counter = 0

    def generate_unique_label():
        nonlocal label_counter
        label_counter += 1
        return f"L{label_counter}"

    # Helper function to generate quadruples for checking types
    def generate_type_check_quadruple(type_name, target_label):
        T = f"T{len(quadruples) + 1}"
        quadruples.append(("=", "tokenActual", type_name, T))
        quadruples.append(("ifTrue", T, "goto", target_label))

    # Type checking for ID or 'SELF_TYPE'
    generate_type_check_quadruple("ID", "L_self_type")

    # Type checking for built-in types
    generate_type_check_quadruple("SELF_TYPE", "L_int")
    generate_type_check_quadruple("Int", "L_string")
    generate_type_check_quadruple("String", "L_bool")
    generate_type_check_quadruple("Bool", "L_io")
    generate_type_check_quadruple("IO", "L_object")

    # Handle the case of 'Object'
    T7 = f"T{len(quadruples) + 1}"
    quadruples.append(("=", "tokenActual", "Object", T7))
    quadruples.append(("ifTrue", T7, "goto", "L_error"))

    # Error handling for invalid types
    quadruples.append(("goto", "L_error"))

    # Labels for processing valid types
    quadruples.append(("L_self_type", None, None, None))
    quadruples.append(("L_int", None, None, None))
    quadruples.append(("L_string", None, None, None))
    quadruples.append(("L_bool", None, None, None))
    quadruples.append(("L_io", None, None, None))
    quadruples.append(("L_object", None, None, None))

    # Label for error handling
    quadruples.append(("L_error", None, None, None))

    return quadruples

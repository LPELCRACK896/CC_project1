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
            if symbol.semantic_type == "expr":
                # Process expression
                # (=, tokenActual, expr, T)
                # (ifTrue, T, goto, L_calculation)
                T = f"T{len(quadruples) + 1}"
                quadruples.append(("=", symbol.name, "expr", T))
                quadruples.append(
                    ("ifTrue", T, "goto", generate_unique_label()))

                # Process sub-expressions
                for sub_expr in symbol.subexpressions:
                    process_expression(sub_expr)

    # Helper function to recursively process expressions
    def process_expression(expr):
        nonlocal quadruples

        if expr.semantic_type == "operator":
            # Handle operators
            # (=, tokenActual, operator, T3)
            # (ifTrue, T3, goto, L_operator)
            T3 = f"T{len(quadruples) + 1}"
            quadruples.append(("=", expr.name, "operator", T3))
            quadruples.append(("ifTrue", T3, "goto", generate_unique_label()))

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

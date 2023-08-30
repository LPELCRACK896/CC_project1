from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, SemanticFeedBack



def check_inhertance(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):

    feedback = []
    all_passed = True

    all_classes_dict = symbol_table.global_scope.get_all_classees()
    
    classes: set = set(all_classes_dict.keys())

    didnt_passed_valid_inhertance = []

    # Revisa la herencia sesa valida
    while classes:
        i_class = classes.pop()
        error_content, found_an_error, classes_checked, class_w_error = symbol_table.check_inhertance_chain(class_name=i_class)
        if found_an_error:
            symbol: Symbol = all_classes_dict.get(i_class)
            name,  content= error_content.split(":") 
            class_chain = "> ".join(classes_checked)
            feedback.append(SemanticError(
                name = name,
                details=f"{content}. {class_chain}.({class_w_error})",
                symbol=symbol,
                scope=symbol_table.global_scope,
                line = str(symbol.start_line)

                ))
            didnt_passed_valid_inhertance.extend(classes_checked)
        classes = classes.difference(set(classes_checked))
        all_passed = all_passed and not found_an_error

    classified_classes = list(set(all_classes_dict.keys()).difference(set(didnt_passed_valid_inhertance)))
    basic_classes = ["Object", "IO", "Int", "String", "Bool"]

    for i_class in classified_classes:

        if i_class in basic_classes:
            continue

        class_symbol: Symbol = all_classes_dict.get(i_class)

        class_scope: Scope = symbol_table.scopes.get(f"{class_symbol.scope}-{i_class}(class)")

        parent_class_scope: Scope = symbol_table.scopes.get(f"global-{class_symbol.data_type}(class)")

        parent_methods = parent_class_scope.get_all_methods()
        class_methods = class_scope.get_all_methods()

        for class_method, class_method_symbol in class_methods.items():
            # Asume que se busca herencia siempre que se escriba un metodo con el mismo nombre que el de su clase padre
            if class_method in parent_methods:
                # Revisa la firma
                parent_symbol: Symbol = parent_methods[class_method]
                parent_parameters_passing_method = parent_symbol.parameter_passing_method
                parent_parameters = parent_symbol.parameters
                parent_return_type = parent_symbol.data_type

                son_parameters = class_method_symbol.parameters
                son_return_type = class_method_symbol.data_type

                # Dado que es heredado le hereda el mismo tipo de metodo para pasar parametros
                class_method_symbol.parameter_passing_method = parent_parameters_passing_method

                if son_return_type != parent_return_type:
                    feedback.append(SemanticError(
                        name= "MissMatchFirmReturn",
                        details = f"On method {class_method} of {i_class} class, the inherited method from {class_symbol.data_type}. Expected to return {parent_return_type} type but got {son_return_type} instead.",
                        symbol= class_method_symbol,
                        scope=class_method_symbol.scope,
                        line= class_method_symbol.start_line
                    ))

                if len(son_parameters) == len(parent_parameters):
                    for i, (son_parameter_i, parent_paramter_i) in enumerate(zip(son_parameters, parent_parameters)):
                        if parent_paramter_i[0] != son_parameter_i[0]:
                            feedback.append(SemanticError(
                                name  = "MisMatchFirmNameFormal",
                                details= f"On method {class_method} of {i_class} class, the inherited method from {class_symbol.data_type}. Expected as {i+1} parameter the name \"{parent_paramter_i[0]}\" but got \"{son_parameter_i[0]}\" instead.",
                                symbol= class_method_symbol,
                                scope=class_method_symbol.scope,
                                line= class_method_symbol.start_line
                            ))
                                
                        if parent_paramter_i[1] != son_parameter_i[1]:
                            feedback.append(SemanticError(
                                name  = "MisMatchFirmTypeFormal",
                                details= f"On method {class_method} of {i_class} class, the inherited method from {class_symbol.data_type}. Expected as {i+1} parameter the type \"{parent_paramter_i[1]}\" but got \"{son_parameter_i[1]}\" instead.",
                                symbol= class_method_symbol,
                                scope=class_method_symbol.scope,
                                line= class_method_symbol.start_line
                            ))      
                else:
                    feedback.append(SemanticError(
                        name= "MissMatchParametersInInherateMethod",
                        details=f"On method {class_method} of {i_class}, the inherited method from {class_symbol.data_type}. Parent method expects to have {len(parent_parameters)} parameters but got {len(son_parameters)} instead.",
                        symbol=class_method_symbol,
                        scope = class_method_symbol.scope,
                        line = class_method_symbol.start_line ))
                    
                    for i in range(max(len(parent_parameters), len(son_parameters))):

                        if i >= len(parent_parameters): # No existe en el padre >> El padre tiene menos parametros = El hijo excede lo parametros
                            feedback.append(SemanticError(
                                name = "MissMatchFirm",
                                details= f"On method {class_method} of {i_class}, the inherited method from {class_symbol.data_type}. Parent method doesnt not expect a parameter {i+1} , but got {son_parameters[i]} as {i+1} parameter.",
                                symbol= class_method_symbol,
                                scope=class_method_symbol.scope,
                                line= class_method_symbol.start_line
                            ))

                        elif i >= len(son_parameters): # No existe en el hijo >> El hijo tiene menos parametros = El Padre tiene mas parametros
                            feedback.append(SemanticError(
                                name = "MissMatchFirm",
                                details= f"On method {class_method} of {i_class}, the inherited method from {class_symbol.data_type}. Parent method expects a parameter {i+1}  {parent_parameters[i]}, but got nothing instead.",
                                symbol= class_method_symbol,
                                scope=class_method_symbol.scope,
                                line= class_method_symbol.start_line
                            ))
                        else: # Existe en ambos 
                            parent_paramter_i = parent_parameters[i]
                            son_parameter_i = son_parameters[i]
                            # El nombre del parametro
                            if parent_paramter_i[0] != son_parameter_i[0]:
                                feedback.append(SemanticError(
                                    name  = "MisMatchFirmNameFormal",
                                    details= f"On method {class_method} of {i_class} class, the inherited method from {class_symbol.data_type}. Expected as {i+1} parameter the name \"{parent_paramter_i[0]}\" but got \"{son_parameter_i[0]}\"",
                                    symbol= class_method_symbol,
                                    scope=class_method_symbol.scope,
                                    line= class_method_symbol.start_line
                                ))
                                
                            if parent_paramter_i[1] != son_parameter_i[1]:
                                feedback.append(SemanticError(
                                    name  = "MisMatchFirmTypeFormal",
                                    details= f"On method {class_method} of {i_class} class, the inherited method from {class_symbol.data_type}. Expected as {i+1} parameter the type \"{parent_paramter_i[1]}\" but got \"{son_parameter_i[1]}\"",
                                    symbol= class_method_symbol,
                                    scope=class_method_symbol.scope,
                                    line= class_method_symbol.start_line
                                ))

    return all_passed, feedback

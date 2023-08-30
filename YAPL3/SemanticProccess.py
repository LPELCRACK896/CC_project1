from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, ActiveRulesType, SemanticFeedBack
from SemanticRules import *


active_rules: ActiveRulesType = {
    "1_class_definition": class_definition,  # EZ: lista
    "1_attributes_definition": attributes_definition,  # nose nocreo al 90%
    "2_has_class_main_containing_main_method": main_check,  # EZ: ia
    "3_main_call":  execution_start_check,  # EZ: tambien ia
    "4_local_and_global_scope": scope_check,  # EZ: no
    "4_visibility_per_scope": visibility_check,  # Intermedio: ia
    # Facil a priori: ya fijo
    "5_inheritance_relations": not_implemented_true,
    # No se: necesita revision
    "5_inheritance_override_logic": not_implemented_true,
    "6_default_values": not_implemented_true,  # EZ: ia estaba desde la symbol table
    "7_casting_int_bool": check_casting,  # EZ:
    "8_assignation_expresions_type_on_each_side": check_assignment_types,  # Intermedio: si?
    # Compleja: talvez?
    "8_assignation_expresions_compatible_and_rule": check_type_compatibility,
    "9_method_calls_and_return_values": check_method_calls_and_return_values,  # Complejo
    "10_control_structures": check_boolean_object_expression_type,  # Facil a priori
    # Un poco más dificil, implica implementar guardar expresiones en tabla de simbolos o algo por el estilo.
    "11_operators_and_expressions": not_implemented_true,
    "12_special_io_class": not_implemented_true,  # Dios nos salve
    "extra_ambit_rules": not_implemented_true,  # Dios nos salve
    "extra_methods_and_return_values": not_implemented_true,  # Dios nos salve
}


def check_semantic(symbol_table: SymbolTable = None, active_rules: ActiveRulesType = active_rules) -> (bool, SemanticFeedBack):
    feedback: SemanticFeedBack = []
    all_rules_passed = True
    for rule,  method in active_rules.items():
        method_passed, errors = method(symbol_table)
        all_rules_passed = all_rules_passed and method_passed
        feedback.extend(errors)
        print(rule, " >>> ", method_passed)

    return all_rules_passed, feedback

# Pruebas


if __name__ == "__main__":
    passed, errors = check_semantic()
    print(1)

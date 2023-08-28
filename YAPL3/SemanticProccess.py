from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, ActiveRulesType, SemanticFeedBack
from SemanticRules import *


active_rules: ActiveRulesType = {
    "1_class_definition": class_definition,  # lista
    "1_attributes_definition": attributes_definition,  # nose nocreo
    "2_has_class_main_containing_main_method": main_check,  # EZ
    "3_main_call":  not_implemented_true,  # EZ
    "4_local_and_global_scope": not_implemented_true,  # EZ
    "4_visibility_per_scope": not_implemented_true,  # Intermedio
    "5_inheritance_relations": not_implemented_true,  # Facil a priori
    "5_inheritance_override_logic": not_implemented_true,  # No se
    "6_default_values": not_implemented_true,  # EZ
    "7_casting_int_bool_string": not_implemented_true,  # EZ
    "8_assignation_expresions_type_on_each_side": not_implemented_true,  # Intermedio
    "8_assignation_expresions_compatible_and_rule": not_implemented_true,  # Compleja
    "9_method_calls_and_return_values": not_implemented_true,  # Complejo
    "10_control_structures": not_implemented_true,  # Facil a priori
    # Un poco más dificil, implica implementar guardar expresiones en tabla de simbolos o algo por el estilo.
    "11_operators_and_expressions": not_implemented_true,
    "12_special_io_class": not_implemented_true,  # Dios nos salve
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

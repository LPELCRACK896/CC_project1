from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, ActiveRulesType
from SemanticRules import *
from SemanticRules2 import *

from typing import List

SemanticFeedBack = List[SemanticError]

active_rules: ActiveRulesType = {
    "1_class_definition": class_definition,  # EZ: lista
    "1_attributes_definition": attributes_definition,  # nose nocreo al 90%
    "2_has_class_main_containing_main_method": main_check,  # EZ: ia
    "3_main_call":  execution_start_check,  # EZ: tambien ia
    "4_local_and_global_scope": scope_check,  # EZ: no
    "4_visibility_per_scope": visibility_check,  # Intermedio: ia
    # Facil a priori: ya fijo
    "5_inheritance_relations": check_inhertance,
    # No se: necesita revision
    "7_casting_int_bool": check_casting,  # EZ:
    "8_assignation_expresions_type_on_each_side": check_assignment_types,  # Intermedio: si?
    # Compleja: talvez?
    "8_assignation_expresions_compatible_and_rule": check_type_compatibility,
    "9_method_calls_and_return_values": check_method_calls_and_return_values,  # Complejo
    "10_control_structures": check_boolean_object_expression_type,  # Facil a priori
    # Un poco más dificil, implica implementar guardar expresiones en tabla de simbolos o algo por el estilo.
    "extra_unitary_check": check_unitary,
    "single_declaration_on_scope": single_declaration_identifier,
    "method_availabilty": check_method
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

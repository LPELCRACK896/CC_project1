from SymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, ActiveRulesType
from SemanticRules import *
from SemanticRules2 import *

from typing import List

SemanticFeedBack = List[SemanticError]

active_rules: ActiveRulesType = {
    "1_class_definition": class_definition,  # EZ: lista
    "2_has_class_main_containing_main_method": main_check,  # EZ: ia
    "3_main_call":  execution_start_check,  # EZ: tambien ia
    "4_local_and_global_scope": scope_check,  # EZ: no
    "4_visibility_per_scope": visibility_check,  # Intermedio: ia
    # Facil a priori: ya fijo
    "5_inheritance_relations": check_inheritance,
    # No se: necesita revision
    # Compleja: talvez?
    "8_assignation_expresions_compatible_and_rule": check_type_compatibility,
    # Un poco más dificil, implica implementar guardar expresiones en tabla de simbolos o algo por el estilo.
    "single_declaration_on_scope": single_declaration_identifier,
    "method_availabilty": errors_detected_by_noted_nodes
}


def check_semantic(symbol_table: SymbolTable = None, active_rules: ActiveRulesType = active_rules) -> (bool, SemanticFeedBack):
    feedback: SemanticFeedBack = []
    all_rules_passed = True
    for rule,  method in active_rules.items():
        method_passed, errors = method(symbol_table)
        all_rules_passed = all_rules_passed and method_passed
        feedback.extend(errors)
        # print(rule, " >>> ", method_passed)

    return all_rules_passed, feedback

# Pruebas


if __name__ == "__main__":
    passed, errors = check_semantic()
    print(1)

from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, ActiveRulesType, SemanticFeedBack
from SemanticRules import *


active_rules: ActiveRulesType = {
    "1_class_definition": not_implemented_true, # EZ
    "1_attributes_definition": not_implemented_true, #EZ
    "2_has_class_main_containing_main_method": not_implemented_true, # EZ
    "3_main_call":  not_implemented_true, # EZ
    "4_local_and_global_scope": not_implemented_true, # EZ
    "4_visibility_per_scope": not_implemented_true, # Intermedio
    "5_inheritance_relations": not_implemented_true, # Facil a priori
    "5_inheritance_override_logic": not_implemented_true, # No se 
    "6_default_values": not_implemented_true, # EZ
    "7_casting_int_bool_string": not_implemented_true, # EZ
    "8_assignation_expresions_type_on_each_side": not_implemented_true, # Intermedio
    "8_assignation_expresions_compatible_and_rule": not_implemented_true, # Compleja
    "9_method_calls_and_return_values": not_implemented_true, # Complejo
    "10_control_structures": not_implemented_true, # Facil a priori
    "11_operators_and_expressions": not_implemented_true, # Un poco más dificil, implica implementar guardar expresiones en tabla de simbolos o algo por el estilo. 
    "12_special_io_class": not_implemented_true, # Dios nos salve
}

def check_semantic(symbol_table: SymbolTable = None, active_rules: ActiveRulesType = active_rules) -> (bool, SemanticFeedBack):
    feddback : SemanticFeedBack = []
    all_rules_passed = True
    for rule,  method  in active_rules.items():
        method_passed, errors = method(symbol_table)
        all_rules_passed = all_rules_passed and method_passed
        feddback.extend(errors)

    return all_rules_passed, feddback

# Pruebas 

if  __name__ == "__main__":
    passed, errors = check_semantic()
    print(1)

    

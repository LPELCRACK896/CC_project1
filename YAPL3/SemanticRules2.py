from ClassSymbolTable import SymbolTable, Symbol, Scope
from SemanticCommon import SemanticError, SemanticFeedBack



def check_inhertance(symbol_table: SymbolTable) -> (bool, SemanticFeedBack):

    feedback = []
    all_passed = True
        
    
    classes = symbol_table.global_scope.get_all_classees()

    
    for class_name, class_symbol in classes.items():
        parent_class_str = class_symbol.data_type
        
        if parent_class_str not in classes:
            feedback.append(SemanticError(
                name="Unexsting reference of inheratance.", 
                details=f"On inherance, {class_name} try to inherate from {parent_class_str}, but \"{parent_class_str}\" doesnt seem to be define in yapl program.", 
                symbol=class_symbol, 
                scope = symbol_table.global_scope, 
                line = None
                ))
            continue
        
        parent_class: Symbol = classes[class_symbol.data_type]
        parent_methods = parent_class

        print(1)

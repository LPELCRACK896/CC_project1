grammar YAPL3;

program: ((mainClassDef classDef*)| (classDef*|mainClassDef )) mainCall? EOF;

// Palabras reservadas
rw_inherits: ('I'|'i')('N'|'n')('H'|'h')('E'|'e')('R'|'r')('I'|'i')('T'|'t')('S'|'s'); //inherits
rw_isvoid: ('I'|'i')('S'|'s')('V'|'v')('O'|'o')('I'|'i')('D'|'d'); //isvoid
rw_while: ('W'|'w')('H'|'h')('I'|'i')('L'|'l')('E'|'e'); //while
rw_class: ('C'|'c')('L'|'l')('A'|'a')('S'|'s')('S'|'s');  //Class
rw_loop: ('L'|'l')('O'|'o')('O'|'o')('P'|'p'); //loop
rw_else: ('E'|'e')('L'|'l')('S'|'s')('E'|'e');  //else
rw_pool: ('P'|'p')('O'|'o')('O'|'o')('L'|'l'); //pool
rw_then:('T'|'t')('H'|'h')('E'|'e')('N'|'n'); //then
rw_new: ('N'|'n')('E'|'e')('W'|'w'); //new
rw_not: ('N'|'n')('O'|'o')('T'|'t'); //not
rw_fi: ('F'|'f')('I'|'i');  //fi 
rw_if: ('I'|'i')('F'|'f');  //if
rw_in: ('I'|'i')('N'|'n');  //in
rw_true: 'true';
rw_false: 'false';  

mainClassDef: rw_class 'Main' '{' mainMethod '}';
mainMethod: 'main' '(' ')' '{'(expr ';')* '}';

classDef: rw_class CLASS_ID ('inherits' CLASS_ID)? '{' feature* '}';
feature: attr | method;
attr: ID ':' type ('<-' expr)? ';';
method: ID '(' formals ')' ':' type '{' (expr ';')* func_return '}';
formals: formal? (',' formal)*;
formal: ID ':' type;
type: ID | 'SELF_TYPE' | 'Int' | 'String' | 'Bool' | 'IO' | 'Object';
expr: 
     ID '<-' expr
    | expr '@' type '.' ID '(' expr (',' expr)* ')'
    | ID '(' expr (',' expr)* ')'
    | 'if' expr  'then' expr 'else' expr 'fi'
    | 'while' expr 'loop' expr 'pool'
    | '{' expr (';' expr)* '}'
    | 'let' ID ':' type ('<-' expr)? (',' ID ':' type ('<-' expr)?)* 'in' expr
    | expr '.' ID '(' expr (',' expr)* ')'
    | 'new' classDef
    | 'isvoid' expr
    | expr op=OP expr
    | '(' expr ')'
    | ID
    | INT
    | STRING
    | rw_false
    | rw_true
    ;

mainCall: '(' 'new' 'Main' ')' '.' 'main' '(' ')';
func_return:
    'return' expr ';'
    ;
comparation_operators:
    | '<'
    | '>'
    | '<='
    | '>='
    | '=='
    | '!='
    ;
bool_value: 
    | rw_true
    | rw_false
    | comparation
    ;

comparation: 
    | ID comparation_operators (INT|STRING)
    | ID comparation_operators ID
    ;

// Lexer rules


//Otros
ID: [a-z][a-zA-Z0-9]*;
INT: [0-9]+;
STRING: '"' (~["\r\n\\] | '\\' ["\\/bfnrt])* '"';
WS : [ \t\r\n]+ -> skip;
COMMENT: '(*' .*? '*)' -> skip;
INLINE_COMMENT: '--' ~('\n')* -> skip;
OP: ('+' | '-' | '*' | '/' | '<' | '<=' | '=' | '>=' | '>');
CLASS_ID: [A-Z][a-zA-Z0-9]*;
grammar YAPL3;

program: ((mainClassDef? classDef*)| (classDef* mainClassDef? )) mainCall? EOF;



mainClassDef: RW_CLASS 'Main' '{' mainMethod '}';
mainMethod: 'main' '(' ')' '{'(expr ';')* '}';

classDef: RW_CLASS CLASS_ID ('inherits' CLASS_ID)? '{' feature* '}';
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
    | 'if' bool_value  'then' expr 'else' expr 'fi'
    | 'while' bool_value'loop' expr 'pool'
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
    | RW_FALSE
    | RW_TRUE
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
    | RW_FALSE
    | RW_TRUE
    | comparation
    ;

comparation: 
    | ID comparation_operators (INT|STRING)
    | ID comparation_operators ID
    ;

// Lexer rules

// Palabras reservadas - Case Insensitive
RW_INHERITS: ('I'|'i')('N'|'n')('H'|'h')('E'|'e')('R'|'r')('I'|'i')('T'|'t')('S'|'s');
RW_ISVOID: ('I'|'i')('S'|'s')('V'|'v')('O'|'o')('I'|'i')('D'|'d');
RW_WHILE: ('W'|'w')('H'|'h')('I'|'i')('L'|'l')('E'|'e');
RW_CLASS: ('C'|'c')('L'|'l')('A'|'a')('S'|'s')('S'|'s');
RW_LOOP: ('L'|'l')('O'|'o')('O'|'o')('P'|'p');
RW_ELSE: ('E'|'e')('L'|'l')('S'|'s')('E'|'e');
RW_POOL: ('P'|'p')('O'|'o')('O'|'o')('L'|'l');
RW_THEN: ('T'|'t')('H'|'h')('E'|'e')('N'|'n');
RW_NEW: ('N'|'n')('E'|'e')('W'|'w');
RW_NOT: ('N'|'n')('O'|'o')('T'|'t');
RW_FI: ('F'|'f')('I'|'i');
RW_IF: ('I'|'i')('F'|'f');
RW_IN: ('I'|'i')('N'|'n');
RW_TRUE: 'true';
RW_FALSE: 'false';

//Otros



ID: [a-z][a-zA-Z0-9]*;
INT: [0-9]+;
STRING: '"' (~["\r\n\\] | '\\' ["\\/bfnrt])* '"';
WS : [ \t\r\n]+ -> skip;
COMMENT: '(*' .*? '*)' -> skip;
INLINE_COMMENT: '--' ~('\n')* -> skip;
OP: ('+' | '-' | '*' | '/' | '<' | '<=' | '=' | '>=' | '>');
CLASS_ID: [A-Z][a-zA-Z0-9]*;
grammar YAPL;

// Parser rules
program: classDef* EOF;
classDef: 'class' CLASS_ID ('inherits' CLASS_ID)? '{' feature* '}';
feature: attr | method;
attr: ID ':' type ('<-' expr)? ';';
method: ID '(' formals ')' ':' type '{' (expr ';')* func_return '}';
formals: formal? (',' formal)*;
formal: ID ':' type;
type: ID | 'SELF_TYPE' | 'Int' | 'String' | 'Bool' | 'IO' | 'Object';
expr: 
      'if' (expr | bool_value) 'then' expr 'else' expr 'fi'
    | 'while' (expr | bool_value )'loop' expr 'pool'
    | '{' expr (';' expr)* '}'
    | 'let' ID ':' type ('<-' expr)? (',' ID ':' type ('<-' expr)?)* 'in' expr
    | ID '<-' expr
    | expr '.' ID '(' expr (',' expr)* ')'
    | expr '@' type '.' ID '(' expr (',' expr)* ')'
    | ID '(' expr (',' expr)* ')'
    | 'isvoid' expr
    | 'new' ID
    | ID
    | INT
    | STRING
    | 'true'
    | 'false'
    | '(' expr ')'
    | expr op=OP expr
    ;

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
    | 'true'
    | 'false'
    | comparation
    ;

comparation: 
    | ID comparation_operators (INT|STRING)
    | ID comparation_operators ID
    ;

// Lexer rules
ID: [a-z][a-zA-Z0-9]*;
INT: [0-9]+;
STRING: '"' (~["\r\n\\] | '\\' ["\\/bfnrt])* '"';
WS : [ \t\r\n]+ -> skip;
COMMENT: '/*' .*? '*/' -> skip;
OP: ('+' | '-' | '*' | '/');
CLASS_ID: [A-Z][a-zA-Z0-9]*;

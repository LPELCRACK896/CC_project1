grammar YAPL3;

program: classDef* (expr';')* EOF;

// Parser rules
classDef: RW_CLASS CLASS_ID (RW_INHERITS (CLASS_ID | type))? '{' feature* '}';
feature: attr | method;
attr: ID ':' type ('<-' expr)? ';';
method: ID '(' formals ')' ':' type '{' (expr ';')* func_return '}';
formals: formal? (',' formal)*;
formal: ID ':' type;
type: ID | 'SELF_TYPE' | 'Int' | 'String' | 'Bool' | 'IO' | 'Object' | CLASS_ID;
expr:
      ID '<-' expr
    | expr '@' (type | CLASS_ID) '.' ID '(' (expr (',' expr)* )?')'
    | ID '(' (expr (',' expr)* )? ')'
    | 'if' expr 'then' expr 'else' expr 'fi'
    | 'while' expr 'loop' expr 'pool'
    | '{' expr (';' expr)* '}'
    | 'let' (ID ':' type ('<-' expr)?)? (',' ID ':' type ('<-' expr)?)* 'in' '[' expr ']'
    | expr '.' ID '(' (expr (',' expr)* )? ')'
    | 'new' (CLASS_ID | type)
    | 'isvoid' expr
    | 'not' expr
    | '~' expr
    | expr op expr
    | '(' expr ')'
    | ID
    | INT
    | STRING
    | RW_FALSE
    | RW_TRUE
    ;
func_return: 'return' expr ';';

op: OP | LE | GE;

// Lexer rules
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

ID: [a-z][a-zA-Z0-9]*;
INT: [0-9]+;
STRING: '"' (~["\r\n\\] | '\\' ["\\/bfnrt])* '"';
WS : [ \t\r\n]+ -> skip;
COMMENT: '(*' .*? '*)' -> skip;
INLINE_COMMENT: '--' ~('\n')* -> skip;
CLASS_ID: [A-Z][a-zA-Z0-9]*;

OP: '+' | '-' | '*' | '/' | '<' | '=' | '>';
LE: '<=';
GE: '>=';

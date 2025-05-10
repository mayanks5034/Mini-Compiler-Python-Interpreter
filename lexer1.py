import ply.lex as lex

# List of token names
tokens = (
    'NUMBER', 'IDENTIFIER', 'STRING',  
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULUS',
    'EQUALS', 'LPAREN', 'RPAREN', 'COMMA', 'COLON',
    'PRINT', 'TRUE', 'FALSE',  
    'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
    'AND', 'OR', 'NOT',
    'IF', 'ELSE', 'WHILE', 'FOR', 'IN',
    'DEF', 'RETURN', 'LBRACKET', 'RBRACKET',
    'TRY', 'EXCEPT',  # ✅ Added Try-Except tokens
    'LEN', 'UPPER', 'LOWER', 'REPLACE', 'STRIP', 'DOT'  # ✅ Added string function tokens
)

# Token regex definitions
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MODULUS = r'%'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COMMA   = r','  
t_COLON   = r':' 
t_LBRACKET = r'\['  # Left bracket
t_RBRACKET = r'\]'  # Right bracket

# Boolean & Comparison Operators
t_GT = r'>'
t_LT = r'<'
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='
t_NE = r'!='
t_DOT = r'\.'

# Keywords
reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'in': 'IN',
    'def': 'DEF',
    'return': 'RETURN',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'True': 'TRUE',
    'False': 'FALSE',
    'try': 'TRY',  # ✅ Added Try
    'except': 'EXCEPT',  # ✅ Added Except
    'len': 'LEN',  # ✅ Added len() function
    'upper': 'UPPER',  # ✅ Added upper() function
    'lower': 'LOWER',  # ✅ Added lower() function
    'replace': 'REPLACE',  # ✅ Added replace() function
    'strip': 'STRIP'  # ✅ Added strip() function
}

# Handle numbers (supporting both integers and floating-point numbers)
def t_NUMBER(t):
    r'\d+(\.\d+)?'  
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# Handle identifiers (variables, functions, etc.)
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Check if it's a keyword
    return t

# Handle string literals (supporting both single & double quotes)
def t_STRING(t):
    r'(\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\')'  
    t.value = t.value[1:-1]  # Remove surrounding quotes
    return t

# Handle newlines properly (Only update line number)
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

# Ignore spaces and tabs
t_ignore = ' \t'

# Ignore comments
def t_COMMENT(t):
    r'\#.*'
    pass  # Ignore the comment
    return None  # Don't return a token

# Error handling with detailed position
def find_column(input_text, token):
    """ Returns the column number of the token in the line """
    last_newline = input_text.rfind('\n', 0, token.lexpos)
    return (token.lexpos - last_newline) if last_newline != -1 else token.lexpos

def t_error(t):
    column = find_column(t.lexer.lexdata, t)
    print(f"Lexer Error: Illegal character '{t.value[0]}' at line {t.lineno}, column {column}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

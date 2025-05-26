from ply import lex
import json

# List of token names
tokens = (
    'NUMBER',
    'STRING',
    'IDENTIFIER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MODULO',
    'EQUALS',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'COLON',
    'COMMA',
    'DOT',
    'GT',
    'LT',
    'GE',
    'LE',
    'EQ',
    'NE',
    'AND',
    'OR',
    'NOT',
    'TRUE',
    'FALSE',
    'IF',
    'ELSE',
    'WHILE',
    'FOR',
    'IN',
    'DEF',
    'RETURN',
    'BREAK',
    'CONTINUE',
    'TRY',
    'EXCEPT',
    'PRINT',
    'LEN',
    'RANGE',
    'NEWLINE'
)

# Regular expression rules for simple tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_GT = r'>'
t_LT = r'<'
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='
t_NE = r'!='

# Reserved words
reserved = {
    'True': 'TRUE',
    'False': 'FALSE',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'in': 'IN',
    'def': 'DEF',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'try': 'TRY',
    'except': 'EXCEPT',
    'print': 'PRINT',
    'len': 'LEN',
    'range': 'RANGE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT'
}

# Track indentation
indent_stack = [0]

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')
    return t

# Add a function to handle end of file
def t_eof(t):
    # Generate DEDENT tokens for any remaining indentation levels
    while len(indent_stack) > 1:
        indent_stack.pop()
        t.type = 'DEDENT'
        return t
    return None

# Regular expression rules with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"[^"\\](\\.[^"\\])"|\'[^\'\\](\\.[^\'\\])\''
    # Remove quotes and handle escape sequences
    t.value = t.value[1:-1].encode().decode('unicode_escape')
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'

# Error handling rule
def t_error(t):
    # Instead of raising an error, we'll skip the character and continue
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def tokenize(code):
    """Tokenize the input code and return a list of tokens with their details."""
    # Reset the lexer state
    lexer.lineno = 1
    lexer.input(code)
    tokens = []
    
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_info = {
            "type": tok.type,
            "value": str(tok.value),
            "line": tok.lineno,
            "lexpos": tok.lexpos
        }
        tokens.append(token_info)
    
    return tokens

def format_token_output(tokens):
    """Format the tokens into a structured, readable output."""
    if not tokens:
        return "No tokens found in the input code."
    
    # Create a formatted table-like output
    output = ["Lexical Analysis Results:\n"]
    output.append("Token Type".ljust(20) + "Token Value".ljust(30) + "Line".ljust(10) + "Position")
    output.append("-" * 70)
    
    for token in tokens:
        type_str = str(token['type']).ljust(20)
        value_str = str(token['value']).ljust(30)
        line_str = str(token['line']).ljust(10)
        pos_str = str(token['lexpos'])
        output.append(f"{type_str}{value_str}{line_str}{pos_str}")
    
    # Add a summary
    output.append("\nToken Summary:")
    token_types = {}
    for token in tokens:
        token_types[token['type']] = token_types.get(token['type'], 0) + 1
    
    for type_name, count in sorted(token_types.items()):
        output.append(f"- {type_name}: {count} tokens")
    
    # Add token categories
    output.append("\nToken Categories:")
    categories = {
        "Keywords": ["IF", "ELSE", "WHILE", "FOR", "IN", "DEF", "RETURN", "BREAK", "CONTINUE", "TRY", "EXCEPT", "PRINT", "LEN", "RANGE", "AND", "OR", "NOT", "TRUE", "FALSE"],
        "Operators": ["PLUS", "MINUS", "TIMES", "DIVIDE", "MODULO", "EQUALS", "GT", "LT", "GE", "LE", "EQ", "NE"],
        "Delimiters": ["LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "COLON", "COMMA", "DOT"],
        "Literals": ["NUMBER", "STRING"],
        "Identifiers": ["IDENTIFIER"],
        "Structure": ["NEWLINE"]
    }
    
    for category, types in categories.items():
        count = sum(token_types.get(t, 0) for t in types)
        output.append(f"- {category}: {count} tokens")
    
    return "\n".join(output)

# Example usage for testing
if _name_ == "_main_":
    test_codes = {
        "Simple Print": 'print("Hello World")',
        "Arithmetic": "x = 5.5 + 3 * 2",
        "For Loop": "for i in range(5):\n    print(i)",
        "While Loop": "while x > 0:\n    x = x - 1",
        "List Operation": "numbers = [1, 2, 3]\nprint(numbers[0])",
        "Function": "def add(a, b):\n    return a + b",
        "String Method": 'text = "Hello"\nprint(text.upper())',
        "If-Else": "if x > 10:\n    print('Big')\nelse:\n    print('Small')"
    }
    
    for name, code in test_codes.items():
        print(f"\n=== Testing {name} ===")
        print("Input Code:")
        print(code)
        print("\nLexical Analysis Output:")
        tokens = tokenize(code)
        print(format_token_output(tokens))
        print("=" * 70)

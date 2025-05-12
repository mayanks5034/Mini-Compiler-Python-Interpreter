import ply.yacc as yacc
from lexer1 import tokens
from ast_nodes1 import (
    Number, Identifier, BinaryOp, Assign, Boolean, Print,
    IfElse, WhileLoop, ForLoop, FunctionDef, FunctionCall, Return, String,
    ListNode, IndexNode, UnaryOp, TryExcept, LenFunction, StringMethod
)

# Grammar rules
def p_statements(p):
    '''statements : statements statement
                  | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement_assign(p):
    'statement : IDENTIFIER EQUALS expression'
    p[0] = Assign(p[1], p[3])
    # Add the result of the expression to the symbol_table
    symbol_table[p[1]] = p[3].evaluate(symbol_table)

# Add a global symbol table
symbol_table = {}

def p_statement_print(p):
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = Print(p[3])
    print(p[3].evaluate(symbol_table))  # ✅ Pass symbol_table, not {}

# ✅ Conditional Statements (if-else)
def p_statement_if_else(p):
    '''statement : IF expression COLON statements
                 | IF expression COLON statements ELSE COLON statements'''
    if len(p) == 5:
        p[0] = IfElse(p[2], p[4], None)
    else:
        p[0] = IfElse(p[2], p[4], p[7])

# In the evaluate method for IfElse:
def evaluate(self, symbol_table):
    condition_value = self.condition.evaluate(symbol_table)
    if condition_value:
        for statement in self.true_branch:
            statement.evaluate(symbol_table)
    elif self.false_branch:
        for statement in self.false_branch:
            statement.evaluate(symbol_table)

# ✅ While Loop
def p_statement_while(p):
    'statement : WHILE expression COLON statements'
    p[0] = WhileLoop(p[2], p[4])

# ✅ For Loop
def p_statement_for(p):
    'statement : FOR IDENTIFIER IN expression COLON statements'
    p[0] = ForLoop(p[2], p[4], p[6])

# ✅ Function Definition
def p_statement_function_def(p):
    'statement : DEF IDENTIFIER LPAREN parameters RPAREN COLON statements'
    # Register function in symbol table
    symbol_table[p[2]] = FunctionDef(p[2], p[4], p[7])
    p[0] = symbol_table[p[2]]

def p_parameters(p):
    '''parameters : IDENTIFIER
                  | parameters COMMA IDENTIFIER
                  | empty'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    else:
        p[0] = p[1] + [p[3]]

# ✅ Function Call
def p_expression_function_call(p):
    'expression : IDENTIFIER LPAREN arguments RPAREN'
    # Check if function is defined in symbol_table
    if p[1] in symbol_table:
        p[0] = FunctionCall(p[1], p[3])
    else:
        raise Exception(f"Function '{p[1]}' is not defined")

def p_arguments(p):
    '''arguments : expression
                 | arguments COMMA expression
                 | empty'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    else:
        p[0] = p[1] + [p[3]]

# ✅ Return Statement
def p_statement_return(p):
    'statement : RETURN expression'
    p[0] = Return(p[2])

# ✅ Expressions
def p_expression_binop(p):
    '''expression : expression MINUS expression
                  | expression DIVIDE expression
                  | expression MODULUS expression
                  | expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression'''
    p[0] = BinaryOp(p[1], p[2], p[3])

def p_expression_boolean(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = Boolean(True if p[1] == "True" else False)

# ✅ Boolean Operators (`not` needs `UnaryOp`)
def p_expression_boolop(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    p[0] = BinaryOp(p[1], p[2], p[3])

def p_expression_not(p):
    'expression : NOT expression'
    p[0] = UnaryOp(p[1], p[2])

def p_expression_string(p):
    'expression : STRING'
    p[0] = String(p[1])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = Number(p[1])

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    p[0] = Identifier(p[1])

def p_expression_list(p):
    'expression : LBRACKET expression_list RBRACKET'
    p[0] = ListNode(p[2])

def p_expression_list_elements(p):
    '''expression_list : expression
                       | expression COMMA expression_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_expression_indexing(p):
    'expression : expression LBRACKET expression RBRACKET'
    p[0] = IndexNode(p[1], p[3])

# ✅ Try-Except Handling
def p_statement_try_except(p):
    'statement : TRY COLON statements EXCEPT COLON statements'
    p[0] = TryExcept(p[3], p[6])

# ✅ String Concatenation and Repetition
def p_expression_string_operations(p):
    '''expression : expression PLUS expression
                  | expression TIMES expression'''
    p[0] = BinaryOp(p[1], p[2], p[3])

# ✅ Built-in `len()` Function
def p_expression_len(p):
    'expression : LEN LPAREN expression RPAREN'
    p[0] = LenFunction(p[3])

# ✅ String Methods
def p_expression_string_methods(p):
    '''expression : expression DOT UPPER LPAREN RPAREN
                  | expression DOT LOWER LPAREN RPAREN
                  | expression DOT STRIP LPAREN RPAREN
                  | expression DOT REPLACE LPAREN expression COMMA expression RPAREN'''
    if len(p) == 6:
        p[0] = StringMethod(p[1], p[3])  # upper(), lower(), strip()
    else:
        p[0] = StringMethod(p[1], p[3], [p[5], p[7]])  # replace(old, new)

# Handle Empty Productions
def p_empty(p):
    'empty :'
    p[0] = None

# Handle Syntax Errors
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' (line {p.lineno}, position {p.lexpos}).")
    else:
        print("Unexpected end of input! Ensure all expressions and statements are complete.")

# Build the parser
parser = yacc.yacc()

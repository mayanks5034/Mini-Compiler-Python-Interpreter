from ply import yacc
from lexer import tokens
from ast_nodes import *

# Define operator precedence - from lowest to highest
precedence = (
    ('left', 'OR'),                    # Lowest precedence
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS'),              # Unary minus
    ('right', 'NOT'),                 # Logical not
    ('nonassoc', 'LPAREN', 'RPAREN'), # Parentheses precedence
)

# Grammar rules
def p_program(p):
    '''program : statements'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + ([p[2]] if p[2] is not None else [])

def p_statement(p):
    '''statement : print_stmt
                | assign_stmt
                | if_stmt
                | while_stmt
                | for_stmt
                | function_def
                | return_stmt
                | break_stmt
                | continue_stmt
                | try_except_stmt
                | NEWLINE'''
    p[0] = p[1]

def p_print_stmt(p):
    '''print_stmt : PRINT LPAREN expr RPAREN
                 | PRINT expr'''
    if len(p) == 5:
        p[0] = Print(p[3])
    else:
        p[0] = Print(p[2])

def p_assign_stmt(p):
    '''assign_stmt : IDENTIFIER EQUALS expr
                  | IDENTIFIER LBRACKET expr RBRACKET EQUALS expr'''
    if len(p) == 4:
        p[0] = Assign(Identifier(p[1]), p[3])
    else:
        p[0] = ListAssign(Identifier(p[1]), p[3], p[6])

def p_if_stmt(p):
    '''if_stmt : IF expr COLON statements
               | IF expr COLON statements ELSE COLON statements'''
    if len(p) == 5:
        p[0] = IfElse(p[2], p[4], [])
    else:
        p[0] = IfElse(p[2], p[4], p[7])

def p_while_stmt(p):
    '''while_stmt : WHILE expr COLON statements'''
    p[0] = WhileLoop(p[2], p[4])

def p_for_stmt(p):
    '''for_stmt : FOR IDENTIFIER IN expr COLON statements'''
    p[0] = ForLoop(Identifier(p[2]), p[4], p[6])

def p_function_def(p):
    '''function_def : DEF IDENTIFIER LPAREN param_list RPAREN COLON statements'''
    p[0] = FunctionDef(p[2], p[4], p[7])

def p_param_list(p):
    '''param_list : IDENTIFIER
                 | param_list COMMA IDENTIFIER
                 | empty'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[3]]

def p_return_stmt(p):
    '''return_stmt : RETURN expr
                  | RETURN'''
    if len(p) == 3:
        p[0] = Return(p[2])
    else:
        p[0] = Return(None)

def p_break_stmt(p):
    '''break_stmt : BREAK'''
    p[0] = Break()

def p_continue_stmt(p):
    '''continue_stmt : CONTINUE'''
    p[0] = Continue()

def p_try_except_stmt(p):
    '''try_except_stmt : TRY COLON statements EXCEPT COLON statements'''
    p[0] = TryExcept(p[3], p[6])

def p_expr(p):
    '''expr : term
            | expr PLUS term
            | expr MINUS term
            | expr TIMES term
            | expr DIVIDE term
            | expr MODULO term
            | expr GT term
            | expr LT term
            | expr GE term
            | expr LE term
            | expr EQ term
            | expr NE term
            | expr AND term
            | expr OR term'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(p[2], p[1], p[3])

def p_term(p):
    '''term : factor
            | NOT term
            | MINUS term %prec UMINUS'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryOp(p[1], p[2])

def p_factor(p):
    '''factor : NUMBER
              | STRING
              | TRUE
              | FALSE
              | IDENTIFIER
              | list_expr
              | function_call
              | string_method
              | len_function
              | range_call
              | LPAREN expr RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_list_expr(p):
    '''list_expr : LBRACKET expr_list RBRACKET
                | IDENTIFIER LBRACKET expr RBRACKET'''
    if len(p) == 4:
        p[0] = ListNode(p[2])
    else:
        p[0] = IndexNode(Identifier(p[1]), p[3])

def p_expr_list(p):
    '''expr_list : expr
                | expr_list COMMA expr
                | empty'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[3]]

def p_function_call(p):
    '''function_call : IDENTIFIER LPAREN expr_list RPAREN
                    | IDENTIFIER LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = FunctionCall(Identifier(p[1]), p[3])
    else:
        p[0] = FunctionCall(Identifier(p[1]), [])

def p_string_method(p):
    '''string_method : IDENTIFIER DOT IDENTIFIER LPAREN expr_list RPAREN
                    | IDENTIFIER DOT IDENTIFIER LPAREN RPAREN'''
    if len(p) == 7:
        p[0] = StringMethod(Identifier(p[1]), p[3], p[5])
    else:
        p[0] = StringMethod(Identifier(p[1]), p[3], [])

def p_len_function(p):
    '''len_function : LEN LPAREN expr RPAREN'''
    p[0] = LenFunction(p[3])

def p_range_call(p):
    '''range_call : RANGE LPAREN expr_list RPAREN
                 | RANGE LPAREN RPAREN'''
    if len(p) == 5:
        args = p[3]
        while len(args) < 3:
            args.append(None)
        p[0] = RangeCall(args[0], args[1], args[2])
    else:
        p[0] = RangeCall(None, None, None)

def p_expression_funccall(p):
    'expression : IDENTIFIER LPAREN arg_list RPAREN'
    p[0] = FunctionCall(p[1], p[3])

def p_arg_list(p):
    '''arg_list : expression
                | arg_list COMMA expression
                | empty'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[3]]

def p_empty(p):
    'empty :'
    p[0] = None

# Error handling
def p_error(p):
    if p:
        # Get the line number and column
        line = p.lineno
        col = p.lexpos - p.lexer.lexdata.rfind('\n', 0, p.lexpos)
        
        # Get the line content
        lines = p.lexer.lexdata.split('\n')
        if 0 <= line-1 < len(lines):
            line_content = lines[line-1]
            pointer = ' ' * (col-1) + '^'
        else:
            line_content = ""
            pointer = ""
            
        # Common error patterns and suggestions
        error_msg = f"Syntax error at line {line}, column {col}:\n"
        error_msg += f"{line_content}\n{pointer}\n"
        
        # Add specific error messages based on the token
        if p.type == 'COLON':
            error_msg += "Missing colon ':' after if/for/while statement or function definition"
        elif p.type == 'RPAREN':
            error_msg += "Missing closing parenthesis ')'"
        elif p.type == 'LBRACKET':
            error_msg += "Missing closing bracket ']'"
        elif p.type == 'RBRACKET':
            error_msg += "Missing opening bracket '['"
        elif p.type == 'LPAREN':
            error_msg += "Missing closing parenthesis ')'"
        elif p.type == 'EQUALS':
            error_msg += "Invalid assignment. Use '=' for assignment"
        elif p.type == 'IDENTIFIER':
            error_msg += f"Unexpected identifier '{p.value}'. Check for missing operators or parentheses"
        elif p.type == 'NUMBER':
            error_msg += f"Unexpected number '{p.value}'. Check for missing operators or parentheses"
        elif p.type == 'STRING':
            error_msg += f"Unexpected string '{p.value}'. Check for missing operators or parentheses"
        else:
            error_msg += f"Unexpected token '{p.value}'"
            
        # Add suggestions for common errors
        error_msg += "\n\nCommon fixes:\n"
        error_msg += "1. Check for missing colons after if/for/while statements\n"
        error_msg += "2. Ensure proper indentation (use spaces or tabs consistently)\n"
        error_msg += "3. Check for matching parentheses and brackets\n"
        error_msg += "4. Verify operator usage and precedence\n"
        error_msg += "5. Make sure all statements are properly terminated"
        
        raise SyntaxError(error_msg)
    else:
        raise SyntaxError("Unexpected end of file. Check for unclosed blocks or missing statements")

# Build the parser
parser = yacc.yacc()

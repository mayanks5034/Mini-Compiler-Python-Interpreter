import tkinter as tk
from tkinter import ttk, font, filedialog
import sys
import io
from lexer import lexer, tokenize, format_token_output
from myparser import parser
from interpreter import Interpreter
import re
from ast_nodes import *  # Import all AST node classes at the top of script.py

# ---------- Functions ----------

def go_to_learning():
    """Show the learning screen."""
    hide_all()
    learn_screen.pack(fill=tk.BOTH, expand=True)

def go_to_testing():
    """Show the testing screen."""
    hide_all()
    testing_screen.pack(fill=tk.BOTH, expand=True)

def go_to_optimizer():
    """Show the optimizer screen."""
    hide_all()
    optimizer_screen.pack(fill=tk.BOTH, expand=True)

def go_to_compiler_phases():
    """Show the compiler phases screen."""
    hide_all()
    compiler_phases_screen.pack(fill=tk.BOTH, expand=True)

def back_to_welcome():
    """Return to the welcome screen."""
    hide_all()
    welcome_screen.pack(fill=tk.BOTH, expand=True)

def hide_all():
    """Hide all main screens."""
    welcome_screen.pack_forget()
    testing_screen.pack_forget()
    compiler_phases_screen.pack_forget()
    optimizer_screen.pack_forget()
    learn_screen.pack_forget()

def execute_code():
    """Execute code from the testing screen."""
    code = input_text.get("1.0", tk.END)
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        exec(code, globals())
        output = redirected_output.getvalue()
        output_box.insert(tk.END, output)
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}")
    finally:
        sys.stdout = old_stdout
    output_box.config(state=tk.DISABLED)

def optimize_ast(node):
    # Recursively optimize AST nodes (constant folding, etc.)
    if isinstance(node, BinaryOp):
        left = optimize_ast(node.left)
        right = optimize_ast(node.right)
        if isinstance(left, Number) and isinstance(right, Number):
            if node.op == '+': return Number(left.value + right.value)
            if node.op == '-': return Number(left.value - right.value)
            if node.op == '*': return Number(left.value * right.value)
            if node.op == '/': return Number(left.value / right.value)
        return BinaryOp(left, node.op, right)
    elif isinstance(node, UnaryOp):
        expr = optimize_ast(node.expr)
        if isinstance(expr, Number):
            if node.op == '-': return Number(-expr.value)
        return UnaryOp(node.op, expr)
    elif isinstance(node, Assign):
        return Assign(node.name, optimize_ast(node.expr))
    elif isinstance(node, Print):
        return Print(optimize_ast(node.expr))
    elif isinstance(node, IfElse):
        cond = optimize_ast(node.condition)
        if isinstance(cond, Boolean):
            if cond.value:
                return [optimize_ast(stmt) for stmt in node.if_body]
            elif node.else_body:
                return [optimize_ast(stmt) for stmt in node.else_body]
            else:
                return []
        return IfElse(cond, [optimize_ast(stmt) for stmt in node.if_body], [optimize_ast(stmt) for stmt in node.else_body] if node.else_body else None)
    elif isinstance(node, WhileLoop):
        return WhileLoop(optimize_ast(node.condition), [optimize_ast(stmt) for stmt in node.body])
    elif isinstance(node, ForLoop):
        return ForLoop(node.var, optimize_ast(node.iterable), [optimize_ast(stmt) for stmt in node.body])
    elif isinstance(node, FunctionDef):
        return FunctionDef(node.name, node.params, [optimize_ast(stmt) for stmt in node.body])
    elif isinstance(node, FunctionCall):
        return FunctionCall(node.name, [optimize_ast(arg) for arg in node.args])
    elif isinstance(node, ListNode):
        return ListNode([optimize_ast(elem) for elem in node.elements])
    elif isinstance(node, IndexNode):
        return IndexNode(optimize_ast(node.expr), optimize_ast(node.index))
    elif isinstance(node, StringMethod):
        return StringMethod(optimize_ast(node.expr), node.method, [optimize_ast(arg) for arg in node.args])
    elif isinstance(node, LenFunction):
        return LenFunction(optimize_ast(node.expr))
    elif isinstance(node, RangeCall):
        return RangeCall(optimize_ast(node.start) if node.start else None, optimize_ast(node.stop) if node.stop else None, optimize_ast(node.step) if node.step else None)
    else:
        return node

def ast_to_code(node):
    # Recursively convert AST back to code
    if isinstance(node, Assign):
        return f"{ast_to_code(node.name)} = {ast_to_code(node.expr)}"
    elif isinstance(node, BinaryOp):
        return f"({ast_to_code(node.left)} {node.op} {ast_to_code(node.right)})"
    elif isinstance(node, UnaryOp):
        return f"{node.op}{ast_to_code(node.expr)}"
    elif isinstance(node, Number):
        return str(node.value)
    elif isinstance(node, String):
        return repr(node.value)
    elif isinstance(node, Boolean):
        return str(node.value)
    elif isinstance(node, Identifier):
        return node.name
    elif isinstance(node, Print):
        return f"print({ast_to_code(node.expr)})"
    elif isinstance(node, IfElse):
        code = f"if {ast_to_code(node.condition)}:\n"
        for stmt in node.if_body:
            code += f"    {ast_to_code(stmt)}\n"
        if node.else_body:
            code += f"else:\n"
            for stmt in node.else_body:
                code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, WhileLoop):
        code = f"while {ast_to_code(node.condition)}:\n"
        for stmt in node.body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, ForLoop):
        code = f"for {ast_to_code(node.var)} in {ast_to_code(node.iterable)}:\n"
        for stmt in node.body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, FunctionDef):
        code = f"def {node.name}({', '.join(ast_to_code(param) for param in node.params)}):\n"
        for stmt in node.body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, FunctionCall):
        return f"{ast_to_code(node.name)}({', '.join(ast_to_code(arg) for arg in node.args)})"
    elif isinstance(node, ListNode):
        return f"[{', '.join(ast_to_code(elem) for elem in node.elements)}]"
    elif isinstance(node, IndexNode):
        return f"{ast_to_code(node.expr)}[{ast_to_code(node.index)}]"
    elif isinstance(node, StringMethod):
        return f"{ast_to_code(node.expr)}.{node.method}({', '.join(ast_to_code(arg) for arg in node.args)})"
    elif isinstance(node, LenFunction):
        return f"len({ast_to_code(node.expr)})"
    elif isinstance(node, RangeCall):
        args = [ast_to_code(arg) for arg in [node.start, node.stop, node.step] if arg is not None]
        return f"range({', '.join(args)})"
    elif isinstance(node, Return):
        return f"return {ast_to_code(node.expr)}"
    elif isinstance(node, Break):
        return "break"
    elif isinstance(node, Continue):
        return "continue"
    elif isinstance(node, TryExcept):
        code = f"try:\n"
        for stmt in node.try_body:
            code += f"    {ast_to_code(stmt)}\n"
        code += f"except:\n"
        for stmt in node.except_body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    else:
        return ""

def optimize_code():
    raw_code = optimizer_input.get("1.0", tk.END).strip()
    optimizer_output.config(state=tk.NORMAL)
    optimizer_output.delete("1.0", tk.END)

    if not raw_code:
        optimizer_output.insert(tk.END, "⚠️ Please enter some Python code to optimize.")
        optimizer_output.config(state=tk.DISABLED)
        return

    try:
        ast = parser.parse(raw_code)
        if ast is None:
            raise Exception("Failed to parse code")
        # Optimize each statement in the AST
        optimized_ast = []
        for node in ast:
            opt = optimize_ast(node)
            if isinstance(opt, list):
                optimized_ast.extend(opt)
            else:
                optimized_ast.append(opt)
        # Convert optimized AST back to code
        optimized_code = "\n".join(ast_to_code(node) for node in optimized_ast if node)
        optimizer_output.insert(tk.END, optimized_code)
    except Exception as e:
        optimizer_output.insert(tk.END, f"❌ Error during optimization:\n{str(e)}")

    optimizer_output.config(state=tk.DISABLED)

def copy_to_clipboard():
    optimized_code = optimizer_output.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(optimized_code)
    root.update()

def download_optimized_code():
    optimized_code = optimizer_output.get("1.0", tk.END)
    if not optimized_code.strip():
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".py",
        filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
        title="Save Optimized Code"
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(optimized_code)

def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def toggle_section(frame):
    if frame.winfo_viewable():
        frame.pack_forget()
    else:
        frame.pack(fill="x", padx=20, pady=(0, 10))

# --- Helper to ensure all phase functions handle both lists and single nodes ---
def ensure_list(ast):
    if isinstance(ast, list):
        return ast
    elif ast is None:
        return []
    else:
        return [ast]

# Define the original pretty_print_ast function first
def pretty_print_ast(node, indent="", is_last=True):
    # Define prefix based on whether it's the last child
    prefix = "└── " if is_last else "├── "
    
    if isinstance(node, list):
        result = []
        for i, n in enumerate(node):
            result.append(pretty_print_ast(n, indent, i == len(node) - 1))
        return "\n".join(result)
    elif hasattr(node, "__class__"):
        cname = node.__class__.__name__
        
        if cname == "Assign":
            return f"{indent}{prefix}Assignment\n{indent}    ├── Variable: {node.name}\n{indent}    └── Value: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "BinaryOp":
            return f"{indent}{prefix}Binary Operation: {node.op}\n{indent}    ├── Left: {pretty_print_ast(node.left, indent + '    ', False)}\n{indent}    └── Right: {pretty_print_ast(node.right, indent + '    ', True)}"
        elif cname == "UnaryOp":
            return f"{indent}{prefix}Unary Operation: {node.op}\n{indent}    └── Expression: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "Number":
            return f"{indent}{prefix}Number: {node.value}"
        elif cname == "String":
            return f"{indent}{prefix}String: '{node.value}'"
        elif cname == "Boolean":
            return f"{indent}{prefix}Boolean: {node.value}"
        elif cname == "Identifier":
            return f"{indent}{prefix}Identifier: {node.name}"
        elif cname == "Print":
            return f"{indent}{prefix}Print Statement\n{indent}    └── Expression: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "IfElse":
            result = [f"{indent}{prefix}If-Else Statement"]
            result.append(f"{indent}    ├── Condition: {pretty_print_ast(node.condition, indent + '    ', False)}")
            result.append(f"{indent}    ├── If Body:")
            for i, stmt in enumerate(node.if_body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.if_body) - 1 and not node.else_body))
            if node.else_body:
                result.append(f"{indent}    └── Else Body:")
                for i, stmt in enumerate(node.else_body):
                    result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.else_body) - 1))
            return "\n".join(result)
        elif cname == "WhileLoop":
            result = [f"{indent}{prefix}While Loop"]
            result.append(f"{indent}    ├── Condition: {pretty_print_ast(node.condition, indent + '    ', False)}")
            result.append(f"{indent}    └── Body:")
            for i, stmt in enumerate(node.body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.body) - 1))
            return "\n".join(result)
        elif cname == "ForLoop":
            result = [f"{indent}{prefix}For Loop"]
            result.append(f"{indent}    ├── Variable: {node.var}")
            result.append(f"{indent}    ├── Iterable: {pretty_print_ast(node.iterable, indent + '    ', False)}")
            result.append(f"{indent}    └── Body:")
            for i, stmt in enumerate(node.body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.body) - 1))
            return "\n".join(result)
        elif cname == "FunctionDef":
            result = [f"{indent}{prefix}Function Definition: {node.name}"]
            result.append(f"{indent}    ├── Parameters: {', '.join(str(p) for p in node.params)}")
            result.append(f"{indent}    └── Body:")
            for i, stmt in enumerate(node.body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.body) - 1))
            return "\n".join(result)
        elif cname == "FunctionCall":
            result = [f"{indent}{prefix}Function Call: {node.name}"]
            result.append(f"{indent}    └── Arguments:")
            for i, arg in enumerate(node.args):
                result.append(pretty_print_ast(arg, indent + '        ', i == len(node.args) - 1))
            return "\n".join(result)
        elif cname == "ListNode":
            result = [f"{indent}{prefix}List"]
            for i, elem in enumerate(node.elements):
                result.append(pretty_print_ast(elem, indent + '    ', i == len(node.elements) - 1))
            return "\n".join(result)
        elif cname == "IndexNode":
            return f"{indent}{prefix}List Index\n{indent}    ├── List: {pretty_print_ast(node.list_expr, indent + '    ', False)}\n{indent}    └── Index: {pretty_print_ast(node.index_expr, indent + '    ', True)}"
        elif cname == "ListAssign":
            return f"{indent}{prefix}List Assignment\n{indent}    ├── List: {pretty_print_ast(node.list_expr, indent + '    ', False)}\n{indent}    ├── Index: {pretty_print_ast(node.index_expr, indent + '    ', False)}\n{indent}    └── Value: {pretty_print_ast(node.value, indent + '    ', True)}"
        elif cname == "Return":
            return f"{indent}{prefix}Return Statement\n{indent}    └── Value: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "Break":
            return f"{indent}{prefix}Break Statement"
        elif cname == "Continue":
            return f"{indent}{prefix}Continue Statement"
        elif cname == "TryExcept":
            result = [f"{indent}{prefix}Try-Except Block"]
            result.append(f"{indent}    ├── Try Block:")
            for i, stmt in enumerate(node.try_block):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.try_block) - 1))
            result.append(f"{indent}    └── Except Block:")
            for i, stmt in enumerate(node.except_block):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.except_block) - 1))
            return "\n".join(result)
        elif cname == "StringMethod":
            result = [f"{indent}{prefix}String Method: {node.method}"]
            result.append(f"{indent}    ├── String: {pretty_print_ast(node.string_obj, indent + '    ', False)}")
            if hasattr(node, 'args') and node.args:
                result.append(f"{indent}    └── Arguments:")
                for i, arg in enumerate(node.args):
                    result.append(pretty_print_ast(arg, indent + '        ', i == len(node.args) - 1))
            return "\n".join(result)
        elif cname == "LenFunction":
            return f"{indent}{prefix}Length Function\n{indent}    └── Expression: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "RangeCall":
            result = [f"{indent}{prefix}Range Function"]
            if node.start:
                result.append(f"{indent}    ├── Start: {pretty_print_ast(node.start, indent + '    ', False)}")
            if node.stop:
                result.append(f"{indent}    ├── Stop: {pretty_print_ast(node.stop, indent + '    ', False)}")
            if node.step:
                result.append(f"{indent}    └── Step: {pretty_print_ast(node.step, indent + '    ', True)}")
            return "\n".join(result)
        else:
            return f"{indent}{prefix}Unknown Node: {cname}"
    else:
        return f"{indent}{prefix}Unknown: {str(node)}"

# Now patch the functions after they're defined
old_pretty_print_ast = pretty_print_ast
def pretty_print_ast(node, indent="", is_last=True):
    node = ensure_list(node)
    if isinstance(node, list) and len(node) == 1:
        return old_pretty_print_ast(node[0], indent, is_last)
    elif isinstance(node, list):
        result = []
        for i, n in enumerate(node):
            result.append(old_pretty_print_ast(n, indent, i == len(node) - 1))
        return "\n".join(result)
    else:
        return old_pretty_print_ast(node, indent, is_last)

# Define the original semantic_analysis function
def semantic_analysis(ast):
    symbol_table = {}
    errors = []
    type_info = {}
    
    def get_type(value):
        if isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, list):
            return "list"
        elif value is None:
            return "None"
        return str(type(value).__name__)

    def visit(node):
        if isinstance(node, list):
            for n in node:
                visit(n)
            return None
        elif hasattr(node, "__class__"):
            cname = node.__class__.__name__
            
            if cname == "Assign":
                value = visit(node.expr)
                var_name = node.name.name if hasattr(node.name, 'name') else node.name
                type_info[var_name] = get_type(value)
                symbol_table[var_name] = value
                return value
                
            elif cname == "Identifier":
                var_name = node.name
                if var_name not in symbol_table:
                    errors.append(f"❌ Undeclared variable: '{var_name}'")
                    return None
                return symbol_table[var_name]
                
            elif cname == "BinaryOp":
                left = visit(node.left)
                right = visit(node.right)
                left_type = get_type(left)
                right_type = get_type(right)
                
                if left is not None and right is not None:
                    if node.op in ['+', '-', '*', '/', '%']:
                        if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                            errors.append(f"❌ Type mismatch in arithmetic operation '{node.op}': {left_type} and {right_type}")
                    elif node.op in ['<', '>', '<=', '>=', '==', '!=']:
                        if left_type != right_type:
                            errors.append(f"❌ Type mismatch in comparison '{node.op}': {left_type} and {right_type}")
                    elif node.op in ['and', 'or']:
                        if left_type != 'bool' or right_type != 'bool':
                            errors.append(f"❌ Type mismatch in logical operation '{node.op}': {left_type} and {right_type}")
                return None
                
            elif cname == "Number":
                return node.value
                
            elif cname == "String":
                return node.value
                
            elif cname == "Boolean":
                return node.value
                
            elif cname == "Print":
                expr = visit(node.expr)
                if expr is not None:
                    type_info['print_expr'] = get_type(expr)
                return None
                
            elif cname == "IfElse":
                cond = visit(node.condition)
                if cond is not None and get_type(cond) != 'bool':
                    errors.append(f"❌ Condition must be a boolean, got {get_type(cond)}")
                visit(node.if_body)
                if node.else_body:
                    visit(node.else_body)
                return None
                
            elif cname == "WhileLoop":
                cond = visit(node.condition)
                if cond is not None and get_type(cond) != 'bool':
                    errors.append(f"❌ While loop condition must be a boolean, got {get_type(cond)}")
                visit(node.body)
                return None
                
            elif cname == "ForLoop":
                var_name = node.var.name if hasattr(node.var, 'name') else node.var
                iterable = visit(node.iterable)
                if iterable is not None:
                    iter_type = get_type(iterable)
                    if iter_type not in ['list', 'range']:
                        errors.append(f"❌ For loop iterable must be a list or range, got {iter_type}")
                old_symbol_table = symbol_table.copy()
                symbol_table[var_name] = None
                visit(node.body)
                symbol_table.clear()
                symbol_table.update(old_symbol_table)
                return None
                
            elif cname == "FunctionDef":
                func_name = node.name
                symbol_table[func_name] = "function"
                type_info[func_name] = "function"
                old_symbol_table = symbol_table.copy()
                for param in node.params:
                    symbol_table[param] = None
                    type_info[param] = "parameter"
                visit(node.body)
                symbol_table.clear()
                symbol_table.update(old_symbol_table)
                return None
                
            elif cname == "FunctionCall":
                func_name = node.name.name if hasattr(node.name, 'name') else node.name
                if func_name not in symbol_table:
                    errors.append(f"❌ Undeclared function: '{func_name}'")
                for arg in node.args:
                    visit(arg)
                return None
                
            elif cname == "ListNode":
                elements = [visit(elem) for elem in node.elements]
                return elements
                
            elif cname == "IndexNode":
                lst = visit(node.expr)
                idx = visit(node.index)
                if lst is not None and get_type(lst) != 'list':
                    errors.append(f"❌ Indexing requires a list, got {get_type(lst)}")
                if idx is not None and get_type(idx) != 'int':
                    errors.append(f"❌ List index must be an integer, got {get_type(idx)}")
                return None
                
            elif cname == "StringMethod":
                string_obj = visit(node.string_obj)
                if string_obj is not None and get_type(string_obj) != 'str':
                    errors.append(f"❌ String method '{node.method}' called on non-string type: {get_type(string_obj)}")
                for arg in getattr(node, 'args', []) or []:
                    visit(arg)
                return None
                
            elif cname == "RangeCall":
                args = [node.start, node.stop, node.step]
                for i, arg in enumerate(args):
                    val = visit(arg) if arg is not None else None
                    if val is not None and get_type(val) != 'int':
                        errors.append(f"❌ Range argument {i+1} must be an integer, got {get_type(val)}")
                return None
                
            elif cname == "Return":
                value = visit(node.expr)
                if value is not None:
                    type_info['return_value'] = get_type(value)
                return None
                
            elif cname == "TryExcept":
                visit(node.try_body)
                visit(node.except_body)
                return None
                
            elif cname == "LenFunction":
                expr = visit(node.expr)
                if expr is not None:
                    expr_type = get_type(expr)
                    if expr_type not in ['list', 'str']:
                        errors.append(f"❌ len() requires a list or string, got {expr_type}")
                return None
                
            elif cname == "UnaryOp":
                expr = visit(node.expr)
                if expr is not None:
                    expr_type = get_type(expr)
                    if node.op == '-' and expr_type not in ['int', 'float']:
                        errors.append(f"❌ Unary minus requires a number, got {expr_type}")
                    elif node.op == 'not' and expr_type != 'bool':
                        errors.append(f"❌ Logical not requires a boolean, got {expr_type}")
                return None
                
            return None
        return None

    visit(ast)
    
    # Format the output
    output = []
    if errors:
        output.append("❌ Semantic Errors Found:")
        for error in errors:
            output.append(f"  {error}")
    else:
        output.append("✅ No semantic errors found!")
        
    output.append("\nType Information:")
    output.append("----------------")
    for var, type_name in type_info.items():
        output.append(f"  {var}: {type_name}")
        
    output.append("\nSymbol Table:")
    output.append("-------------")
    for var, value in symbol_table.items():
        if value == "function":
            output.append(f"  {var}: function")
        else:
            output.append(f"  {var}: {get_type(value)}")
            
    return len(errors) == 0, "\n".join(output)

# Define the original generate_icg function
def generate_icg(ast):
    code_lines = []
    temp_counter = [0]
    label_counter = [0]
    
    def new_temp():
        temp_counter[0] += 1
        return f"t{temp_counter[0]}"
        
    def new_label():
        label_counter[0] += 1
        return f"L{label_counter[0]}"
        
    def visit(node):
        if isinstance(node, list):
            for n in node:
                visit(n)
            return None
        elif hasattr(node, "__class__"):
            cname = node.__class__.__name__
            
            if cname == "Assign":
                rhs = visit(node.expr)
                code_lines.append(f"{node.name} = {rhs}")
                return node.name
                
            elif cname == "Number":
                temp = new_temp()
                code_lines.append(f"{temp} = {node.value}")
                return temp
                
            elif cname == "String":
                temp = new_temp()
                code_lines.append(f"{temp} = '{node.value}'")
                return temp
                
            elif cname == "Boolean":
                temp = new_temp()
                code_lines.append(f"{temp} = {node.value}")
                return temp
                
            elif cname == "Identifier":
                temp = new_temp()
                code_lines.append(f"{temp} = {node.name}")
                return temp
                
            elif cname == "BinaryOp":
                left = visit(node.left)
                right = visit(node.right)
                temp = new_temp()
                code_lines.append(f"{temp} = {left} {node.op} {right}")
                return temp
                
            elif cname == "UnaryOp":
                expr = visit(node.expr)
                temp = new_temp()
                code_lines.append(f"{temp} = {node.op} {expr}")
                return temp
                
            elif cname == "Print":
                val = visit(node.expr)
                code_lines.append(f"print {val}")
                return None
                
            elif cname == "IfElse":
                cond = visit(node.condition)
                else_label = new_label()
                end_label = new_label()
                
                code_lines.append(f"if {cond} == False goto {else_label}")
                for stmt in node.if_body:
                    visit(stmt)
                code_lines.append(f"goto {end_label}")
                code_lines.append(f"{else_label}:")
                if node.else_body:
                    for stmt in node.else_body:
                        visit(stmt)
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "WhileLoop":
                start_label = new_label()
                end_label = new_label()
                
                code_lines.append(f"{start_label}:")
                cond = visit(node.condition)
                code_lines.append(f"if {cond} == False goto {end_label}")
                for stmt in node.body:
                    visit(stmt)
                code_lines.append(f"goto {start_label}")
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "ForLoop":
                start_label = new_label()
                end_label = new_label()
                iter_var = new_temp()
                
                # Initialize iterator
                iter_expr = visit(node.iterable)
                code_lines.append(f"{iter_var} = {iter_expr}")
                
                code_lines.append(f"{start_label}:")
                # Check if iteration is complete
                code_lines.append(f"if {iter_var} == None goto {end_label}")
                
                # Assign current value to loop variable
                code_lines.append(f"{node.var} = {iter_var}")
                
                # Execute loop body
                for stmt in node.body:
                    visit(stmt)
                    
                # Move to next iteration
                code_lines.append(f"goto {start_label}")
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "FunctionDef":
                code_lines.append(f"function {node.name}:")
                for param in node.params:
                    code_lines.append(f"param {param}")
                for stmt in node.body:
                    visit(stmt)
                return None
                
            elif cname == "FunctionCall":
                args = [visit(arg) for arg in node.args]
                # Convert None to 'None' string to avoid join error
                safe_args = [str(a) if a is not None else "None" for a in args]
                temp = new_temp()
                code_lines.append(f"{temp} = call {node.name}({', '.join(safe_args)})")
                return temp
                
            elif cname == "ListNode":
                temp = new_temp()
                code_lines.append(f"{temp} = []")
                for elem in node.elements:
                    elem_temp = visit(elem)
                    code_lines.append(f"{temp}.append({elem_temp})")
                return temp
                
            elif cname == "IndexNode":
                lst = visit(node.expr)
                idx = visit(node.index)
                temp = new_temp()
                code_lines.append(f"{temp} = {lst}[{idx}]")
                return temp
                
            elif cname == "ListAssign":
                lst = visit(node.expr)
                idx = visit(node.index)
                val = visit(node.value)
                code_lines.append(f"{lst}[{idx}] = {val}")
                return None
                
            elif cname == "Return":
                val = visit(node.expr)
                code_lines.append(f"return {val}")
                return None
                
            elif cname == "Break":
                code_lines.append("break")
                return None
                
            elif cname == "Continue":
                code_lines.append("continue")
                return None
                
            elif cname == "TryExcept":
                try_label = new_label()
                except_label = new_label()
                end_label = new_label()
                
                code_lines.append(f"{try_label}:")
                for stmt in node.try_block:
                    visit(stmt)
                code_lines.append(f"goto {end_label}")
                
                code_lines.append(f"{except_label}:")
                for stmt in node.except_block:
                    visit(stmt)
                    
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "StringMethod":
                string_obj = visit(node.string_obj)
                temp = new_temp()
                if node.method == "upper":
                    code_lines.append(f"{temp} = {string_obj}.upper()")
                elif node.method == "lower":
                    code_lines.append(f"{temp} = {string_obj}.lower()")
                elif node.method == "strip":
                    code_lines.append(f"{temp} = {string_obj}.strip()")
                elif node.method == "replace":
                    args = [visit(arg) for arg in node.args]
                    code_lines.append(f"{temp} = {string_obj}.replace({args[0]}, {args[1]})")
                return temp
                
            elif cname == "LenFunction":
                expr = visit(node.expr)
                temp = new_temp()
                code_lines.append(f"{temp} = len({expr})")
                return temp
                
            elif cname == "RangeCall":
                start = visit(node.start) if node.start else "0"
                stop = visit(node.stop) if node.stop else "None"
                step = visit(node.step) if node.step else "1"
                temp = new_temp()
                code_lines.append(f"{temp} = range({start}, {stop}, {step})")
                return temp
                
            return None
        return None

    visit(ast)
    
    # Format the output
    output = []
    output.append("Intermediate Code (Three-Address Code):")
    output.append("=====================================")
    output.append("")
    
    for i, line in enumerate(code_lines, 1):
        output.append(f"{i:3d} | {line}")
        
    output.append("\nLegend:")
    output.append("-------")
    output.append("tN    : Temporary variable")
    output.append("LN    : Label")
    output.append("goto  : Jump instruction")
    output.append("call  : Function call")
    output.append("param : Function parameter")
    
    return "\n".join(output)

# Now patch semantic_analysis and generate_icg
old_semantic_analysis = semantic_analysis
def semantic_analysis(ast):
    ast = ensure_list(ast)
    return old_semantic_analysis(ast)

old_generate_icg = generate_icg
def generate_icg(ast):
    ast = ensure_list(ast)
    return old_generate_icg(ast)

def update_phase_output(phase_name, content):
    text_widget = phase_sections[phase_name]["text"]
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", content)
    text_widget.config(state=tk.DISABLED)

def optimize_code_icg(icg_code):
    if not icg_code or icg_code == "<no intermediate code generated>":
        return "⚠️ No intermediate code to optimize."
        
    lines = icg_code.split('\n')
    optimized_lines = []
    optimizations = []
    
    # Skip header and legend
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('Legend:'):
            start_idx = i
            break
            
    # Process each line
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('Legend:'):
            break
            
        # Extract the actual code part (after line number)
        code = line.split('|', 1)[1].strip() if '|' in line else line
        
        # Constant Folding
        if '=' in code and any(op in code for op in ['+', '-', '*', '/']):
            try:
                # Try to evaluate constant expressions
                left, right = code.split('=', 1)
                left = left.strip()
                right = right.strip()
                
                # Check if right side is a constant expression
                if all(c.isdigit() or c in '+-*/() ' for c in right):
                    result = eval(right)
                    optimized_lines.append(f"{left} = {result}")
                    optimizations.append(f"Constant folding: {right} → {result}")
                    i += 1
                    continue
            except:
                pass
                
        # Copy Propagation
        if '=' in code and not any(op in code for op in ['+', '-', '*', '/']):
            left, right = code.split('=', 1)
            left = left.strip()
            right = right.strip()
            
            # Check if right side is just a variable
            if right.isidentifier():
                # Look ahead for uses of left
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].split('|', 1)[1].strip() if '|' in lines[j] else lines[j]
                    if left in next_line and '=' not in next_line:
                        optimized_lines.append(f"# {code}  # Copy propagated")
                        optimizations.append(f"Copy propagation: {left} → {right}")
                        i += 1
                        break
                else:
                    optimized_lines.append(code)
                    i += 1
                    continue
                    
        # Common Subexpression Elimination
        if i > 0 and i < len(lines) - 1:
            prev_code = lines[i-1].split('|', 1)[1].strip() if '|' in lines[i-1] else lines[i-1]
            next_code = lines[i+1].split('|', 1)[1].strip() if '|' in lines[i+1] else lines[i+1]
            
            if '=' in code and '=' in prev_code and '=' in next_code:
                prev_left, prev_right = prev_code.split('=', 1)
                curr_left, curr_right = code.split('=', 1)
                next_left, next_right = next_code.split('=', 1)
                
                if prev_right.strip() == curr_right.strip():
                    optimized_lines.append(f"# {code}  # Common subexpression eliminated")
                    optimizations.append(f"Common subexpression elimination: {curr_right} → {prev_left}")
                    i += 1
                    continue
                    
        # Loop Optimization
        if 'goto' in code and 'L' in code:
            # Check if this is a loop
            if i > 0 and 'if' in lines[i-1]:
                # Try to move loop-invariant code outside
                loop_start = i
                while i < len(lines) and 'goto' not in lines[i]:
                    i += 1
                loop_end = i
                
                # Check for loop-invariant code
                for j in range(loop_start, loop_end):
                    loop_line = lines[j].split('|', 1)[1].strip() if '|' in lines[j] else lines[j]
                    if '=' in loop_line and not any(var in loop_line for var in ['i', 'j', 'k']):
                        optimized_lines.append(f"# {loop_line}  # Moved outside loop")
                        optimizations.append(f"Loop optimization: Moved invariant code outside loop")
                        continue
                    optimized_lines.append(loop_line)
                i += 1
                continue
                
        # Dead Code Elimination
        if '=' in code:
            left = code.split('=', 1)[0].strip()
            # Check if variable is used later
            used = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].split('|', 1)[1].strip() if '|' in lines[j] else lines[j]
                if left in next_line and '=' not in next_line:
                    used = True
                    break
            if not used:
                optimized_lines.append(f"# {code}  # Dead code eliminated")
                optimizations.append(f"Dead code elimination: {left} is never used")
                i += 1
                continue
                
        optimized_lines.append(code)
        i += 1
        
    # Format the output
    output = []
    output.append("Code Optimization Analysis:")
    output.append("==========================")
    output.append("")
    
    if optimizations:
        output.append("Applied Optimizations:")
        output.append("---------------------")
        for opt in optimizations:
            output.append(f"✓ {opt}")
        output.append("")
        
    output.append("Optimized Code:")
    output.append("--------------")
    for i, line in enumerate(optimized_lines, 1):
        output.append(f"{i:3d} | {line}")
        
    output.append("\nOptimization Summary:")
    output.append("-------------------")
    output.append(f"• Total optimizations applied: {len(optimizations)}")
    output.append("• Types of optimizations:")
    output.append("  - Constant folding")
    output.append("  - Copy propagation")
    output.append("  - Common subexpression elimination")
    output.append("  - Loop optimization")
    output.append("  - Dead code elimination")
    
    return "\n".join(output)

def generate_code(optimized_code):
    if not optimized_code or "No intermediate code" in optimized_code:
        return "⚠️ No code to generate."
        
    lines = optimized_code.split('\n')
    generated_code = []
    reg_counter = [0]
    label_counter = [0]
    
    def new_reg():
        reg_counter[0] += 1
        return f"R{reg_counter[0]}"
        
    def new_label():
        label_counter[0] += 1
        return f"L{label_counter[0]}"
        
    # Skip header and summary
    start_idx = 0
    for i, line in enumerate(lines):
        if "Optimized Code:" in line:
            start_idx = i + 2
            break
            
    # Process each line
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if not line or "Optimization Summary" in line:
            break
            
        # Extract the actual code part (after line number)
        code = line.split('|', 1)[1].strip() if '|' in line else line
        
        # Skip commented lines
        if code.startswith('#'):
            i += 1
            continue
            
        # Assignment
        if '=' in code:
            left, right = code.split('=', 1)
            left = left.strip()
            right = right.strip()
            
            # Constant assignment
            if right.isdigit():
                reg = new_reg()
                generated_code.append(f"MOV {reg}, #{right}    ; Load constant {right}")
                generated_code.append(f"STR {reg}, [{left}]   ; Store in {left}")
                
            # Variable assignment
            elif right.isidentifier():
                reg1 = new_reg()
                reg2 = new_reg()
                generated_code.append(f"LDR {reg1}, [{right}]  ; Load {right}")
                generated_code.append(f"STR {reg1}, [{left}]   ; Store in {left}")
                
            # Arithmetic operation
            elif any(op in right for op in ['+', '-', '*', '/']):
                op = next(op for op in ['+', '-', '*', '/'] if op in right)
                left_op, right_op = right.split(op)
                left_op = left_op.strip()
                right_op = right_op.strip()
                
                reg1 = new_reg()
                reg2 = new_reg()
                reg3 = new_reg()
                
                # Load operands
                if left_op.isdigit():
                    generated_code.append(f"MOV {reg1}, #{left_op}  ; Load constant {left_op}")
                else:
                    generated_code.append(f"LDR {reg1}, [{left_op}] ; Load {left_op}")
                    
                if right_op.isdigit():
                    generated_code.append(f"MOV {reg2}, #{right_op}  ; Load constant {right_op}")
                else:
                    generated_code.append(f"LDR {reg2}, [{right_op}] ; Load {right_op}")
                    
                # Perform operation
                if op == '+':
                    generated_code.append(f"ADD {reg3}, {reg1}, {reg2}  ; Add operands")
                elif op == '-':
                    generated_code.append(f"SUB {reg3}, {reg1}, {reg2}  ; Subtract operands")
                elif op == '*':
                    generated_code.append(f"MUL {reg3}, {reg1}, {reg2}  ; Multiply operands")
                elif op == '/':
                    generated_code.append(f"DIV {reg3}, {reg1}, {reg2}  ; Divide operands")
                    
                generated_code.append(f"STR {reg3}, [{left}]   ; Store result in {left}")
                
        # Print statement
        elif code.startswith('print'):
            reg = new_reg()
            var = code.split('print', 1)[1].strip()
            generated_code.append(f"LDR {reg}, [{var}]  ; Load value to print")
            generated_code.append(f"PUSH {reg}         ; Push to stack for printing")
            generated_code.append(f"CALL print         ; Call print function")
            generated_code.append(f"POP {reg}          ; Clean up stack")
            
        # If statement
        elif code.startswith('if'):
            cond = code.split('goto', 1)[0].split('if', 1)[1].strip()
            label = code.split('goto', 1)[1].strip()
            
            if '==' in cond:
                left, right = cond.split('==')
                reg1 = new_reg()
                reg2 = new_reg()
                generated_code.append(f"LDR {reg1}, [{left.strip()}]  ; Load left operand")
                if right.strip().isdigit():
                    generated_code.append(f"MOV {reg2}, #{right.strip()}  ; Load constant")
                else:
                    generated_code.append(f"LDR {reg2}, [{right.strip()}]  ; Load right operand")
                generated_code.append(f"CMP {reg1}, {reg2}  ; Compare operands")
                generated_code.append(f"BNE {label}      ; Branch if not equal")
                
        # Goto statement
        elif code.startswith('goto'):
            label = code.split('goto', 1)[1].strip()
            generated_code.append(f"B {label}          ; Unconditional branch")
            
        # Label
        elif code.endswith(':'):
            generated_code.append(f"{code}             ; Label")
            
        # Function call
        elif code.startswith('call'):
            func = code.split('call', 1)[1].split('(')[0].strip()
            args = code.split('(')[1].rstrip(')').split(',')
            for arg in args:
                reg = new_reg()
                generated_code.append(f"LDR {reg}, [{arg.strip()}]  ; Load argument")
                generated_code.append(f"PUSH {reg}         ; Push argument to stack")
            generated_code.append(f"CALL {func}         ; Call function")
            for _ in args:
                generated_code.append(f"POP {new_reg()}     ; Clean up stack")
                
        # Return statement
        elif code.startswith('return'):
            val = code.split('return', 1)[1].strip()
            reg = new_reg()
            generated_code.append(f"LDR {reg}, [{val}]  ; Load return value")
            generated_code.append(f"MOV R0, {reg}      ; Set return register")
            generated_code.append(f"RET                ; Return from function")
            
        i += 1
        
    # Format the output
    output = []
    output.append("Code Generation (Assembly-like):")
    output.append("===============================")
    output.append("")
    
    if generated_code:
        output.append("Generated Code:")
        output.append("--------------")
        for i, line in enumerate(generated_code, 1):
            output.append(f"{i:3d} | {line}")
            
        output.append("\nRegister Usage:")
        output.append("--------------")
        output.append(f"• Total registers used: {reg_counter[0]}")
        output.append("• Register naming: R1, R2, R3, ...")
        
        output.append("\nLabel Usage:")
        output.append("-----------")
        output.append(f"• Total labels used: {label_counter[0]}")
        output.append("• Label naming: L1, L2, L3, ...")
        
        output.append("\nInstruction Types:")
        output.append("-----------------")
        output.append("• MOV: Move immediate value to register")
        output.append("• LDR: Load from memory to register")
        output.append("• STR: Store from register to memory")
        output.append("• ADD/SUB/MUL/DIV: Arithmetic operations")
        output.append("• CMP: Compare operands")
        output.append("• B/BNE: Branch instructions")
        output.append("• PUSH/POP: Stack operations")
        output.append("• CALL/RET: Function calls")
    else:
        output.append("No code generated.")
        
    return "\n".join(output)

def analyze_phases():
    code = code_input.get("1.0", tk.END).strip()
    if not code:
        update_phase_output("Lexical Analysis", "⚠️ Please enter some code to analyze.")
        update_phase_output("Syntax & AST Analysis", "")
        update_phase_output("Semantic Analysis", "")
        update_phase_output("Intermediate Code Generation", "")
        update_phase_output("Code Optimization", "")
        update_phase_output("Code Generation", "")
        return

    try:
        # Lexical Analysis
        tokens = tokenize(code)
        if tokens:
            update_phase_output("Lexical Analysis", format_token_output(tokens))
        else:
            update_phase_output("Lexical Analysis", "No tokens found in the input code.")

        # Syntax & AST Analysis (use Python's built-in compile for robust syntax/indentation check)
        syntax_result = ""
        ast = None
        try:
            compile(code, "<string>", "exec")
            syntax_result = "✅ Syntax and indentation are correct!"
        except Exception as e:
            syntax_result = f"❌ Syntax/Indentation Error:\n==========================\n{e}"

        # Always try to parse AST, even if compile() fails
        try:
            ast = parser.parse(code)
            ast = ensure_list(ast)
            if not ast:
                raise Exception("No AST generated (possible syntax error).")
            ast_str = pretty_print_ast(ast)
            syntax_result += ("\n\nAbstract Syntax Tree (AST):\n" +
                             "===========================\n" +
                             ast_str + "\n\n" +
                             "The AST shows the hierarchical structure of your code, where:\n" +
                             "├── Each node represents a programming construct\n" +
                             "├── Child nodes show the components of each construct\n" +
                             "└── The tree structure helps verify correct syntax")
        except Exception as ast_e:
            syntax_result += f"\n\n❌ AST generation failed:\n========================\n{ast_e}"
            ast = None

        update_phase_output("Syntax & AST Analysis", syntax_result)

        # If AST generation failed, skip further phases
        if ast is None or not ast:
            update_phase_output("Semantic Analysis", "")
            update_phase_output("Intermediate Code Generation", "")
            update_phase_output("Code Optimization", "")
            update_phase_output("Code Generation", "")
            return

        # Semantic Analysis
        try:
            sem_ok, sem_msg = semantic_analysis(ast)
            if not sem_ok:
                update_phase_output("Semantic Analysis", 
                    "❌ Semantic Errors Found:\n" +
                    "======================\n" +
                    sem_msg + "\n\n" +
                    "💡 Tips to fix semantic errors:\n" +
                    "1. Check variable declarations and types\n" +
                    "2. Verify function definitions and calls\n" +
                    "3. Ensure proper type compatibility\n" +
                    "4. Look for undefined variables or functions")
            else:
                update_phase_output("Semantic Analysis", sem_msg)
            if not sem_ok:
                update_phase_output("Intermediate Code Generation", "❌ ICG skipped due to semantic error.")
                update_phase_output("Code Optimization", "❌ Optimization skipped due to semantic error.")
                update_phase_output("Code Generation", "❌ Code Generation skipped due to semantic error.")
                return
        except Exception as e:
            update_phase_output("Semantic Analysis", 
                "❌ Error in Semantic Analysis:\n" +
                "==========================\n" +
                str(e) + "\n\n" +
                "Please check your code for:\n" +
                "1. Proper variable declarations\n" +
                "2. Correct function definitions\n" +
                "3. Valid type usage")
            update_phase_output("Intermediate Code Generation", "❌ ICG skipped due to semantic error.")
            update_phase_output("Code Optimization", "❌ Optimization skipped due to semantic error.")
            update_phase_output("Code Generation", "❌ Code Generation skipped due to semantic error.")
            return

        # Intermediate Code Generation
        try:
            icg_code = generate_icg(ast)
            update_phase_output("Intermediate Code Generation", 
                "✅ Intermediate Code Generated:\n" +
                "===========================\n" +
                icg_code)
        except Exception as e:
            update_phase_output("Intermediate Code Generation", 
                "❌ Error in Intermediate Code Generation:\n" +
                "===================================\n" +
                str(e) + "\n\n" +
                "This error occurred while converting your code to intermediate representation.")
            update_phase_output("Code Optimization", "❌ Optimization skipped due to ICG error.")
            update_phase_output("Code Generation", "❌ Code Generation skipped due to ICG error.")
            return

        # Code Optimization
        try:
            optimized_code = optimize_code_icg(icg_code)
            update_phase_output("Code Optimization", 
                "✅ Code Optimization Results:\n" +
                "=========================\n" +
                optimized_code)
        except Exception as e:
            update_phase_output("Code Optimization", 
                "❌ Error in Code Optimization:\n" +
                "=========================\n" +
                str(e) + "\n\n" +
                "This error occurred while optimizing your code.")
            update_phase_output("Code Generation", "❌ Code Generation skipped due to optimization error.")
            return

        # Code Generation
        try:
            codegen = generate_code(optimized_code)
            update_phase_output("Code Generation", 
                "✅ Final Generated Code:\n" +
                "=====================\n" +
                codegen)
        except Exception as e:
            update_phase_output("Code Generation", 
                "❌ Error in Code Generation:\n" +
                "========================\n" +
                str(e) + "\n\n" +
                "This error occurred while generating the final code.")

    except Exception as e:
        update_phase_output("Lexical Analysis", 
            "❌ Error during analysis:\n" +
            "======================\n" +
            str(e) + "\n\n" +
            "Please check your input code for any obvious errors.")
        update_phase_output("Syntax & AST Analysis", "")
        update_phase_output("Semantic Analysis", "")
        update_phase_output("Intermediate Code Generation", "")
        update_phase_output("Code Optimization", "")
        update_phase_output("Code Generation", "")

# ---------- Styling ----------

root = tk.Tk()
root.title("🔥 Mini Compiler - Python Interpreter 🔥")
root.geometry("1200x700")
root.config(bg="#f2f2f2")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Segoe UI", 12, "bold"),
                padding=10,
                relief="flat",
                background="#4CAF50",
                foreground="white")
style.map("TButton", background=[("active", "#45a049")])

default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Segoe UI", size=12)

# ---------- Welcome Screen (Restored) ----------
welcome_screen = tk.Frame(root, bg="#1E1E2F")
welcome_screen.pack(fill=tk.BOTH, expand=True)

# Header
header_label = tk.Label(
    welcome_screen,
    text="🔥 Mini Compiler - Python Interpreter 🔥",
    font=("Segoe UI", 28, "bold"),
    bg="#1E1E2F",
    fg="#FFD700"
)
header_label.pack(pady=(30, 10))

# Subheader
subheader_label = tk.Label(
    welcome_screen,
    text="Learn, test and optimize Python code interactively.",
    font=("Segoe UI", 16),
    bg="#1E1E2F",
    fg="#DDDDDD"
)
subheader_label.pack(pady=(0, 20))

# Project Team
team_label = tk.Label(
    welcome_screen,
    text="Project Team:\nMayank Singh, Piyush Kumar, Kartik Kapri, Kumkum Pandey",
    font=("Segoe UI", 12, "italic"),
    bg="#1E1E2F",
    fg="#BBBBBB"
)
team_label.pack(pady=(0, 30))

# Navigation Buttons
nav_buttons = tk.Frame(welcome_screen, bg="#1E1E2F")
nav_buttons.pack(pady=10)

for i, (text, cmd) in enumerate([
    ("🧪 Test Your Skills", go_to_testing),
    ("🚀 Optimize Code", go_to_optimizer),
    ("🔍 Compiler Phases", go_to_compiler_phases),
]):
    btn = tk.Button(
        nav_buttons, text=text, font=("Segoe UI", 13, "bold"),
        bg="#1976D2", fg="white", activebackground="#1565C0", cursor="hand2",
        padx=20, pady=10, relief="flat", command=cmd
    )
    btn.grid(row=0, column=i, padx=15)

# ---------- Learn Python Screen ----------

learn_screen = tk.Frame(root, bg="#E3F2FD")

tk.Label(learn_screen, text="📘 Learn Python", font=("Segoe UI", 22, "bold"),
         bg="#E3F2FD", fg="#0D47A1").pack(pady=20)

scroll_frame = tk.Frame(learn_screen)
scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(scroll_frame, bg="#ffffff", highlightthickness=0)
scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
scrollable_content = tk.Frame(canvas, bg="#ffffff")

canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
scrollable_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
canvas.bind_all("<MouseWheel>", on_mousewheel)

sections = {
    "🔤 Variables & Data Types": "Python supports various data types like int, float, string, and boolean.",
    "🔁 Loops": "Use 'for' or 'while' loops to iterate over sequences or repeat actions.",
    "📦 Functions": "Functions help you reuse code. Define using 'def'.",
    "📄 File Handling": "Python can open, read, and write files using the 'open' function.",
    "🧪 Exception Handling": "Use try-except blocks to manage errors gracefully."
}

for title, desc in sections.items():
    container = tk.Frame(scrollable_content, bg="#E3F2FD", bd=1, relief="solid")
    title_label = tk.Label(container, text=title, font=("Segoe UI", 14, "bold"),
                           bg="#C5CAE9", fg="#1A237E", cursor="hand2", anchor="w", padx=10)
    title_label.pack(fill="x")

    content = tk.Label(container, text=desc, font=("Segoe UI", 12),
                       wraplength=1000, justify="left", bg="#E8EAF6", anchor="w", padx=10)
    content.pack_forget()

    title_label.bind("<Button-1>", lambda e, frame=content: toggle_section(frame))
    container.pack(fill="x", padx=20, pady=10)

ttk.Button(learn_screen, text="🔙 Back", command=back_to_welcome).pack(pady=10)

# ---------- Testing Screen (Interpreter) ----------
testing_screen = tk.Frame(root, bg="#23272F")

# Code editor label
tk.Label(testing_screen, text="Python Code Editor", font=("Segoe UI", 16, "bold"), bg="#23272F", fg="#FFD700").pack(pady=(20, 5))

# Code editor and output side by side
editor_output_pane = tk.PanedWindow(testing_screen, orient=tk.HORIZONTAL, sashwidth=5, bg="#23272F")
editor_output_pane.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

# Code editor
editor_frame = tk.Frame(editor_output_pane, bg="#181A20")
editor_output_pane.add(editor_frame, stretch="always")
input_text = tk.Text(editor_frame, height=20, font=("Fira Mono", 13), wrap="none", bg="#23272F", fg="#ECECEC", insertbackground="#FFD700", undo=True)
input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Output console
output_frame = tk.Frame(editor_output_pane, bg="#181A20")
editor_output_pane.add(output_frame, stretch="always")
tk.Label(output_frame, text="Output Console", font=("Segoe UI", 14, "bold"), bg="#181A20", fg="#00BFAE").pack(fill="x", padx=10, pady=(10, 0))
output_box = tk.Text(output_frame, height=20, font=("Fira Mono", 13), wrap="none", state=tk.DISABLED, bg="#263238", fg="#ECEFF1", insertbackground="#FFD700")
output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Run and Back buttons
button_frame = tk.Frame(testing_screen, bg="#23272F")
button_frame.pack(pady=10)
tk.Button(button_frame, text="▶ Run Code", font=("Segoe UI", 12, "bold"), bg="#1976D2", fg="white", activebackground="#1565C0", command=execute_code, cursor="hand2", padx=20, pady=10, relief="flat").grid(row=0, column=0, padx=10)
tk.Button(button_frame, text="🔙 Back", font=("Segoe UI", 12, "bold"), bg="#1976D2", fg="white", activebackground="#1565C0", command=back_to_welcome, cursor="hand2", padx=20, pady=10, relief="flat").grid(row=0, column=1, padx=10)

# ---------- Optimizer Screen ----------

optimizer_screen = tk.Frame(root, bg="#f3e5f5")

tk.Label(optimizer_screen, text="🚀 Python Code Optimizer ",
         font=("Segoe UI", 22, "bold"), bg="#f3e5f5", fg="#4A148C").pack(pady=20)

# Create a PanedWindow for side-by-side layout
optimizer_pane = tk.PanedWindow(optimizer_screen, orient=tk.HORIZONTAL, bg="#f3e5f5")
optimizer_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left panel for input code
left_frame = tk.Frame(optimizer_pane, bg="#f3e5f5")
optimizer_pane.add(left_frame, stretch="always")

tk.Label(left_frame, text="📝 Enter Code:", font=("Segoe UI", 13, "bold"),
         bg="#f3e5f5", fg="#6A1B9A").pack(anchor="w")

optimizer_input = tk.Text(left_frame, height=20, font=("Consolas", 12), wrap="word",
                          bg="#fff", fg="#000", insertbackground="black")
optimizer_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Right panel for optimized code
right_frame = tk.Frame(optimizer_pane, bg="#f3e5f5")
optimizer_pane.add(right_frame, stretch="always")

tk.Label(right_frame, text="✅ Optimized Code:", font=("Segoe UI", 13, "bold"),
         bg="#f3e5f5", fg="#4A148C").pack(anchor="w")

optimizer_output = tk.Text(right_frame, height=20, font=("Consolas", 12), wrap="word",
                           state=tk.DISABLED, bg="#e1bee7", fg="#1A1A1A", insertbackground="black")
optimizer_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Button frame at the bottom
button_frame = tk.Frame(optimizer_screen, bg="#f3e5f5")
button_frame.pack(pady=10)

ttk.Button(button_frame, text="🚀 Optimize Code", command=optimize_code).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="🔙 Back", command=back_to_welcome).grid(row=0, column=1, padx=10)

# ---------- Compiler Phases Screen ----------

compiler_phases_screen = tk.Frame(root, bg="#1E1E2F")

# Make the window resizable
compiler_phases_screen.pack_propagate(False)

# Use a PanedWindow to split left (input) and right (analysis)
phases_pane = tk.PanedWindow(compiler_phases_screen, orient=tk.HORIZONTAL, sashwidth=5, bg="#1E1E2F")
phases_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left: Code Input with its own scrollbar
input_frame = tk.LabelFrame(
    phases_pane,
    text="📝 Input Code",
    font=("Segoe UI", 12, "bold"),
    bg="#292A3E",
    fg="#FFC107",
    bd=2,
    relief="ridge"
)
input_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

input_scroll = tk.Scrollbar(input_frame, orient="vertical", width=18)
code_input = tk.Text(
    input_frame,
    height=20,
    font=("Consolas", 12),
    bg="#2E2E2E",
    fg="white",
    insertbackground="white",
    wrap=tk.NONE,
    yscrollcommand=input_scroll.set
)
input_scroll.config(command=code_input.yview)
input_scroll.pack(side="right", fill="y")
code_input.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=10)

phases_pane.add(input_frame, stretch="always")

# Right: Scrollable Analysis Area
right_frame = tk.Frame(phases_pane, bg="#1E1E2F")
phases_pane.add(right_frame, stretch="always")

# Add a canvas and scrollbar for the analysis area
analysis_canvas = tk.Canvas(right_frame, bg="#1E1E2F", highlightthickness=0)
analysis_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=analysis_canvas.yview, width=18)
analysis_canvas.configure(yscrollcommand=analysis_scrollbar.set)
analysis_scrollbar.pack(side="right", fill="y")
analysis_canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas for analysis boxes
analysis_inner = tk.Frame(analysis_canvas, bg="#1E1E2F")
analysis_canvas.create_window((0, 0), window=analysis_inner, anchor="nw")

# Update scrollregion when content changes
analysis_inner.bind(
    "<Configure>", lambda e: analysis_canvas.configure(scrollregion=analysis_canvas.bbox("all")))

# Analysis boxes with their own scrollbars
analysis_boxes = {}
for phase_name in [
    "Lexical Analysis",
    "Syntax & AST Analysis",
    "Semantic Analysis",
    "Intermediate Code Generation",
    "Code Optimization",
    "Code Generation"
]:
    frame = tk.LabelFrame(
        analysis_inner,
        text=f"🔹 {phase_name}",
        font=("Segoe UI", 12, "bold"),
        bg="#292A3E",
        fg="#FFC107",
        bd=2,
        relief="ridge"
    )
    frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Add a vertical scrollbar to each analysis box
    box_scroll = tk.Scrollbar(frame, orient="vertical", width=18)
    text_widget = tk.Text(
        frame,
        height=10,
        font=("Consolas", 11),
        bg="#2E2E2E",
        fg="white",
        wrap=tk.WORD,
        yscrollcommand=box_scroll.set
    )
    box_scroll.config(command=text_widget.yview)
    box_scroll.pack(side="right", fill="y")
    text_widget.pack(side="left", fill="both", expand=True, padx=0, pady=0)
    text_widget.config(state=tk.DISABLED)

    analysis_boxes[phase_name] = text_widget

# Update phase_sections to use the new analysis_boxes
phase_sections = {k: {"text": v} for k, v in analysis_boxes.items()}

# Add analyze and back buttons below the pane, always visible
button_frame = tk.Frame(compiler_phases_screen, bg="#1E1E2F")
button_frame.pack(fill=tk.X, pady=(0, 10))

analyze_button = tk.Button(
    button_frame,
    text="🔍 Analyze",
    font=("Segoe UI", 12, "bold"),
    bg="#1976D2",
    fg="white",
    command=lambda: analyze_phases(),
    cursor="hand2"
)
analyze_button.pack(side="left", padx=20)

back_button = tk.Button(
    button_frame,
    text="🔙 Back",
    font=("Segoe UI", 12, "bold"),
    bg="#1976D2",
    fg="white",
    command=back_to_welcome,
    cursor="hand2"
)
back_button.pack(side="right", padx=20)

root.mainloop()

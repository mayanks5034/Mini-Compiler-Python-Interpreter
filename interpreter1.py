from ast_nodes1 import ( 
    Number, Identifier, BinaryOp, UnaryOp, Assign, Boolean, Print, IfElse, WhileLoop, 
    FunctionDef, FunctionCall, Return, String, ForLoop, IndexNode, ListNode, TryExcept
)

class Interpreter:
    def __init__(self):
        self.variables = {}  # Stores variable values
        self.functions = {}  # Stores function definitions
    
    def interpret(self, statements):
        """Interprets the AST nodes (list of statements)."""
        result = None  
        for stmt in statements:
            if isinstance(stmt, Assign):
                self.variables[stmt.name] = self.evaluate(stmt.expr)
            elif isinstance(stmt, Print):
                self.evaluate(stmt.expr)
            elif isinstance(stmt, IfElse):
                self.execute_if_else(stmt)
            elif isinstance(stmt, WhileLoop):
                self.execute_while(stmt)
            elif isinstance(stmt, ForLoop):
                self.execute_for_loop(stmt)
            elif isinstance(stmt, FunctionDef):
                self.functions[stmt.name] = stmt  
            elif isinstance(stmt, FunctionCall):
                result = self.execute_function(stmt)
            elif isinstance(stmt, Return):
                return self.evaluate(stmt.value)  
            elif isinstance(stmt, TryExcept):  # ✅ Handling Try-Except
                self.execute_try_except(stmt)
        return result

    def evaluate(self, node):
        """Evaluates expressions"""
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, Boolean):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Identifier):
            return self.variables.get(node.name, None)

        elif isinstance(node, UnaryOp):  
            operand = self.evaluate(node.expr)  
            if node.op == 'not':
                return not bool(operand)  
            elif node.op == '-':
                return -operand  
            elif node.op == '+':
                return +operand  

        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == '+':
                return left + right if isinstance(left, (int, float)) else str(left) + str(right)
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                return left / right if right != 0 else float('inf')
            elif node.op == '%':
                return left % right
            elif node.op == 'and':
                return bool(left and right)
            elif node.op == 'or':
                return bool(left or right)
            elif node.op == '>':
                return left > right
            elif node.op == '<':
                return left < right
            elif node.op == '>=':
                return left >= right
            elif node.op == '<=':
                return left <= right
            elif node.op == '==':
                return left == right
            elif node.op == '!=':
                return left != right
        
        elif isinstance(node, ListNode):
            return [self.evaluate(item) for item in node.elements]

        elif isinstance(node, IndexNode):
            list_obj = self.evaluate(node.list_expr)
            index = self.evaluate(node.index_expr)
            if isinstance(list_obj, list) and isinstance(index, int):
                return list_obj[index]
            else:
                print(f"Error: Invalid index '{index}' for list {list_obj}")
                return None

        elif isinstance(node, FunctionCall):
            if node.name == "len":  # ✅ Handling `len()`
                return self.execute_len(node)
            elif isinstance(node.name, Identifier):  # Function calls
                return self.execute_function(node)

        elif isinstance(node, list):
            return [self.evaluate(item) for item in node]
        
        return None

    def execute_len(self, function_call):
        """Executes built-in function len()"""
        if len(function_call.arguments) != 1:
            print(f"Error: 'len' function expects 1 argument, got {len(function_call.arguments)}")
            return None

        obj = self.evaluate(function_call.arguments[0])
        if isinstance(obj, (list, str)):
            return len(obj)
        else:
            print(f"Error: 'len' function cannot be used on type {type(obj).__name__}")
            return None

    def execute_try_except(self, try_except_node):
        """Executes try-except blocks"""
        try:
            self.interpret(try_except_node.try_body)
        except Exception as e:
            print(f"Exception Caught: {e}")
            self.interpret(try_except_node.except_body)

    def execute_if_else(self, if_else_node):
        """Executes if-else statements"""
        condition_result = self.evaluate(if_else_node.condition)
        if condition_result:
            self.interpret(if_else_node.if_body)
        else:
            self.interpret(if_else_node.else_body)

    def execute_while(self, while_node):
        """Executes while loops"""
        while self.evaluate(while_node.condition):
            self.interpret(while_node.body)

    def execute_for_loop(self, for_node):
        """Executes for loops"""
        iterable = self.evaluate(for_node.iterable)

        if isinstance(for_node.iterable, FunctionCall) and for_node.iterable.name == "range":
            if len(for_node.iterable.arguments) != 1:
                print(f"Error: 'range' function expects 1 argument, got {len(for_node.iterable.arguments)}")
                return
            evaluated_arg = self.evaluate(for_node.iterable.arguments[0])
            if not isinstance(evaluated_arg, int):
                print(f"Error: 'range' function expects an integer argument, got {evaluated_arg}")
                return
            iterable = range(evaluated_arg)  

        if iterable is None:
            print(f"Error: Loop iterable '{for_node.iterable}' is None.")
            return  

        if not isinstance(iterable, (list, range, str)):  
            print(f"Error: '{iterable}' is not iterable")
            return

        prev_value = self.variables.get(for_node.variable, None)

        for value in iterable:
            self.variables[for_node.variable] = value  
            self.interpret(for_node.body)  

        if prev_value is not None:
            self.variables[for_node.variable] = prev_value
        else:
            del self.variables[for_node.variable]  

    def execute_function(self, function_call):
        """Executes function calls"""
        func_def = self.functions.get(function_call.name)
        if not func_def:
            print(f"Error: Function '{function_call.name}' is not defined")
            return None

        if len(func_def.parameters) != len(function_call.arguments):
            print(f"Error: Function '{function_call.name}' expects {len(func_def.parameters)} arguments, but got {len(function_call.arguments)}")
            return None

        local_scope = {param: self.evaluate(arg) for param, arg in zip(func_def.parameters, function_call.arguments)}
        previous_scope = self.variables.copy()  
        self.variables.update(local_scope)

        return_value = None
        for stmt in func_def.body:
            return_value = self.interpret([stmt])
            if return_value is not None:  
                break

        self.variables = previous_scope  
        return return_value

    def execute(self, code):
        try:
            self.interpret(code)
        except Exception as e:
            print(f"Runtime Error: {e}")


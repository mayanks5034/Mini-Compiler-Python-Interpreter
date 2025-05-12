class Number:
    def __init__(self, value):
        self.value = value

    def evaluate(self, context):
        return self.value

    def __str__(self):
        return f"Number({self.value})"

class String:
    def __init__(self, value):
        self.value = value

    def evaluate(self, context):
        return self.value

    def __str__(self):
        return f"String({self.value})"

class Boolean:
    def __init__(self, value):
        self.value = value

    def evaluate(self, context):
        return self.value

    def __str__(self):
        return f"Boolean({self.value})"

class Identifier:
    def __init__(self, name):
        self.name = name

    def evaluate(self, symbol_table):
        if self.name in symbol_table:
            return symbol_table[self.name]  # ✅ Fetch stored value
        else:
            raise Exception(f"❌ Error: Variable '{self.name}' is not defined")

    def __str__(self):
        return f"Identifier({self.name})"

class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr  # Store the expression for assignment

    def evaluate(self, symbol_table):
        # Store the result of the expression in the symbol table
        value = self.expr.evaluate(symbol_table)
        symbol_table[self.name] = value  # Assign the evaluated value to the symbol table
        return value

    def __str__(self):
        return f"Assign({self.name} = {self.expr})"

class ListNode:
    def __init__(self, elements):
        self.elements = elements

    def evaluate(self, env):
        return [elem.evaluate(env) for elem in self.elements]

    def __str__(self):
        return f"ListNode({self.elements})"

class IndexNode:
    def __init__(self, list_expr, index_expr):
        self.list_expr = list_expr
        self.index_expr = index_expr

    def evaluate(self, env):
        lst = self.list_expr.evaluate(env)
        index = self.index_expr.evaluate(env)
        if not isinstance(lst, list):
            raise Exception("❌ Error: Cannot index a non-list object")
        return lst[index]

    def __str__(self):
        return f"IndexNode({self.list_expr}[{self.index_expr}])"

class ListAssign:
    def __init__(self, list_expr, index_expr, value):
        self.list_expr = list_expr
        self.index_expr = index_expr
        self.value = value

    def evaluate(self, env):
        lst = self.list_expr.evaluate(env)
        index = self.index_expr.evaluate(env)
        val = self.value.evaluate(env)

        if not isinstance(lst, list):
            raise Exception("❌ Error: Cannot index a non-list object")
        lst[index] = val

    def __str__(self):
        return f"ListAssign({self.list_expr}[{self.index_expr}] = {self.value})"

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, env):
        left_val = self.left.evaluate(env)
        right_val = self.right.evaluate(env)

        if self.op == '+':
            return left_val + right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '/':
            if right_val == 0:
                raise Exception("❌ Error: Division by zero")
            return left_val / right_val
        elif self.op == '%':
            return left_val % right_val
        elif self.op == '==':
            return left_val == right_val
        elif self.op == '!=':
            return left_val != right_val
        elif self.op == '>':
            return left_val > right_val
        elif self.op == '<':
            return left_val < right_val
        elif self.op == '>=':
            return left_val >= right_val
        elif self.op == '<=':
            return left_val <= right_val
        elif self.op == 'and':
            return left_val and right_val
        elif self.op == 'or':
            return left_val or right_val
        else:
            raise Exception(f"Unknown operator: {self.op}")

    def __str__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, env):
        value = self.expr.evaluate(env)

        if self.op == '-':
            return -value
        elif self.op == 'not':
            return not value
        else:
            raise Exception(f"Unknown unary operator: {self.op}")

    def __str__(self):
        return f"UnaryOp({self.op} {self.expr})"

class Print:
    def __init__(self, expr):
        self.expr = expr  # The expression to evaluate

    def evaluate(self, context):
        # Evaluate the expression and print the result
        result = self.expr.evaluate(context)
        print(f"Evaluating Print: {result}")
        print(result)

    def __str__(self):
        return f"Print({self.expr})"

class IfElse:
    def __init__(self, condition, if_body, else_body):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

    def evaluate(self, env):
        if self.condition.evaluate(env):
            for stmt in self.if_body:
                stmt.evaluate(env)
        elif self.else_body:
            for stmt in self.else_body:
                stmt.evaluate(env)

    def __str__(self):
        return f"IfElse({self.condition}, {self.if_body}, {self.else_body})"

class WhileLoop:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def evaluate(self, env):
        while self.condition.evaluate(env):
            for stmt in self.body:
                stmt.evaluate(env)

    def __str__(self):
        return f"WhileLoop({self.condition}, {self.body})"

class ForLoop:
    def __init__(self, var, iterable, body):
        self.var = var
        self.iterable = iterable
        self.body = body

    def evaluate(self, env):
        iterable_value = self.iterable.evaluate(env)
        for val in iterable_value:
            env[self.var] = val
            for stmt in self.body:
                stmt.evaluate(env)

    def __str__(self):
        return f"ForLoop(var={self.var}, iterable={self.iterable}, body={self.body})"

class FunctionDef:
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def evaluate(self, env):
        env[self.name] = self

    def __str__(self):
        return f"FunctionDef({self.name}, {self.parameters}, {self.body})"


class FunctionCall:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def evaluate(self, env):
        function_def = env.get(self.name)
        if not function_def:
            raise Exception(f"Function '{self.name}' is not defined")

        local_env = env.copy()
        for param, arg in zip(function_def.parameters, self.arguments):
            local_env[param] = arg.evaluate(env)

        for stmt in function_def.body:
            if isinstance(stmt, Return):
                return stmt.value.evaluate(local_env)
            stmt.evaluate(local_env)

    def __str__(self):
        return f"FunctionCall({self.name}, {self.arguments})"

class Return:
    def __init__(self, value):
        self.value = value

    def evaluate(self, context):
        return self.value.evaluate(context)

    def __str__(self):
        return f"Return({self.value})"

class LenFunction:
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, env):
        return len(self.expr.evaluate(env))

    def __str__(self):
        return f"LenFunction({self.expr})"

class TryExcept:
    def __init__(self, try_block, except_block):
        self.try_block = try_block  # List of statements inside try
        self.except_block = except_block  # List of statements inside except

    def evaluate(self, context):
        try:
            for stmt in self.try_block:
                stmt.evaluate(context)
        except Exception as e:
            print(f"Exception caught: {e}")
            for stmt in self.except_block:
                stmt.evaluate(context)

class StringMethod:
    def __init__(self, string_obj, method, args=None):
        self.string_obj = string_obj  # The string on which the method is called
        self.method = method  # Method name (upper, lower, etc.)
        self.args = args if args else []  # Optional arguments (for replace())

    def evaluate(self, context):
        string_value = self.string_obj.evaluate(context)  # Evaluate string expression
        if self.method == "upper":
            return string_value.upper()
        elif self.method == "lower":
            return string_value.lower()
        elif self.method == "strip":
            return string_value.strip()
        elif self.method == "replace":
            if len(self.args) == 2:
                return string_value.replace(self.args[0].evaluate(context), self.args[1].evaluate(context))
        return None

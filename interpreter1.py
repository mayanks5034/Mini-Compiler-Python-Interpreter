from ast_nodes import *

class Interpreter:
    """Interpreter for the custom AST."""
    def __init__(self):
        self.environment = {}
        self.functions = {}
        self.return_value = None
        self.in_loop = False
        self.break_loop = False
        self.continue_loop = False

    def evaluate(self, node):
        """Evaluate an AST node."""
        if isinstance(node, list):
            return [self.evaluate(item) for item in node]
        if node is None:
            return None
        method_name = f'evaluate_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_evaluate)
        return method(node)

    def generic_evaluate(self, node):
        raise Exception(f'No evaluate_{node.__class__.__name__} method')

    def evaluate_Number(self, node):
        return node.value

    def evaluate_String(self, node):
        return node.value

    def evaluate_Boolean(self, node):
        return node.value

    def evaluate_Identifier(self, node):
        if node.name in self.environment:
            return self.environment[node.name]
        elif node.name in self.functions:
            return self.functions[node.name]
        raise Exception(f"Undefined variable or function: {node.name}")

    def evaluate_BinaryOp(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            if right == 0:
                raise Exception("Division by zero")
            return left / right
        elif node.op == '%':
            if right == 0:
                raise Exception("Modulo by zero")
            return left % right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            return left < right
        elif node.op == '>':
            return left > right
        elif node.op == '<=':
            return left <= right
        elif node.op == '>=':
            return left >= right
        elif node.op == 'and':
            return left and right
        elif node.op == 'or':
            return left or right
        else:
            raise Exception(f"Unknown operator: {node.op}")

    def evaluate_UnaryOp(self, node):
        expr = self.evaluate(node.expr)
        if node.op == '-':
            return -expr
        elif node.op == 'not':
            return not expr
        else:
            raise Exception(f"Unknown unary operator: {node.op}")

    def evaluate_Assign(self, node):
        value = self.evaluate(node.value)
        self.environment[node.name.name] = value
        return value

    def evaluate_Print(self, node):
        value = self.evaluate(node.expr)
        print(value)
        return value

    def evaluate_IfElse(self, node):
        condition = self.evaluate(node.condition)
        if condition:
            return self.evaluate(node.if_body)
        elif node.else_body:
            return self.evaluate(node.else_body)
        return None

    def evaluate_WhileLoop(self, node):
        self.in_loop = True
        result = None
        while self.evaluate(node.condition):
            if self.break_loop:
                self.break_loop = False
                break
            if self.continue_loop:
                self.continue_loop = False
                continue
            result = self.evaluate(node.body)
        self.in_loop = False
        return result

    def evaluate_ForLoop(self, node):
        self.in_loop = True
        result = None
        iterable = self.evaluate(node.iterable)
        if isinstance(iterable, range):
            for i in iterable:
                if self.break_loop:
                    self.break_loop = False
                    break
                if self.continue_loop:
                    self.continue_loop = False
                    continue
                self.environment[node.var.name] = i
                result = self.evaluate(node.body)
        elif isinstance(iterable, (list, tuple)):
            for item in iterable:
                if self.break_loop:
                    self.break_loop = False
                    break
                if self.continue_loop:
                    self.continue_loop = False
                    continue
                self.environment[node.var.name] = item
                result = self.evaluate(node.body)
        else:
            raise Exception(f"Cannot iterate over {type(iterable)}")
        self.in_loop = False
        return result

    def evaluate_FunctionDef(self, node):
        self.functions[node.name] = node
        return None

    def evaluate_FunctionCall(self, node):
        if node.name not in self.functions:
            raise Exception(f"Undefined function: {node.name}")
        func = self.functions[node.name]
        if not isinstance(func, FunctionDef):
            raise Exception(f"{node.name} is not a function")
        old_env = self.environment.copy()
        self.environment = {}
        args = [self.evaluate(arg) for arg in node.args]
        for param, arg in zip(func.params, args):
            self.environment[param.name] = arg
        result = self.evaluate(func.body)
        self.environment = old_env
        return result

    def evaluate_Return(self, node):
        self.return_value = self.evaluate(node.expr)
        return self.return_value

    def evaluate_Break(self, node):
        if not self.in_loop:
            raise Exception("Break statement outside loop")
        self.break_loop = True
        return None

    def evaluate_Continue(self, node):
        if not self.in_loop:
            raise Exception("Continue statement outside loop")
        self.continue_loop = True
        return None

    def evaluate_ListNode(self, node):
        return [self.evaluate(elem) for elem in node.elements]

    def evaluate_IndexNode(self, node):
        lst = self.evaluate(node.expr)
        idx = self.evaluate(node.index)
        if not isinstance(lst, (list, tuple, str)):
            raise Exception(f"Cannot index {type(lst)}")
        if not isinstance(idx, int):
            raise Exception("Index must be an integer")
        if idx < 0 or idx >= len(lst):
            raise Exception("Index out of range")
        return lst[idx]

    def evaluate_TryExcept(self, node):
        try:
            return self.evaluate(node.try_body)
        except Exception:
            return self.evaluate(node.except_body)

    def evaluate_LenFunction(self, node):
        expr = self.evaluate(node.expr)
        if not isinstance(expr, (list, tuple, str)):
            raise Exception(f"Cannot get length of {type(expr)}")
        return len(expr)

    def evaluate_StringMethod(self, node):
        string_obj = self.evaluate(node.string_obj)
        if not isinstance(string_obj, str):
            raise Exception(f"Cannot call string method on {type(string_obj)}")
        args = [self.evaluate(arg) for arg in node.args]
        if node.method == 'upper':
            return string_obj.upper()
        elif node.method == 'lower':
            return string_obj.lower()
        elif node.method == 'strip':
            return string_obj.strip()
        elif node.method == 'replace' and len(args) == 2:
            return string_obj.replace(args[0], args[1])
        else:
            raise Exception(f"Unknown string method: {node.method}")

    def evaluate_RangeCall(self, node):
        start = self.evaluate(node.start) if node.start is not None else 0
        stop = self.evaluate(node.stop) if node.stop is not None else None
        step = self.evaluate(node.step) if node.step is not None else 1
        if not all(isinstance(x, int) for x in [start, stop, step] if x is not None):
            raise Exception("Range arguments must be integers")
        return range(start, stop, step)

    def interpret(self, statements):
        """Interpret a list of statements."""
        result = None
        for statement in statements:
            result = self.evaluate(statement)
            if self.return_value is not None:
                return self.return_value
        return result

    def execute(self, code):
        """Execute code by parsing and interpreting it."""
        from myparser import parser
        ast = parser.parse(code)
        if ast is None:
            raise Exception("Failed to parse code")
        return self.interpret(ast)

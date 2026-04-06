import ast
import os

class FuncVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = {}
        self.current_func = None

    def visit_FunctionDef(self, node):
        self.current_func = node.name
        if node.name not in self.calls:
            self.calls[node.name] = []
        self.generic_visit(node)
        self.current_func = None

    def visit_Call(self, node):
        name = None

        if hasattr(node.func, "id"):
            name = node.func.id
        elif hasattr(node.func, "attr"):
            name = node.func.attr

        if name and self.current_func:
            self.calls[self.current_func].append(name)

        self.generic_visit(node)


def build_function_graph(root="."):
    graph = {}

    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".py"):
                continue

            path = os.path.join(dirpath, f)

            try:
                code = open(path, "r", encoding="utf-8").read()
            except:
                continue

            try:
                tree = ast.parse(code)
            except:
                continue

            v = FuncVisitor()
            v.visit(tree)

            graph[path] = v.calls

    return graph

import ast
import os
from core.import_map import build_import_map
from core.resolver import resolve_call

class Visitor(ast.NodeVisitor):
    def __init__(self, import_map):
        self.import_map = import_map
        self.func = None
        self.calls = {}

    def visit_FunctionDef(self, node):
        self.func = node.name
        self.calls.setdefault(self.func, [])
        self.generic_visit(node)
        self.func = None

    def visit_Call(self, node):
        if not self.func:
            return

        name = None

        if hasattr(node.func, "id"):
            name = node.func.id
        elif hasattr(node.func, "attr"):
            name = node.func.attr

        if name:
            resolved = resolve_call(name, self.import_map)
            self.calls[self.func].append(resolved)

        self.generic_visit(node)


def build_function_graph(root="."):
    import_map = build_import_map(root)
    graph = {}

    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".py"):
                continue

            path = os.path.join(dirpath, f)

            try:
                code = open(path, "r", encoding="utf-8").read()
                tree = ast.parse(code)
            except:
                continue

            v = Visitor(import_map)
            v.visit(tree)

            graph[path] = v.calls

    return graph

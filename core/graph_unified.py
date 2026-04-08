import ast
import os


class CallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        name = None

        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr

        if name:
            self.calls.append(name)

        self.generic_visit(node)


def extract_calls(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    graph = {}

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            visitor = CallVisitor()
            visitor.visit(node)
            graph[node.name] = {
                "type": "function",
                "calls": visitor.calls
            }

    return graph


def build_unified_graph(target="."):
    result = {}

    for root, _, files in os.walk(target):
        for f in files:
            if not f.endswith(".py"):
                continue

            path = os.path.join(root, f)

            try:
                funcs = extract_calls(path)

                result[path] = {
                    "type": "file",
                    "calls": list(funcs.keys())
                }

                result.update(funcs)

            except Exception:
                pass

    return result

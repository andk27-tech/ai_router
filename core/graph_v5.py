import os, ast
from collections import defaultdict

class Visitor(ast.NodeVisitor):
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

def build_function_graph(root="."):
    graph = {}

    for dirpath, _, files in os.walk(root):
        if "venv" in dirpath:
            continue

        for f in files:
            if not f.endswith(".py"):
                continue

            path = os.path.join(dirpath, f)

            try:
                code = open(path, "r", encoding="utf-8").read()
                tree = ast.parse(code)
            except:
                continue

            v = Visitor()
            v.visit(tree)

            graph[path] = {
                "calls": v.calls
            }

    return graph


def build_execution_dag():
    raw = build_function_graph()
    edges = defaultdict(set)

    for file, data in raw.items():
        for c in data["calls"]:
            edges[file].add(f"{file}:{c}")

    return {k: list(v) for k, v in edges.items()}

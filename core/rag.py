import os
import ast

IGNORE_DIRS = {
    "venv",
    ".venv",
    "__pycache__",
    "site-packages",
}

def search(query: str):
    return {"query": query, "result": []}


def build_full_graph():
    graph = {}

    root = os.getcwd()

    for dirpath, dirnames, filenames in os.walk(root):

        # 🚫 디렉토리 필터링
        dirnames[:] = [
            d for d in dirnames
            if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        for f in filenames:
            if not f.endswith(".py"):
                continue

            path = os.path.join(dirpath, f)

            try:
                with open(path, "r", encoding="utf-8") as fp:
                    code = fp.read()
            except:
                continue

            graph[path] = extract_api_flow(code)

    return graph


def extract_api_flow(code: str):
    class V(ast.NodeVisitor):
        def __init__(self):
            self.calls = []

        def visit_Call(self, node):
            if hasattr(node.func, "id"):
                self.calls.append(node.func.id)
            elif hasattr(node.func, "attr"):
                self.calls.append(node.func.attr)
            self.generic_visit(node)

    try:
        tree = ast.parse(code)
    except:
        return []

    v = V()
    v.visit(tree)

    return list(set(v.calls))

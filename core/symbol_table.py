import os
import ast

def build_symbol_table(root="."):
    table = {}

    for dirpath, _, files in os.walk(root):

        # 🔥 핵심: venv 제거
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

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    table[node.name] = f"{path}:{node.name}"

    return table

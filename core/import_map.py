import ast
import os

def build_import_map(root="."):
    imap = {}

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

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        for n in node.names:
                            imap[n.name] = f"{node.module}.{n.name}"

                if isinstance(node, ast.Import):
                    for n in node.names:
                        imap[n.name] = n.name

    return imap

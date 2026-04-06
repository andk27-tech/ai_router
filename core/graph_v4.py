import ast
import os
from core.import_map import build_import_map
from core.resolver import resolve_call


class Visitor(ast.NodeVisitor):
    def __init__(self, import_map):
        self.import_map = import_map

        self.current_func = None

        self.module_calls = []
        self.function_calls = {}
        self.decorators = {}

    # -------------------------
    # MODULE LEVEL CALLS
    # -------------------------
    def visit_Expr(self, node):
        # standalone expression (FastAPI(), get(), etc)
        if isinstance(node.value, ast.Call):
            self._handle_call(node.value)
        self.generic_visit(node)

    def visit_Call(self, node):
        # inside function or module
        self._handle_call(node)
        self.generic_visit(node)

    # -------------------------
    # FUNCTION SCOPE
    # -------------------------
    def visit_FunctionDef(self, node):
        self.current_func = node.name
        self.function_calls.setdefault(node.name, [])

        # decorators
        for d in node.decorator_list:
            name = self._get_name(d)
            if name:
                self.decorators.setdefault(node.name, []).append(name)

        self.generic_visit(node)
        self.current_func = None

    # -------------------------
    # CORE CALL HANDLER
    # -------------------------
    def _handle_call(self, node):
        name = self._get_name(node.func)
        if not name:
            return

        resolved = resolve_call(name, self.import_map)

        # function scope
        if self.current_func:
            self.function_calls[self.current_func].append(resolved)
        else:
            # module scope
            self.module_calls.append(resolved)

    # -------------------------
    # NAME RESOLUTION
    # -------------------------
    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None


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

            graph[path] = {
                "module_calls": v.module_calls,
                "function_calls": v.function_calls,
                "decorators": v.decorators
            }

    return graph

import ast

def build_call_graph(code: str):
    tree = ast.parse(code)

    calls = []

    class V(ast.NodeVisitor):
        def visit_Call(self, node):
            if hasattr(node.func, "id"):
                calls.append(node.func.id)
            elif hasattr(node.func, "attr"):
                calls.append(node.func.attr)
            self.generic_visit(node)

    V().visit(tree)
    return calls

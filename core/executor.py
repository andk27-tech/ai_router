import importlib

def resolve_and_run(node, context=None):
    try:
        module_path, func_name = node.rsplit(".", 1)

        module = importlib.import_module(module_path)
        func = getattr(module, func_name)

        if context is None:
            context = {}

        return func(**context)

    except Exception as e:
        return f"[ERROR] {node}: {e}"

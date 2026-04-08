from core.symbol_table import build_symbol_table

def resolve_graph(graph):
    table = build_symbol_table()
    resolved = {}

    for k, v in graph.items():
        resolved[k] = []

        for node in v:
            name = node.split(":")[-1]

            if name in table:
                resolved[k].append(table[name])
            else:
                resolved[k].append(node)

    return resolved

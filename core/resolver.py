def build_symbol_table(graph):
    table = {}
    for k in graph:
        if ":" in k:
            _, func = k.split(":")
            table[func] = k
    return table

def resolve_graph(graph):
    table = build_symbol_table(graph)
    out = {}
    for k, v in graph.items():
        new = []
        for n in v:
            name = n.split(":")[-1].split(".")[-1]
            new.append(table.get(name, n))
        out[k] = new
    return out

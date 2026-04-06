from core.score import score_node

def rank_graph(graph):
    ranked = {}

    for k, v in graph.items():
        items = [(node, score_node(node)) for node in v]
        items.sort(key=lambda x: x[1], reverse=True)

        ranked[k] = [x[0] for x in items]

    return ranked

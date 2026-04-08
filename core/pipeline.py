def run_node(name, inputs):
    """
    mock execution engine
    """
    if not inputs:
        return f"{name}:ROOT"

    return f"{name}:({','.join(inputs)})"


def run_pipeline(graph, order):
    results = {}

    for node in order:
        deps = graph.get(node, [])

        input_data = []
        for d in deps:
            input_data.append(results[d])

        results[node] = run_node(node, input_data)

    return results

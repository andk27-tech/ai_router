def run_node(node, graph):
    deps = graph.get(node, [])

    input_data = ''
    for d in deps:
        input_data += str(d) + ' '

    if not input_data.strip():
        input_data = node

    return f'processed({node} <- {input_data})'


def run_node_safe(node):
    return run_node(node, {})

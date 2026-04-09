from core.node import run_node
from core.evaluator import score_output

def run_graph(graph, input_data: str):
    current = input_data

    for node in graph:
        output = run_node(node, current)
        score = score_output(output)

        print(f"[{node['id']}] OUTPUT:\n{output}\nSCORE:{score}\n")

        current = output

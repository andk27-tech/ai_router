from core.graph_v5 import build_execution_dag
from core.graph_clean import clean_graph


class GraphRouter:
    def __init__(self):
        raw = build_execution_dag()
        self.graph = clean_graph(raw)

    def run(self, start):
        visited = set()
        result = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)

            result.append(node)

            for nxt in self.graph.get(node, []):
                dfs(nxt)

        dfs(start)
        return result

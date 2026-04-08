def build_entry_graph(graph, entry="./main.py"):
    # 디버그: 실제 키 확인
    print("DEBUG ENTRY SEARCH:", list(graph.keys())[:5])

    # 1. entry 자동 탐색 (무조건 성공하게)
    real_entry = None
    for k in graph.keys():
        if "main.py" in k:
            real_entry = k
            break

    if not real_entry:
        return {}

    visited = set()
    result = {}

    def dfs(node):
        if node in visited:
            return
        visited.add(node)

        result[node] = graph.get(node, [])

        for nxt in graph.get(node, []):
            dfs(nxt)

    dfs(real_entry)
    return result

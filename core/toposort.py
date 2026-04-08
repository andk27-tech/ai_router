from collections import defaultdict, deque

def topological_sort(graph):
    indegree = defaultdict(int)

    for node in graph:
        indegree[node] = 0

    for node, deps in graph.items():
        for d in deps:
            indegree[node] += 1

    q = deque([n for n in graph if indegree[n] == 0])

    order = []

    while q:
        node = q.popleft()
        order.append(node)

        for nxt in graph:
            if node in graph[nxt]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)

    if len(order) != len(graph):
        raise Exception("Cycle detected")

    return order

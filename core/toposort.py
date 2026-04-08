from collections import defaultdict, deque

def topological_sort(graph):
    indegree = defaultdict(int)
    adj = defaultdict(list)

    nodes = set(graph.keys())

    # build adjacency + nodes
    for node, deps in graph.items():
        for d in deps:
            adj[d].append(node)
            indegree[node] += 1
            nodes.add(d)

    # init missing nodes
    for n in nodes:
        indegree[n] = indegree[n]

    q = deque([n for n in nodes if indegree[n] == 0])

    order = []

    while q:
        node = q.popleft()
        order.append(node)

        for nxt in adj[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)

    if len(order) != len(nodes):
        raise Exception("Cycle detected")

    return order

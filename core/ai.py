def ask_llm(payload: dict):
    graph = payload.get("call_graph", {})
    query = payload.get("input", "")
    context = payload.get("context", {})

    # 1. graph에서 관련 노드 추출 (아주 단순 버전)
    matched = []

    for k, v in graph.items():
        if isinstance(v, list):
            if any(query.lower() in str(x).lower() for x in v):
                matched.append({
                    "file": k,
                    "calls": v
                })

    # 2. fallback
    if not matched:
        matched = list(graph.items())[:5]

    return {
        "query": query,
        "matched_nodes": matched[:5],
        "graph_size": len(graph),
        "note": "router v1 active"
    }

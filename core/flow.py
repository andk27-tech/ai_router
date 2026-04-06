def build_flow(graph: dict):
    flow = []

    # main entry 찾기
    for file, calls in graph.items():
        if "main.py" in file:
            flow.append({
                "entry": file,
                "calls": calls
            })

    return flow

def clean_graph(graph):
    cleaned = {}

    for k, v in graph.items():

        # 최소 필터만 유지 (삭제 금지)
        if not k:
            continue

        cleaned[k] = []

        for item in v:

            if not item:
                continue

            cleaned[k].append(item)

    return cleaned

def clean_graph(graph):
    skip = {"json","FastAPI","list","dict","set","append","items","print","len","str"}

    cleaned = {}

    for k, v in graph.items():
        cleaned[k] = []

        for item in v:
            name = item.split(":")[-1]
            if name in skip:
                continue
            cleaned[k].append(item)

    return cleaned

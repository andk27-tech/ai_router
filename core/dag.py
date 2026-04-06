def build_dag(graph: dict):
    dag = {}

    for file, calls in graph.items():
        for c in calls:
            if c not in dag:
                dag[c] = []
            dag[c].append(file)

    return dag

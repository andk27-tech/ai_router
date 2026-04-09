def run_node(name, inputs):
    """
    mock execution engine
    """
    if not inputs:
        return f"{name}:ROOT"

    return f"{name}:({','.join(inputs)})"


def run_pipeline(graph, order):
    results = {}

    for node in order:
        deps = graph.get(node, [])

        input_data = []
        for d in deps:
            input_data.append(results[d])

        results[node] = run_node(node, input_data)

    return results

# --- retry policy integration ---
from policy.retry_policy import RetryPolicy

retry_policy = RetryPolicy()

def execute_node(node, state):
    result = node.run(state)

    score = result.get("score", 1.0)
    retry_count = result.get("retry_count", 0)

    node_result = {
        "score": score,
        "retry_count": retry_count
    }

    if retry_policy.should_retry(node_result):
        print(f"[RETRY] node={node.name}")
        node_result["retry_count"] += 1
        return node.run(state)

    return result

def resolve_graph(state):
    """
    최소 실행용 stub
    """
    return {
        "output": state.get("query", ""),
        "score": 0.5
    }

import time

def resolve_graph(graph):
    """
    최소 실행 엔진 (stub 버전)
    - graph 순회
    - trace 생성
    """

    trace = []

    start_time = time.time()

    for node, edges in graph.items():
        t_start = time.time()

        trace.append({
            "node": node,
            "event": "START",
            "t": t_start - start_time
        })

        # simulate execution
        time.sleep(0.01)

        trace.append({
            "node": node,
            "event": "END",
            "t": time.time() - start_time
        })

    return {
        "trace": trace,
        "graph": graph
    }

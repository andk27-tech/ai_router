from core.sample_graph import graph
from core.runner import run_graph

if __name__ == "__main__":
    input_text = "AI는 앞으로 모든 산업을 바꾼다. 자동화와 판단 시스템이 핵심이다."
    run_graph(graph, input_text)

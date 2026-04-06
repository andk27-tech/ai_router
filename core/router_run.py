from core.graph_v5 import build_execution_dag
from core.graph_clean import clean_graph
from core.router_rank import rank_graph

def main():
    g = build_execution_dag()
    g = clean_graph(g)
    g = rank_graph(g)
    print(g)

if __name__ == "__main__":
    main()

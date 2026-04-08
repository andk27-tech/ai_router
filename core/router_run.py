from core.graph_clean import clean_graph
from core.import_resolver import resolve_graph
from core.router_rank import rank_graph
from core.graph_v5 import build_execution_dag
from core.entry_filter import build_entry_graph

def main():
    g = build_execution_dag()
    g = clean_graph(g)
    g = resolve_graph(g)
    g = rank_graph(g)

    g = build_entry_graph(g, "main.py")

    print(g)

if __name__ == "__main__":
    main()

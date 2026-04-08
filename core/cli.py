import argparse
import json
from core.pipeline import resolve_graph


def print_trace_timeline(trace):
    nodes = sorted(list(set(t["node"] for t in trace)))

    start = {}
    end = {}

    for t in trace:
        if t["event"] == "START":
            start[t["node"]] = t["t"]
        elif t["event"] == "END":
            end[t["node"]] = t["t"]

    base = min(start.values())

    print("\n=== EXECUTION TIMELINE ===")

    for n in nodes:
        s = start.get(n, base)
        e = end.get(n, s + 0.0001)

        s_bar = int((s - base) * 10000)
        e_bar = int((e - base) * 10000)

        bar = " " * s_bar + "█" * max(1, e_bar - s_bar)

        print(f"{n:>3} | {bar}")

def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="cmd")

    graph = sub.add_parser("graph")
    graph.add_argument("--input", type=str, required=False)
    graph.add_argument("--json", type=str, default=None)
    graph.add_argument("--dot", type=str, default=None)

    args = parser.parse_args()

    if args.cmd == "graph":
        print("CLI LOADED")

        # input graph 로딩
        if args.input:
            with open(args.input, "r") as f:
                graph_data = json.load(f)
        else:
            graph_data = {
                "A": ["B", "C"],
                "B": ["C"],
                "C": []
            }

        result = resolve_graph(graph_data)
        print_trace_timeline(result.get("trace", []))

        # JSON export
        if args.json:
            with open(args.json, "w") as f:
                json.dump(result, f, indent=2)
            print(f"[OK] JSON saved -> {args.json}")

        # DOT export
        if args.dot:
            from core.cli import to_dot
            with open(args.dot, "w") as f:
                f.write(to_dot(graph_data))
            print(f"[OK] DOT saved -> {args.dot}")


def to_dot(graph):
    lines = ["digraph G {"]
    for k, v in graph.items():
        for node in v:
            lines.append(f'  "{k}" -> "{node}"')
    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()

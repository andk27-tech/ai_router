import sys
from core.graph_unified import build_unified_graph


def cmd_graph():
    g = build_unified_graph()

    print("\n=== GRAPH ===\n")

    for k, v in g.items():
        print(f"[{k}]")
        print(f"  type: {v.get('type')}")
        print(f"  calls: {v.get('calls')}")
        print()


def cmd_debug(target):
    g = build_unified_graph()

    if target not in g:
        print("not found:", target)
        return

    print(f"\n=== DEBUG: {target} ===\n")
    print(g[target])


def cmd_help():
    print("""
ai_router commands:

  graph        show full graph
  debug <x>    inspect node
  help         show help
""")


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    cmd = sys.argv[1]

    if cmd == "graph":
        cmd_graph()

    elif cmd == "debug":
        if len(sys.argv) < 3:
            print("usage: ai_router debug <target>")
            return
        cmd_debug(sys.argv[2])

    elif cmd == "help":
        cmd_help()

    else:
        print("unknown command:", cmd)
        cmd_help()

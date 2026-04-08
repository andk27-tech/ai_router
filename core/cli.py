print('CLI LOADED')
from core.pipeline import run
import sys
from core.graph_unified import build_unified_graph


def cmd_debug(target):
    g = run()

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




def cmd_graph():
    print('GRAPH CALLED')
    print("GRAPH HIT")
    g = run()
    print("RUN RESULT:", g)

    print("\n=== GRAPH ===\n")

    for k, v in (g or {}).items():
        print(f"[{k}]")
        for item in v:
            print("  ->", item)
        print()


if __name__ == '__main__':
    main()

def cmd_graph():
    from core.pipeline import run

    g = run()

    print("\n=== GRAPH ===\n")

    if not g:
        print("EMPTY GRAPH")
        return

    for k, v in g.items():
        print(f"[{k}]")
        for item in v:
            print("  ->", item)
        print()


def apply_patch():
    import core.cli as cli
    cli.cmd_graph = cmd_graph

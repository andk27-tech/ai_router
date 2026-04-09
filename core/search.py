from core.data import DATA

def search(keyword):
    results = []

    for text, score in DATA:
        if keyword.lower() in text.lower():
            results.append((text, score))

    return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용: python3 -m core.search <keyword>")
        exit()

    kw = sys.argv[1]
    res = search(kw)

    print(f"\n=== SEARCH: {kw} ===")
    for t, s in res:
        print(f"- {t} ({s})")

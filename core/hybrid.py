from core.data import DATA
from core.rule import quality_score

def relevance_score(text, keyword):
    text_low = text.lower()
    key_low = keyword.lower()

    if key_low not in text_low:
        return 0

    # 포함 횟수 + 위치 기반 점수
    count = text_low.count(key_low)
    position_bonus = 1 if text_low.startswith(key_low) else 0

    return count + position_bonus


def hybrid_search(keyword):
    results = []

    for text, score in DATA:
        rel = relevance_score(text, keyword)

        if rel > 0:
            final = quality_score(text, score) + rel
            results.append((text, final))

    ranked = sorted(results, key=lambda x: x[1], reverse=True)
    return ranked


if __name__ == "__main__":
    import sys

    kw = sys.argv[1]

    res = hybrid_search(kw)

    print(f"\n=== HYBRID SEARCH: {kw} ===")
    for t, s in res:
        print(f"- {t} ({s})")

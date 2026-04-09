from core.data import DATA
from core.rule import quality_score
from core.weight import keyword_bonus


def relevance_score(text, keyword):
    if not keyword:
        return 1

    t = text.lower()
    k = keyword.lower()

    if k not in t:
        return 0

    return t.count(k)


def get_feed(keyword=None):
    results = []

    for text, base in DATA:
        rel = relevance_score(text, keyword)

        # keyword 모드일 때 필터
        if keyword and rel == 0:
            continue

        base = quality_score(text, base)

        bonus = keyword_bonus(text)

        # 🔥 핵심 변경: penalty 먼저 반영된 base 기준으로 보너스 제한
        score = base + (bonus * 0.5) + rel

        results.append((text, score))

    return sorted(results, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    import sys

    kw = sys.argv[1] if len(sys.argv) > 1 else None

    feed = get_feed(kw)

    print(f"\n=== FEED: {kw if kw else 'ALL'} ===")
    for t, s in feed[:5]:
        print(f"- {t} ({s})")

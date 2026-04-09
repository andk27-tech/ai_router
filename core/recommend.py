from core.data import DATA
from core.rule import quality_score

def get_top(n=3):
    scored = []

    for t, s in DATA:
        final = quality_score(t, s)
        scored.append((t, final))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:n]

if __name__ == "__main__":
    print("\n=== TOP 추천 (필터 적용) ===")
    for i, (t, s) in enumerate(get_top()):
        print(f"{i+1}. {t} ({s})")

from core.memory import MEMORY

def score_policy(policy, recent):
    if not recent:
        return 0

    total = 0
    for m in recent:
        if policy == "expand":
            total += m["score"] + (2 if len(m["output"]) > 25 else 0)
        elif policy == "balance":
            total += m["score"]
        elif policy == "refine":
            total += m["score"] - 1
    return total / len(recent)

def generate_new_policy(recent):
    avg = sum(m["score"] for m in recent) / len(recent)

    # 🔥 핵심: 조건 기반 새 policy 생성
    if avg > 12:
        return "deep_expand"
    if avg > 9:
        return "adaptive_balance"
    return "tight_refine"

def evolve_policy():
    recent = MEMORY[-5:]

    base = ["refine", "balance", "expand"]

    # 🔥 기존 + 생성 policy 합치기
    dynamic = [generate_new_policy(recent)]

    candidates = list(set(base + dynamic))

    scored = {
        p: score_policy(p, recent)
        for p in candidates
    }

    return max(scored, key=scored.get)

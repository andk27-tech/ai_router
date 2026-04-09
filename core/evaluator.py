def evaluate(output, policy=None):
    text = output.lower()

    base = 5

    # 길이 보너스
    base += min(len(text) / 50, 3)

    # policy 가중치
    if policy == "expand":
        base += text.count("|") * 0.5
    elif policy == "balance":
        base += 1 if "균형" in text else 0
    elif policy == "refine":
        base += 1 if "정리" in text else 0

    # 안정화
    score = int(min(10, max(1, base)))

    return score, "policy-aware"

def evaluate(output):
    if not output:
        return 0, "empty"

    words = output.split()

    score = 0
    reason = []

    # 다양성
    unique = len(set(words))
    score += unique
    if unique < 3:
        reason.append("too repetitive")

    # 길이
    length = len(words)
    score += min(length, 10)
    if length < 3:
        reason.append("too short")

    # 반복 패널티
    max_repeat = max(words.count(w) for w in set(words))
    if max_repeat >= 3:
        score -= 10
        reason.append("heavy repetition")

    return score, ", ".join(reason) if reason else "ok"

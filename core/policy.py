WEIGHTS = {
    "refine": 1.0,
    "balance": 1.0,
    "expand": 1.0,
    "expand_deep": 1.2  # 더 깊은 확장 정책에 높은 가중치
}

def get_weight(policy):
    return WEIGHTS.get(policy, 1.0)

def update_weight(winner):
    for k in WEIGHTS:
        if k == winner:
            WEIGHTS[k] += 0.1
        else:
            WEIGHTS[k] -= 0.05

        WEIGHTS[k] = max(0.3, min(2.0, WEIGHTS[k]))
